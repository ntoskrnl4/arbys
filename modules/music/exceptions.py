import asyncio
import discord


class TimeoutConnectingError(asyncio.TimeoutError):
	"""Timeout specific to connecting to a voice channel"""


class GuildAlreadyConnected(discord.ClientException):
	"""We're already connected to a channel in this guild."""


class NoJoinPermission(discord.ClientException):
	"""Insufficient permission to join a channel."""


class NoSpeakPermission(discord.ClientException):
	"""Insufficient permission to speak in a channel we can join."""


class NoActiveConnection(discord.ClientException):
	"""There is no active voice channel to perform the operation."""