# 3.7: from __future__ import annotations
from typing import List, Callable, Dict, Union
from prefix import check_prefix
from exceptions import UserBotError, HandlerError, TimerException

import discord
import time
import log
import datetime
import config
import asyncio
import traceback
import sys


def log_message(message: discord.Message):
	if not client.log_all_messages:
		return
	if not message.attachments:  # no attachments
		try:
			log.msg(f"[{message.guild.name} - {message.guild.id}] [#{message.channel.name} - {message.channel.id}] [message id: {message.id}] [{message.author.name}#{message.author.discriminator} - {message.author.id}] {message.author.display_name}: {message.system_content}")
		except AttributeError:
			log.msg(f"[DM] [message id: {message.id}] [{message.author.name}#{message.author.discriminator} - {message.author.id}] {message.system_content}")
	else:
		try:
			log.msg(f"[{message.guild.name} - {message.guild.id}] [#{message.channel.name} - {message.channel.id}] [message id: {message.id}] [{message.author.name}#{message.author.discriminator} - {message.author.id}] {message.author.display_name}: {message.system_content} {' '.join([x.url for x in message.attachments])}")
		except AttributeError:
			log.msg(f"[DM] [message id: {message.id}] [{message.author.name}#{message.author.discriminator} - {message.author.id}] {message.system_content} {' '.join([x.url for x in message.attachments])}")


class FrameworkClient(discord.Client):

	_ready_handlers: List[Callable[[], None]] = []
	_shutdown_handlers: List[Callable[[], None]] = []
	_message_handlers: List[Callable[[discord.Message], None]] = []
	_member_join_handlers: List[Callable[[discord.Member], None]] = []
	_member_leave_handlers: List[Callable[[discord.Member], None]] = []

	_command_lookup: Dict[str, Callable[[discord.Message, str], None]] = {}

	_basic_help: Dict[str, str] = {}
	# Basic help dictionary should be a direct mapping of "command": "description". The prefix should not be included,
	# as it will be automatically inserted into the listed title for each command. The description for each command
	# should be a one-line description, although it can be multiple lines if necessary. Do not include aliases, nor
	# argument information, and shorten decsriptions as much as possible while maintaining easy understandability.

	_long_help: Dict[str, Dict[str, str]] = {}
	# Long help should be a dictionary of dictionaries; keys should be the command, and the fields of the dictionary
	# should be a mapping of title->content in the embed.

	cmd_aliases: Dict[str, List[str]] = {}
	alias_lookup: Dict[str, str] = {}

	cfg_bot_name = config.bot_name

	prefixes: List[str] = []
	default_prefix: str = None
	log_all_messages: bool = config.log_messages

	_trace_timer: float = None

	def __init__(self, *args, **kwargs) -> None:
		self.first_execution: float = None
		self.first_execution_dt: datetime.datetime = None
		super().__init__(*args, **kwargs)
		self.command_count: int = 0
		self.message_count: int = 0
		self.active: bool = False  # tells if we're doing something major eg. loading/unloading or reloading modules
		self.prefixes = config.prefixes
		try:
			self.default_prefix = self.prefixes[0]
		except IndexError:
			log.warning("No prefixes configured in bot - it will be impossible to trigger the bot")

	def run(self, *args, **kwargs) -> None:
		self.first_execution = time.perf_counter()  # monotonic on both Windows and Linux which is :thumbsup:
		self.first_execution_dt = datetime.datetime.utcnow()
		if not kwargs.get("bot", True):
			log.fatal("tried to login with a non-bot token (this framework is designed to run with a bot account)")
			raise UserBotError("Non-bot accounts are not supported")

		# checks to make sure everything is a coroutine
		if config.debug:

			if any([not asyncio.iscoroutinefunction(x) for x in self._ready_handlers]):
				log.critical("not all ready functions are coroutines, this could cause things to stop working or a fatal exception to be raised")
				raise HandlerError("not all ready functions are coroutines, this could cause things to stop working or a fatal exception to be raised")

			if any([not asyncio.iscoroutinefunction(x) for x in self._shutdown_handlers]):
				log.critical("not all shutdown functions are coroutines, this could cause things to stop working or a fatal exception to be raised")
				raise HandlerError("not all shutdown functions are coroutines, this could cause things to stop working or a fatal exception to be raised")

			if any([not asyncio.iscoroutinefunction(x) for x in self._message_handlers]):
				log.critical("not all message handlers are coroutines, this could cause things to stop working or a fatal exception to be raised")
				raise HandlerError("not all message handlers are coroutines, this could cause things to stop working or a fatal exception to be raised")

			if any([not asyncio.iscoroutinefunction(x) for x in self._member_join_handlers]):
				log.critical("not all member join handlers are coroutines, this could cause things to stop working or a fatal exception to be raised")
				raise HandlerError("not all member join handlers are coroutines, this could cause things to stop working or a fatal exception to be raised")

			if any([not asyncio.iscoroutinefunction(x) for x in self._member_leave_handlers]):
				log.critical("not all member leave handlers are coroutines, this could cause things to stop working or a fatal exception to be raised")
				raise HandlerError("not all member leave handlers are coroutines, this could cause things to stop working or a fatal exception to be raised")

			log.debug("all functions good to run (are coroutines)")

		log.info(f"Bot started at {str(self.first_execution_dt)} ({self.first_execution})")
		super().run(*args, **kwargs)

	async def on_ready(self):
		for func in self._ready_handlers:
			await func()
		await self.change_presence(activity=discord.Game(name=f"{self.default_prefix}help"), status=discord.Status.online)
		self.active = True
		log.info(f"Bot is ready to go! We are @{client.user.name}#{client.user.discriminator} (id: {client.user.id})")

	async def on_shutdown(self):
		for func in self._shutdown_handlers:
			await func()
			await asyncio.sleep(0.1)
		client._do_cleanup()
		sys.exit(0)

	async def on_message(self, message: discord.Message):
		log_message(message)
		if not self.active:
			return
		is_cmd, this_prefix = check_prefix(message.content, self.prefixes)
		if not is_cmd:
			for func in self._message_handlers:
				await func(message)
		else:
			command = message.content[len(this_prefix):]
			known_cmd, run_by = check_prefix(command, list(self._command_lookup.keys()))
			if not known_cmd:
				# unknown command branch
				await message.channel.send("`Bad command or file name`\n(See bot help for help)")
				return
			await self._command_lookup[run_by](command, message)

	async def on_member_join(self, member: discord.Member):
		for func in self._member_join_handlers:
			await func(member)

	async def on_member_leave(self, member: discord.Member):
		for func in self._member_leave_handlers:
			await func(member)

	def command(self, trigger: str, aliases: List[str] = None):
		if aliases is None:
			aliases = []

		self.cmd_aliases[trigger] = aliases
		for alias in aliases:
			self.alias_lookup[alias] = trigger

		def inner_decorator(func: Callable[[str, discord.Message], None]):
			nonlocal aliases

			async def new_cmd(command: str, message: discord.Message) -> None:
				try:
					await func(command, message)
				except Exception:
					stackdump = traceback.format_exc()
					embed = discord.Embed(title="Internal error", description=f"There was an error processing the command. Here's the stack trace, if necessary (this is also recorded in the log):\n```{stackdump}```", colour=0xf00000)
					embed = embed.set_footer(text="Error occurred at " + str(datetime.datetime.utcnow()))
					await message.channel.send(embed=embed)
					log.error(f"Error processing command: {message.content}", include_exception=True)

			# now add the trigger plus aliases to the command dict
			self._command_lookup[trigger] = new_cmd
			for alias in aliases:
				self._command_lookup[alias] = new_cmd

			return new_cmd
		return inner_decorator

	def member_join(self, func: Callable[[], None]):
		self._member_join_handlers.append(func)
		return func

	def member_leave(self, func: Callable[[], None]):
		self._member_leave_handlers.append(func)
		return func

	def message(self, func: Callable[[], None]):
		self._message_handlers.append(func)
		return func

	def ready(self, func: Callable[[], None]):
		self._ready_handlers.append(func)
		return func

	def shutdown(self, func: Callable[[], None]):
		self._shutdown_handlers.append(func)
		return func

	def basic_help(self, title: str, desc: str, include_prefix: bool = True):
		if include_prefix:
			self._basic_help.update({f"{self.default_prefix}{title}": desc})
		else:
			self._basic_help.update({f"{title}": desc})

	def long_help(self, cmd: str, mapping: dict):
		self._long_help[cmd] = mapping


client = FrameworkClient(status=discord.Status(config.boot_status))
