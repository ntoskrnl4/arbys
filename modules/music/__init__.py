"""
Primary module for the music command in the bot. All other classes and functions
are in the different modules in this folder.
"""
from typing import List

import log
from client import client
from modules.__common__ import confirm
from .manager import get_manager
from .exceptions import *

import asyncio
import discord


user_blacklist: List[int] = [
	# Try not to get yourself added to this list
]

# We have to create a master lock, because there are some instances where if you
# have several commands run simultaneously you can break some things. I don't
# really know exactly how, but it did sometimes happen with the old music module
# (eg. if you changed volume while adding a song, or if you changed the bot
# state while you were also pausing the bot).
master_lock = asyncio.Lock()


@client.command(trigger="music")
async def tree_root(command: str, message: discord.Message):
	parts = command.split(" ")

	if message.author.id in user_blacklist:
		await message.channel.send("Command rejected: You are not permitted to use this command")
		return

	if len(parts) == 1:
		await message.channel.send("Subcommand not given. See command help for available subcommands.")
		return
	
	if message.guild is None:
		await message.channel.send("Sorry, but that command is not allowed in DMs.")
		return
	
	if not discord.opus.is_loaded():
		await message.channel.send("Internal error: The required library for voice functionality is not loaded.")
		return
	
	mgr = manager.get_manager(message.guild)
	mgr.change_message_channel(message.channel)
	
	if parts[1] == "play":
		try:
			await mgr.play()
		except NoActiveConnection:
			await message.channel.send("State error: You must join the bot to a voice channel before playing music")
			return
		except StopIteration:
			await message.channel.send("Queue exhausted: stopping playback")
	
	assert isinstance(message.channel, discord.TextChannel)
	assert isinstance(message.author, discord.Member)
	assert isinstance(message.guild, discord.Guild)
	# await message.channel.trigger_typing()
	if parts[1] == "join":
		# Different possible states to be in:
		# 	User not in voice, bot not in voice
		# 	User not in voice, bot in voice
		# 	User in voice, bot not in voice (bingo!)
		# 	User in voice, bot in voice, same channel
		# 	User in voice, bot in voice, different channel
		if message.author.voice is None:
			# user not in voice
			if message.guild.me.voice is None:
				# user not in voice, we're not in voice
				await message.channel.send("Cannot join channel: Ambiguous/unknown target channel")
				return
			else:
				# user not in voice, we're in voice
				await message.channel.send("Cannot join channel: Already in a channel (also, next time please "
											"join the channel you are referring to first)")
				return
		else:
			# user in voice
			if message.guild.me.voice is None:
				# user in voice, we're not in voice
				# correct usage
				try:
					await mgr.connect(message.author.voice.channel)
					breakpoint()
				except TimeoutConnectingError:
					await message.channel.send("Channel join failed: Timeout")
					return
				except discord.opus.OpusNotLoaded:
					await message.channel.send("Internal error: Opus module not loaded\n(fun fact, "
												"this code branch shouldn't be hit)")
					return
				except GuildAlreadyConnected:
					await message.channel.send("State error: There is already another active voice connection in "
												"this guild\n(fun fact, this code branch shouldn't be hit)")
					return
				except NoJoinPermission:
					await message.channel.send("Cannot join channel: Insufficient permissions to connect to the channel")
					return
				except NoSpeakPermission:
					await message.channel.send("Refusing to join channel: Insufficient permissions to speak in the channel")
					return
				except Exception as e:
					log.warning("Unknown exception trying to join the channel")
					raise
				await confirm(message, "Joined the channel")
			else:
				if message.guild.me.voice.channel == message.author.voice.channel:
					# user in voice, we're in voice, same channel
					await message.channel.send("Already in this channel with you")
					return
				else:
					# user in voice, we're in voice, different channel
					await message.channel.send("Cannot join channel: Already in a different channel in this server")
					return
	
	if parts[1] == "add":
		media = command.split(" ", 1)[1][4:]  # Get just the media
		if media == "":
			await message.channel.send("Nothing given to add to queue")
			return
		await mgr.add_to_queue(media)
			
