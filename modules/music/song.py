from .sources import *
from typing import Optional, Tuple, Union, Dict

import aiohttp
import asyncio
import discord
import hashlib
import log
import os
import subprocess
import time
import youtube_dl

ytdl_session = youtube_dl.YoutubeDL({"format": "bestaudio", "noplaylist": True})

aiohttp_session = aiohttp.ClientSession()
hashid = lambda x: hashlib.sha256(x).hexdigest()[:8]
cache_location = "_cache/"


async def get_song_information(url: str) -> Dict[str, Union[str, float]]:
	"""
	Gets the song information from the source.
	
	:param url: Youtube (or other) video URL to pass in.
	:return: Data about the song that was discovered.
	"""
	data = None
	data = ytdl_session.extract_info(url, download=False)  # THIS BLOCKS. Todo: fix
	while data is None:
		await asyncio.sleep(0.1)
		
	available_formats = data.get("formats", [])
	available_formats = [x for x in available_formats if x.get("vcodec", "none") == "none"]
	try:
		best_media_url = sorted(available_formats, key=lambda x: x["abr"])[-1]["url"]
	except KeyError:
		best_media_url = url
	title = data.get("title", "[Unknown name]")
	length = data.get("duration", -1)
	return {"url": best_media_url,
			"title": title,
			"length": length}


def check_url_alive(url: str) -> bool:
	"""
	Checks if a Youtube link is still valid.
	
	:param url: Direct URL to check.
	:return: Whether the given URL is valid.
	"""
	if "googlevideo" not in url:  # YT is the only one that has temporary video
		return True  # direct URLs, so if it's not a youtube link it's going to be valid
	try:
		location = url.index("expire=")
	except ValueError:
		return False  # it didn't have an expire? either way getting a new url is a safe bet
	
	expiration_date = int(url[location+7:location+17])
	if expiration_date < time.time()+5:  # Don't use an expir(ed/ing) video
		return False
	else:
		return True


async def save_direct_url(url: str) -> str:
	filename = cache_location + hashid(url)
	async with await aiohttp_session.get(url) as response:
		with open(filename, "wb") as target_f:
			target_f.write(await response.read())
	return filename


class Song:
	"""
	Denotes a song and its corresponding AudioSource.
	"""
	locally_cached_file: str = None
	submitted_url: str = None
	media_url: str = None
	length: float = None
	name: str = None
	_AudioSourceObject: TrackingVolumeTransformer = EmptySource()

	def __init__(self, url: Optional[str] = None):
		"""
		Creates a new ``Song`` object representing a song and the associated
		AudioSource. This must be immediately followed by an asynchronous call
		to ``Song.load_info()``.
		
		``submitted_url: str``
			The URL that was given to create the song.
		
		``length: float``
			The length of the song, in seconds.
		
		``name: str``
			The title of the song.

		:param url: URL of the song.
		:raise FileNotFoundError: You created a Song out of a local file, but that file doesn't exist.
		"""
		if url is None:  # we must be from self.from_existing, so just exit
			return
		self.submitted_url = url
		if url.startswith("file://"):
			self.locally_cached_file = url.replace("file://", "")
			try:
				p = subprocess.run(["mediainfo", self.locally_cached_file], capture_output=True)
				stdout = p.stdout.decode()
				stdout = stdout.split("\n")
				len_parts = [x for x in stdout if x.startswith("Duration")][0]
				len_parts = len_parts.split(" ")  # we can split on spaces because for whatever reason the output of the command uses a million spaces to pad
				# [ ..., "8", "min", "24", "sec"]
				duration = int(len_parts[-4])*60 + int(len_parts[-2])
				self.length = duration
			except FileNotFoundError:
				if os.path.lexists(self.locally_cached_file):
					# we don't have Linux package `mediainfo`
					self.length = -1
				else:
					raise FileNotFoundError("Provided path does not exist.")
			except:
				log.warning(f"Error fetching information about song from file {self.locally_cached_file}")
				self.name = "[Error getting name]"
				self.length = -1
	
	async def load_info(self):
		"""Asynchronously get the song information (youtube_dl takes a bit...)"""
		song_info = await get_song_information(self.submitted_url)
		
		self.name = song_info["title"]
		self.length = song_info["length"]
		self.media_url = song_info["url"]

	@classmethod
	def from_existing(cls, media_url, length, name):
		"""
		Creates a new Song that we already know everything about (eg. for a
		local file, or for a song from a bot playlist).
		
		:param media_url: Direct location of the source. Opening this path should return the media itself.
		:param length: Length of the song.
		:param name: Name of the song.
		:return: The song that was created.
		:rtype: Song
		"""
		new = cls()
		new.submitted_url = media_url
		new.media_url = media_url
		new.length = length
		new.name = name
		return new

	async def cache(self):
		"""
		Downloads the specified YouTube video in anticipation of then playing it.
		
		:rtype: None
		"""
		if self.locally_cached_file is not None:
			return
		if check_url_alive(self.media_url):
			self.locally_cached_file = await save_direct_url(self.media_url)
		else:
			self.media_url = (await get_song_information(self.submitted_url))["url"]
			self.locally_cached_file = await save_direct_url(self.media_url)
	
	async def get_source(self) -> TrackingVolumeTransformer:
		"""
		Returns the AudioSource for the song. This should only be used by ``MusicInterface``.
		"""
		# This should really only be called once, if it is called several times you'll just reset the song I think?
		if self.locally_cached_file is None:
			
			asyncio.create_task(self.cache())  # If this line gives you an error, you are running a version before 3.7. Change this to asyncio.ensure_future() and it will work.
			# If you do change it to ensure_future instead of updating
			# to 3.7, be aware that some features of this bot may break.
			
			while self.locally_cached_file is None:
				await asyncio.sleep(0.01)
		self._AudioSourceObject = TrackingVolumeTransformer(discord.FFmpegPCMAudio(self.locally_cached_file, pipe=True))
		return self._AudioSourceObject
	
	@property
	def volume(self) -> float:
		return self._AudioSourceObject.volume
	
	@volume.setter
	def volume(self, new_vol: float):
		if new_vol < 0:
			new_vol = 0
		if new_vol > 2:
			new_vol = 2
		self._AudioSourceObject.volume = new_vol

	def progress(self) -> Tuple[float, float]:
		"""
		Returns the progress through this song in the form ``(current, length)``
		
		:return: Progress through the song.
		:rtype: Tuple[float, float]
		"""
		return getattr(self._AudioSourceObject, "progress", 0.0), self.length

	def to_embed(self, title: str, queue_pos: Optional[int] = None) -> discord.Embed:
		if queue_pos is None:
			if queue_pos == 0:
				embed = discord.Embed(title=title, description=f"Next On Deck", colour=0xbf35e3)
			else:
				embed = discord.Embed(title=title, description=f"In queue at position {queue_pos}", colour=0xbf35e3)
		else:
			embed = discord.Embed(title=title, description=discord.Embed.Empty, colour=0xbf35e3)
		embed = embed.add_field(name="Name", value=self.name)
		embed = embed.add_field(name="Duration", value=f"{self._AudioSourceObject.progress//60}m{self._AudioSourceObject.progress%60}s / {self.length//60}m{self.length%60}s")
		return embed
		
	def __del__(self):
		try:
			os.remove(self.locally_cached_file)
		except:
			log.error(f"Could not remove local song cache file {self.locally_cached_file}", include_exception=False)
