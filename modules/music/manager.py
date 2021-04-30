
from .interface import MusicInterface
from .exceptions import *
from .song import Song
from typing import Dict, List, Optional, Deque

import collections
import discord

active_managers: Dict[discord.Guild, "GuildManager"] = {}


def get_manager(guild: discord.Guild) -> "GuildManager":
	"""Retrieves a GuildManager for the given guild. If not found, creates one."""
	return active_managers.get(guild, GuildManager(guild))


class GuildManager:
	"""
	Coordinates audio for an entire guild, including queues, interfaces, etc.
	"""
	
	guild: discord.Guild = None
	channel: Optional[discord.VoiceChannel] = None
	interface: Optional[MusicInterface] = None
	queue: Deque[Song] = collections.deque(maxlen=25)
	command_channel: discord.TextChannel = None
	
	def __init__(self, guild: discord.Guild):
		global active_managers
		self.guild = guild
		active_managers[guild] = self
	
	async def connect(self, channel: discord.VoiceChannel):
		"""
		Connects to a voice channel.
		
		:param channel: The channel to connect to.
		:rtype: None
		:raises TimeoutConnectingError: Timed out connecting to the specified channel.
		:raises discord.opus.OpusNotLoaded: The Opus library needed for voice connectivity is not loaded.
		:raises GuildAlreadyConnected: There is already another active voice connection in the target guild.
		:raises NoJoinPermission: We do not have permission to join the desired channel.
		:raises NoSpeakPermission: We do not have permission to speak in the desired channel.
		"""
		if (self.channel is not None) and (self.interface is not None):
			raise GuildAlreadyConnected()
		self.interface = MusicInterface(channel)
		await self.interface.connect()
		self.channel = channel

	async def disconnect(self, clear_queue: bool = True):
		"""
		Exits the voice channel and clears the queue.
		
		:param clear_queue: Whether to clear the music queue when leaving the channel. Defaults to <code>True</code>
		:return: <code>None</code>
		"""
		self.channel = None
		await self.interface.close()
		self.interface = None
		if clear_queue:
			self.queue = collections.deque(maxlen=25)
	
	async def play(self):
		"""
		Starts playing music from the currently active queue for this guild.
		
		:raises NoActiveConnection: Not connected to a voice channel.
		:raises StopIteration: Queue has been drained.
		"""
		if (self.channel is not None) and (self.interface is not None):
			raise NoActiveConnection()
		while True:
			try:
				next = self.queue.popleft()
			except IndexError:
				raise StopIteration("Done playing music [queue exhausted]")
			await self.command_channel.send(embed=await self.interface.change_source(next))
			
			while self.interface.playing or self.interface.paused:
				try:
					await asyncio.sleep(1)
				except:
					pass
	
	async def add_to_queue(self, url):
		"""Adds a song to the queue and sends the new song embed."""
		new = Song(url)
		await new.load_info()
		self.queue.append(new)
		await self.command_channel.send(embed=new.to_embed(title="Song added to queue", queue_pos=self.queue.index(new)))
	
	def change_message_channel(self, ch: discord.TextChannel):
		"""Changes the channel to which messages about songs are sent to."""
		self.command_channel = ch
	
	async def send_current_song_info(self):
		"""Sends info about the currently playing song back to the command channel."""
		await self.command_channel.send(embed=self.interface.song.to_embed(title="Currently Playing"))