import time

from . import sources
from .exceptions import *
from .song import Song
from collections import defaultdict
from typing import Union, Callable, DefaultDict

import asyncio
import discord
import log


_active_ifaces: DefaultDict[discord.VoiceChannel, Union[None, "MusicInterface"]] = defaultdict(lambda: None)


class MusicInterface:
	"""
	A music interface that connects to a channel in a guild and lets you set the
	current song, pause/play the song, and change the volume.
	
	Connection to a channel: ``MusicInterface(channel)``
		If one already exists, this will return the existing instance.
		This does not check if voice capability is enabled: if ``discord.opus.OpusNotLoaded``
		is thrown, **it will propagate upwards**.
	
	
	Pausing the music:
		``MusicInterface.pause()``
	
	Play the music:
		``MusicInterface.play()``
	
	Toggle the music state:
		``MusicInterface.toggle_state()``
	
	Change the song:
		``await MusicInterface.change_source(song)``
	
	Get/set the volume:
		``MusicInterface.song.volume``
	
	Set the callback to run when a song is finished:
		``MusicInterface.set_callback(f)``
	
	Close the interface and disconnect:
		``await MusicInterface.close()``
	"""

	_client: discord.VoiceClient = None
	channel: discord.VoiceChannel = None
	song: Union[Song, None] = None  # None if we're not playing anything atm
	initialized: bool = False
	target_cb: Callable[[Exception], None] = None

	def __new__(cls, channel: discord.VoiceChannel):
		iface = _active_ifaces.get(channel, None)
		if isinstance(iface, type(cls)):
			return iface
		# if not, we have to create a new one.
		# we do this by going to our parent and essentially asking them
		# to create us for ourselves, because that's how computers work
		return super().__new__(cls)
		
	def __init__(self, channel: discord.VoiceChannel):
		"""
		Initialize our music interface. This should be followed by a call to ``connect()``.

		:param channel: The channel to connect to.
		:raises NoJoinPermission: We do not have permission to join the desired channel.
		:raises NoSpeakPermission: We do not have permission to speak in the desired channel.
		:rtype: None
		"""

		if self.initialized:
			# we already exist. abourt
			return
		
		self.channel: discord.VoiceChannel = channel
		
		channel_perms = channel.permissions_for(channel.guild.me)
		if not channel_perms.connect:
			raise NoJoinPermission()
		if channel_perms.connect and not channel_perms.speak:
			raise NoSpeakPermission()
		
	async def connect(self):
		"""
		Connect to the desired channel. This should be called immediately after creating the object.
		
		:raises TimeoutConnectingError: Timed out connecting to the specified channel.
		:raises discord.opus.OpusNotLoaded: The Opus library needed for voice connectivity is not loaded.
		:raises GuildAlreadyConnected: There is already another active voice connection in the target guild.
		:rtype: None
		"""
		global _active_ifaces
		try:
			self._client = await self.channel.connect(timeout=5)
		except asyncio.TimeoutError:
			raise TimeoutConnectingError("Could not connect to the channel in time")
		except discord.opus.OpusNotLoaded:
			# commands we run sohuld check for this soooooooooooooooo
			raise
		except discord.ClientException:
			# We're already connected somewhere else in this guild. That's the
			# fault of the VoiceManager object
			raise GuildAlreadyConnected()
		except Exception:
			log.critical("modules.music.interface.MusicInterface: UNKNOWN EXCEPTION connecting to a VoiceChannel. "
						"Perhaps the documentation is incomplete?")
			# wtf do we do??
			raise
		else:
			self.initialized = True
			_active_ifaces[self.channel] = self
		
		asyncio.create_task(self.change_source(sources.EmptySource()))  # Clear a TX bug when joining
		
	async def change_source(self, new_source: Union[discord.AudioSource, Song, None]) -> discord.Embed:
		"""
		Change the audio that is currently playing.
		
		:param new_source: a Song to play immediately, or None to stop playing.
		:raises RuntimeError: A raw AudioSource that isn't an EmptySource was passed in.
		:returns: The embed showing the new song, to be sent back.
		"""
		if new_source is None:
			# stop the music
			self.song = None
			self._client.stop()
			return
		if isinstance(new_source, sources.EmptySource):
			self.song = None
			self._client.source = new_source
			return
		if isinstance(new_source, discord.AudioSource):
			log.error("modules.music.interface.MusicInterface: AudioSource was changed from underneath us")
			raise RuntimeError("A raw AudioSource that isn't EmptySource was passed in")
		self._client.stop()
		self.song = new_source
		self.song._super_cleanup = self.target_cb
		self._client.source = await new_source.get_source()
		self._client.play(self._client.source, after=self.target_cb)
		return self.song.to_embed(title="Now Playing")
		
	def play(self):
		self._client.resume()
		
	def pause(self):
		self._client.pause()
		
	def toggle_state(self):
		if not self.playing:
			return  # Nothing to do
		if self.playing and not self.paused:
			self._client.pause()
			return
		if self.playing and self.paused:
			self._client.resume()
			return
	
	async def close(self):
		# Goodbye
		await self._client.disconnect()
		_active_ifaces[self.channel] = None

	@property
	def playing(self) -> bool:
		if self._client.is_playing():
			return not self._client.is_paused()
		else:
			return False

	@property
	def paused(self) -> bool:
		if not self._client.is_playing():
			return False
		else:
			return self._client.is_playing()

	def set_callback(self, f):
		self.target_cb = f
