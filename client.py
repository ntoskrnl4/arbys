from exceptions import UserBotError, HandlerError
from typing import List, Callable, Dict, Union

import asyncio
import config
import datetime
import discord
import log
import os
import prefix
import sys
import time
import traceback


class FrameworkClient(discord.Client):
	__version__ = "0.5.2"

	_background_tasks: List[Callable[[], None]] = []
	_ready_handlers: List[Callable[[], None]] = []
	_shutdown_handlers: List[Callable[[], None]] = []
	_message_handlers: List[Callable[[discord.Message], None]] = []
	_member_join_handlers: List[Callable[[discord.Member], None]] = []
	_member_remove_handlers: List[Callable[[discord.Member], None]] = []
	_reaction_add_handlers: List[Callable[[discord.Reaction, Union[discord.User, discord.Member]], None]] = []
	_reaction_remove_handlers: List[Callable[[discord.Reaction, Union[discord.User, discord.Member]], None]] = []

	_command_lookup: Dict[str, Callable[[discord.Message, str], None]] = {}

	_basic_help: Dict[str, str] = {}
	# Basic help dictionary should be a direct mapping of "command": "description". The prefix should not be included,
	# as it will be automatically inserted into the listed title for each command. The description for each command
	# should be a one-line description, although it can be multiple lines if necessary. Do not include aliases, nor
	# argument information, and keep descriptions terse.

	_long_help: Dict[str, Dict[str, str]] = {}
	# Long help should be a dictionary of dictionaries; keys should be the command, and the fields of the dictionary
	# should be a mapping of title->content in the embed.

	unknown_command = "`Bad command or file name`\n(See bot help for help)"
	# String that will be given when a command is not found.

	cmd_aliases: Dict[str, List[str]] = {}
	# Command -> aliases
	alias_lookup: Dict[str, str] = {}
	# Alias -> command

	bot_name = config.bot_name

	prefixes: List[str] = []
	default_prefix: str = None
	log_all_messages: bool = config.log_messages
	message_count: int = 0
	command_count: int = 0
	first_execution: float = None
	first_execution_dt: datetime.datetime = None

	def __init__(self, *args, **kwargs) -> None:
		super().__init__(*args, **kwargs)
		self._has_been_readied: bool = False
		self.active: bool = False
		self.prefixes = [x.lower() for x in config.prefixes]
		try:
			self.default_prefix = self.prefixes[0]
			self._no_boot_prefixes = False
		except IndexError:
			log.warning("No prefixes configured in bot - only valid prefix will be a self mention")
			self._no_boot_prefixes = True

	def run(self, *args, **kwargs) -> None:
		self.first_execution = time.perf_counter()  # monotonic on both Windows and Linux which is :thumbsup:
		self.first_execution_dt = datetime.datetime.utcnow()
		if not kwargs.get("bot", True):
			log.fatal("tried to login with a non-bot token (this framework is designed to run with a bot account)")
			raise UserBotError("Non-bot accounts are not supported")

		# checks to make sure everything is a coroutine
		if any([not asyncio.iscoroutinefunction(x) for x in self._ready_handlers]):
			log.critical("not all ready functions are coroutines")
			raise HandlerError("not all ready functions are coroutines")
		if any([not asyncio.iscoroutinefunction(x) for x in self._shutdown_handlers]):
			log.critical("not all shutdown functions are coroutines")
			raise HandlerError("not all shutdown functions are coroutines")
		if any([not asyncio.iscoroutinefunction(x) for x in self._message_handlers]):
			log.critical("not all message handlers are coroutines")
			raise HandlerError("not all message handlers are coroutines")
		if any([not asyncio.iscoroutinefunction(x) for x in self._member_join_handlers]):
			log.critical("not all member join handlers are coroutines")
			raise HandlerError("not all member join handlers are coroutines")
		if any([not asyncio.iscoroutinefunction(x) for x in self._member_remove_handlers]):
			log.critical("not all member leave handlers are coroutines")
			raise HandlerError(f"not all member leave handlers are coroutines")
		if any([not asyncio.iscoroutinefunction(x) for x in self._reaction_add_handlers]):
			log.critical("not all reaction add handlers are coroutines")
			raise HandlerError(f"not all reaction add handlers are coroutines")
		if any([not asyncio.iscoroutinefunction(x) for x in self._reaction_remove_handlers]):
			log.critical("not all reaction remove handlers are coroutines")
			raise HandlerError(f"not all reaction remove handlers are coroutines")

		log.debug("all functions good to run (are coroutines)")

		log.info(f"Bot started at {str(self.first_execution_dt)} ({self.first_execution})")
		super().run(*args, **kwargs)

	# ==========
	# d.py event triggers
	# ==========

	async def on_ready(self):
		if self._has_been_readied:
			await self.change_presence(activity=discord.Game(name=self.boot_playing_msg), status=discord.Status.online)
			log.info("Bot reconnected to Discord")
			return

		# add our own mention as a prefix
		self.prefixes.append(f"<@{self.user.id}> ")
		self.prefixes.append(f"<@!{self.user.id}> ")
		if not config.no_bpid_prefix:
			self.prefixes.append(f"bpid{os.getpid()} ")  # Add our own Bot Process ID to differentiate between instances

		if self._no_boot_prefixes:
			# we need to add our own then
			self.default_prefix = f"<@{self.user.id}> "
			self.boot_playing_msg = f"@{self.user.name} help"
		else:
			self.boot_playing_msg = f"{self.default_prefix}help"

		for func in self._ready_handlers:
			try:
				await func()
			except Exception as e:
				log.warning("Ignoring exception in ready coroutine (see stack trace below)", include_exception=True)
		await self.change_presence(activity=discord.Game(name=self.boot_playing_msg), status=discord.Status.online)
		self.active = True
		self._has_been_readied = True
		log.info(f"Bot is ready to go! We are @{client.user.name}#{client.user.discriminator} (id: {client.user.id})")
		log.info(f"Bot process ID is {os.getpid()}. If no_bpid_prefix is disabled this specific instance can be addressed with bpid{os.getpid()}.")

	async def on_shutdown(self):
		log.debug(f"entering shutdown handler, here's goodbye from on_shutdown()")
		for func in self._shutdown_handlers:
			try:
				await func()
			except Exception as e:
				log.warning("Ignoring exception in shutdown coroutine (see stack trace below)", include_exception=True)
			await asyncio.sleep(0.1)
		client._do_cleanup()
		sys.exit(0)

	async def on_message(self, message: discord.Message):

		self.message_count += 1

		if self.active:
			for func in self._message_handlers:
				try:
					await func(message)
				except Exception:
					log.warning("Ignoring exception in message coroutine (see stack trace below)", include_exception=True)
		is_cmd, this_prefix = prefix.check_bot_prefix(message.content, self.prefixes)
		if is_cmd:
			command = message.content[len(this_prefix):]
			known_cmd, run_by = prefix.check_command_prefix(command, list(self._command_lookup.keys()))
			if (self.active is False) and (run_by != "_exec"):
				return
			if not known_cmd:
				# unknown command branch
				await message.channel.send(self.unknown_command)
				return
			await self._command_lookup[run_by](command, message)

	async def on_reaction_add(self, reaction: discord.Reaction, source: Union[discord.User, discord.Member]):
		for func in self._reaction_add_handlers:
			try:
				await func(reaction, source)
			except Exception:
				log.warning("Ignoring exception in reaction_add coroutine (see stack trace below)", include_exception=True)

	async def on_reaction_remove(self, reaction: discord.Reaction, source: Union[discord.User, discord.Member]):
		for func in self._reaction_remove_handlers:
			try:
				await func(reaction, source)
			except Exception:
				log.warning("Ignoring exception in reaction_remove coroutine (see stack trace below)", include_exception=True)

	async def on_member_join(self, member: discord.Member):
		for func in self._member_join_handlers:
			try:
				await func(member)
			except Exception:
				log.warning("Ignoring exception in member_join coroutine (see stack trace below)", include_exception=True)

	async def on_member_remove(self, member: discord.Member):
		for func in self._member_remove_handlers:
			try:
				await func(member)
			except Exception:
				log.warning("Ignoring exception in member_leave coroutine (see stack trace below)", include_exception=True)

	# ==========
	# Decorators
	# ==========

	def background(self, period: int):
		def inside(func: Callable[[], None]):
			nonlocal period

			async def modified_function():
				await self.wait_until_ready()
				while not self.is_closed():
					try:
						await func()
					except Exception:
						log.error(f"Error processing background task {func.__name__}():", include_exception=True)
					await asyncio.sleep(period)

			self._background_tasks.append(self.loop.create_task(modified_function()))
			modified_function.__name__ = func.__name__
			modified_function.__module__ = func.__module__
			log.debug(f"registered new background task {func.__name__}() with period {period} seconds")
			return modified_function
		return inside

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
					self.command_count += 1
					# The following line is the gateway back into external code
					await func(command, message)
				except Exception:
					timestamp = datetime.datetime.utcnow().__str__()
					stackdump = traceback.format_exc()
					embed = discord.Embed(title="Internal error", description=f"There was an error processing the command. Here's the stack trace, if necessary (this is also recorded in the log):\n```{stackdump}```", colour=0xf00000)
					embed = embed.set_footer(text="Error occurred at " + timestamp)
					await message.channel.send(embed=embed)
					log.error(f"Error processing command: {message.content}", include_exception=True)

			# now add the trigger plus aliases to the command dict
			self._command_lookup[trigger] = new_cmd
			for alias in aliases:  # name shadows but we don't care tbh it's only a tempvar
				self._command_lookup[alias] = new_cmd
			new_cmd.__name__ = func.__name__
			new_cmd.__module__ = func.__module__

			log.debug(f"registered new command handler {func.__name__}() with trigger '{trigger}' and aliases: {aliases}")
			return new_cmd
		return inner_decorator

	def member_join(self, func: Callable[[], None]):
		self._member_join_handlers.append(func)
		log.debug(f"registered new member_join handler {func.__name__}()")
		return func

	def member_remove(self, func: Callable[[], None]):
		self._member_remove_handlers.append(func)
		log.debug(f"registered new member_remove handler {func.__name__}()")
		return func

	def message(self, receive_self: bool = True):
		def inner_decorator(func: Callable[[discord.Message], None]):
			async def wrapped_handler(message: discord.Message):
				if not receive_self and message.author.id == client.user.id:
					return
				await func(message)
			self._message_handlers.append(func)
			log.debug(f"registered new message handler {func.__name__}()")
			return wrapped_handler
		return inner_decorator

	def reaction_add(self, func: Callable[[], None]):
		self._reaction_add_handlers.append(func)
		log.debug(f"registered new new reaction handler {func.__name__}()")
		return func

	def reaction_remove(self, func: Callable[[], None]):
		self._reaction_remove_handlers.append(func)
		log.debug(f"registered new reaction remove handler {func.__name__}()")
		return func

	def ready(self, func: Callable[[], None]):
		self._ready_handlers.append(func)
		log.debug(f"registered new ready handler {func.__name__}()")
		return func

	def shutdown(self, func: Callable[[], None]):
		self._shutdown_handlers.append(func)
		log.debug(f"registered new shutdown handler {func.__name__}()")
		return func

	# ==========
	# Other Functions
	# ==========

	def basic_help(self, title: str, desc: str, include_prefix: bool = True):
		# check first that nothing's blank
		if title.strip() == "" or desc.strip() == "":
			log.critical("Blank content in help message: running the help command with this blank content *will* throw an error. Traceback logged under debug level.")
			log.debug("".join(traceback.format_stack()))

		if include_prefix:
			self._basic_help.update({f"{self.default_prefix}{title}": desc})
		else:
			self._basic_help.update({f"{title}": desc})
		log.debug(f"registered new basic_help entry under the title {title}")

	def long_help(self, cmd: str, mapping: Dict[str, str]):
		if cmd.strip() == "" or "" in list(mapping.values()) + list(mapping.keys()):
			# if any blank values, throw an error
			log.critical("Blank content in help message: running the help command with this blank content *will* throw an error. Traceback logged under debug level.")
			log.debug("".join(traceback.format_stack()))

		self._long_help[cmd] = mapping
		log.debug(f"registered new long_help entry for command {cmd}")


client = FrameworkClient(status=discord.Status(config.boot_status), max_messages=config.message_cache_size)
