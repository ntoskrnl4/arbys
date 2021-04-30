from client import client
from datetime import datetime

import discord
import log
import os
import socket
import threading
import time


try:
	import psutil
except ModuleNotFoundError:
	has_psutil = False
	psutil = None
else:
	has_psutil = True
	psutil_update_thread = None

client.basic_help(title="stats", desc=f"Shows running statistics of {client.bot_name}")

detailed_help = {
	"Usage": f"{client.default_prefix}stats",
	"Description": f"This command shows different available statistics of {client.bot_name}, including servers, uptime, and commands run.",
	"Related": f"`{client.default_prefix}info` - shows information about {client.bot_name}",
}
client.long_help(cmd="stats", mapping=detailed_help)


@client.command(trigger="stats", aliases=["statistics", "s", "status"])
async def statistics(command: str, message: discord.Message):
	if "--uptime" in command:
		up = time.perf_counter() - client.first_execution
		await message.channel.send(f"Uptime:\n`{up:.3f}` seconds\n`{up/86400:.4f}` days")
		return

	async with message.channel.typing():

		embed = discord.Embed(title=f"Running statistics for {client.bot_name}", description=discord.Embed.Empty, color=0x404040)

		up = time.perf_counter() - client.first_execution
		embed = embed.add_field(name="Uptime", value=f"{up:.3f} seconds\n{up/86400:.4f} days")
		embed = embed.add_field(name="Servers", value=len(client.guilds))
		embed = embed.add_field(name="Commands since boot", value=client.command_count)
		embed = embed.add_field(name="Messages since boot", value=client.message_count)
		embed = embed.add_field(name="Messages in cache", value=len(client._connection._messages))
		n_connected = len(client.voice_clients)
		n_playing = len([x for x in client.voice_clients if x.is_playing()])
		embed = embed.add_field(name="Connected voice chats", value=f"{n_connected} ({n_playing} playing)")
		embed = embed.add_field(name="Bot Process ID", value=os.getpid())
		embed = embed.add_field(name="Host Machine Name", value=socket.gethostname())

		if has_psutil:
			try:
				temp = psutil.sensors_temperatures()['cpu-thermal'][0].current
			except (AttributeError, KeyError):
				temp = None
			self = psutil.Process()
			cpu_self = self.cpu_percent(interval=1)
			self_m_used = self.memory_info().rss
			m_raw = psutil.virtual_memory()
			m_total = m_raw.total
			m_available = m_raw.available
			m_used = m_total - m_available
			cpu = psutil.cpu_percent(percpu=True)
			index = 0
			cpu_text = ""
			for v in cpu:
				cpu_text += f"**CPU {index}:** {v}%\n"
				index += 1

			embed = embed.add_field(name="Host CPU temp", value=f"{int(temp) if temp is not None else 'Unknown'}°C")
			embed = embed.add_field(name="Process Memory", value=f"{self_m_used/(1024*1024):.3f} MiB")
			embed = embed.add_field(name="Process CPU", value=f"{cpu_self:.1f}%")
			embed = embed.add_field(name="System RAM Usage", value=f"{m_used/(1024*1024):.1f}/{m_total/(1024*1024):.1f} MiB ({(m_used/m_total)*100:.2f}%)")
			embed = embed.add_field(name="System CPU", value=cpu_text)
		
		if client.__version__ == "0.7":
			# todo: v0.7 - update references
			raise RuntimeError("TODO: Update references")
		
		bg_count = len(client._background_tasks)
		cmd_count = len(set(client._command_lookup.values()))
		ready_count = len(client._ready_handlers)
		shutdown_count = len(client._shutdown_handlers)
		msg_count = len(client._message_handlers)
		mj_count = len(client._member_join_handlers)
		ml_count = len(client._member_remove_handlers)
		readd_count = len(client._reaction_add_handlers)
		redel_count = len(client._reaction_remove_handlers)
		
		embed = embed.add_field(name="Registered Event Handlers",
								value=f"Registered commands: {cmd_count}\n"
									f"Background tasks: {bg_count}\n"
									f"Ready handlers: {ready_count}\n"
									f"Shutdown handlers: {shutdown_count}\n"
									f"Message handlers: {msg_count}\n"
									f"Member join handlers: {mj_count}\n"
									f"Member leave handlers: {ml_count}\n"
									f"Reaction add handlers: {readd_count}\n"
									f"Reaction remove handlers: {redel_count}\n")

		embed = embed.set_footer(text=datetime.utcnow().__str__())
	await message.channel.send(embed=embed)

