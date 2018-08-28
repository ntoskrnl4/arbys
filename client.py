from __future__ import annotations
from typing import List, Callable

import discord
import time
import log
import datetime
import config


class FrameworkClient(discord.Client):

	_ready_handlers: List[Callable[[], None]] = []
	_shutdown_handlers: List[Callable[[], None]] = []
	_message_handlers: List[Callable[[str, discord.Message], None]] = []
	_member_join_handlers: List[Callable[[discord.Member], None]] = []
	_member_leave_handlers: List[Callable[[discord.Member], None]] = []

	def __init__(self, *args, **kwargs) -> None:
		self.first_execution: float = None
		self.first_execution_dt: datetime.datetime = None
		self.last_received_message: float = None
		super().__init__(*args, **kwargs)
		self.command_count: int = 0
		self.message_count: int = 0
		self.shutting_down: bool = False  # we'll use this to check if we're shutting down and therefore ignore msgs

	def run(self, *args, **kwargs) -> None:
		self.first_execution = time.perf_counter()  # monotonic on both Windows and Linux which is :thumbsup:
		self.first_execution_dt = datetime.datetime.utcnow()
		log.info(f"__main__.DiscordClient.run(): Bot started at {str(self.first_execution_dt)} ({self.first_execution})")
		super().run(*args, **kwargs)


client = FrameworkClient(status=discord.Status(config.boot_status))
