# 3.7: from __future__ import annotations
from typing import List, Callable, Dict, Tuple, Union
from prefix import check_prefix
from exceptions import UserBotError, HandlerError, TimerException

import discord
import time
import log
import datetime
import config
import asyncio
import traceback


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

	_basic_help = {}
	# Basic help dictionary should be a direct mapping of "command": "description". The prefix should not be included,
	# as it will be automatically inserted into the listed title for each command. The description for each command
	# should be a one-line description, although it can be multiple lines if necessary. These should be kept short as
	# possible, as the basic help list will be compacted in the embed as much as possible. Do not include aliases, nor
	# argument information, and shorten decsriptions as much as possible while maintaining easy understandability
	# (breaking grammar will probably be necessary to achieve this).

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
			log.warning("No prefixes configured in bot - it may be impossible to trigger the bot")
			log.info("Bot prefix set to `AddPrefixesForMeThanks ` as a result of no set prefix")
			self.default_prefix = "AddPrefixesForMeThanks "

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

	async def on_message(self, message: discord.Message):
		log_message(message)
		if not self.active:
			return
		for func in self._message_handlers:
			await func(message)

	async def on_member_join(self, member: discord.Member):
		for func in self._member_join_handlers:
			await func(member)

	async def on_member_leave(self, member: discord.Member):
		for func in self._member_leave_handlers:
			await func(member)

	def command(self, trigger: str, aliases: List[str] = None, prefixes=None):
		if aliases is None:
			aliases = []

		self.cmd_aliases[trigger] = aliases
		for alias in aliases:
			self.alias_lookup[alias] = trigger

		def inner_decorator(func: Callable[[str, discord.Message], None]):
			async def new_cmd(message: discord.Message) -> None:
				nonlocal prefixes, trigger, aliases
				if prefixes is None:
					prefixes = client.prefixes  # "self" shouldn't be defined, yes? PyCharm thinks otherwise...
				result, this_prefix = check_prefix(message.content, prefixes)
				if not result:
					return
				else:
					# No way to do a case-insensitive replace so we simply chop the first X characters with the prefix
					command = message.content[len(this_prefix):]

					# We can literally just run everything we did with prefixes with the command as well
					triggers = [trigger]
					triggers.extend(aliases)
					is_us, _ = check_prefix(command, triggers)
					if not is_us:
						return
					else:
						client.debug_response_trace(flag=True)
						try:
							await func(command=command, message=message)  # PyCharm thinks these are unexpected, but they're not
						except Exception:
							stackdump = traceback.format_exc()
							embed = discord.Embed(title="Internal error", description=f"There was an error processing the command. Here's the stack trace, if necessary (this is also recorded in the log):\n```{stackdump}```", colour=0xf00000)
							embed = embed.set_footer(text="Error occurred at " + str(datetime.datetime.utcnow()))
							await message.channel.send(embed=embed)
							log.error(f"Error processing command: {message.content}", include_exception=True)
			self._message_handlers.append(new_cmd)
			return new_cmd
		return inner_decorator

	def member_join(self, func: Callable[[], None]):
		self._member_join_handlers.append(func)

	def member_leave(self, func: Callable[[], None]):
		self._member_leave_handlers.append(func)

	def ready(self, func: Callable[[], None]):
		self._ready_handlers.append(func)

	def shutdown(self, func: Callable[[], None]):
		self._shutdown_handlers.append(func)

	def basic_help(self, title: str, desc: str, include_prefix: bool = True):
		if include_prefix:
			self._basic_help.update({f"{self.default_prefix}{title}": desc})
		else:
			self._basic_help.update({f"{title}": desc})

	def long_help(self, cmd: str, mapping: dict):
		self._long_help[cmd] = mapping

	def debug_response_trace(self, flag: Union[bool, int] = False, clear: Union[bool, int] = False, reset: Union[bool, int] = False):
		"""
		Internal timer to measure response times.

		:param flag: Activate timer and start timing. If running, record timer to log.
		:param clear: Log and reset the timer.
		:param reset: Force reset the timer. Exception if any other value is True at the same time.
		"""
		marker = time.perf_counter()  # A double's precision is high enough that at 10 million seconds of uptime, the
		# precision is only at about 1.8ns, which is far more than enough to measure timings. At 20 million seconds of
		# uptime, precision would be 3.6ns. 20M seconds of uptime is 231 days, which is in all honesty an unlikely
		# uptime to reach, although it's still good to know that should we get (and go past) there, our precision is
		# still in the nanoseconds range.
		if config.debug:
			if bool(not (flag or clear) and (not reset)):
				try:
					raise TimerException("Function Argument Error")
				except TimerException:
					log.warning("Timer in client object activated, but no action performed (warn and clear args are both False)", include_exception=True)
					return

			if bool(flag and (not clear) and (not reset)):
				# Start or log timer
				if self._trace_timer is None:
					# Start the timer
					self._trace_timer = marker
					return
				if self._trace_timer is not None:
					# Log timer
					log.debug(f"Response time was {(marker-self._trace_timer)*1000:.4f} ms")

			if bool(clear and (not flag) and (not reset)):
				log.debug(f"Response time was {(marker-self._trace_timer)*1000:.4f} ms")
				self._trace_timer = None

			if bool(clear and flag and (not reset)):
				log.debug(f"Response time was {(marker-self._trace_timer)*1000:.4f} ms")
				self._trace_timer = marker

			if bool(reset and not (clear or flag)):
				self._trace_timer = None

			if bool(reset and (clear or flag)):
				try:
					raise TimerException("Function Argument Error")
				except TimerException:
					log.warning(f"Timer in client object called with reset and another arg true (reset: {reset}, flag: {flag}, clear: {clear}", include_exception=True)
					return


client = FrameworkClient(status=discord.Status(config.boot_status))
