from modules import __common__
from datetime import datetime
from client import client
import discord
import time
import key
import log
import os


client.basic_help(title="exit", desc="Cleans up and shuts down the bot.")

detailed_help = {
	"Usage": f"{client.default_prefix}exit [pid]",
	"Arguments": "`pid` - (Optional) Process ID identifying which bot to exit out of",
	"Description": "This command completely exits out of the bot, and performs any registered cleanup procedures. A user ID check is performed against a builtin list of users allowed to run this command.",
	# NO Aliases field, this will be added automatically!
}
client.long_help(cmd="exit", mapping=detailed_help)


@client.command(trigger="exit")
async def command(command: str, message: discord.Message):
	if not __common__.check_permission(message.author):
		await message.add_reaction("❌")
		if message.author.id == key.shutdown_easter_egg_user:
			await message.channel.send("*hehehe*\n\nCan't fool me! >:3")
		return
	else:
		parts = command.split(" ")
		try:
			target_pid = int(parts[2])
		except IndexError:
			target_pid = os.getpid()
		except ValueError:
			await message.channel.send("Invalid integer of PID to kill")
			return
		if target_pid == os.getpid():
			await message.channel.send("Shutting down bot...")
			await message.channel.send(f"Uptime: {time.perf_counter() - client.first_execution:.3f} seconds ({(time.perf_counter() - client.first_execution)/86400:.3f} days)")
			log.info(f"Bot shutdown initiated at {datetime.utcnow().__str__()} by {message.author.name}#{message.author.discriminator}")
			await client.on_shutdown()
	return


@client.command(trigger="_exit")
async def emergency_suicide(command: str, message: discord.Message):
	if not __common__.check_permission(message.author):
		await message.add_reaction("❌")
		return
	else:
		os._exit(2)