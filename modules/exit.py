from key import shutdown_users, shutdown_easter_egg_user
from datetime import datetime
from client import client
import discord
import time
import log
import os


cmd_name = "exit"

client.basic_help(title=cmd_name, desc="Cleans up and shuts down the bot.")

detailed_help = {
	"Usage": f"{client.default_prefix}{cmd_name}",
	"Arguments": "None",
	"Description": "This command completely exits out of the bot, and performs any registered cleanup procedures. A user ID check is performed against a builtin list of users allowed to run this command.",
	# NO Aliases field, this will be added automatically!
}
client.long_help(cmd=cmd_name, mapping=detailed_help)


@client.command(trigger=cmd_name,
				aliases=[])  # aliases is a list of strs of other triggers for the command
async def command(command: str, message: discord.Message):
	if (any([x.id in key.shutdown_ids for x in message.author.roles]) or message.author.id in key.shutdown_ids):
		try:
			await message.add_reaction("❌")
			if message.author.id == shutdown_easter_egg_user:
				await message.channel.send("*hehehe*\n\nCan't fool me! >:3")
		except:
			pass
		finally:
			return
	else:
		await message.channel.send("Shutting down bot...")
		await message.channel.send(f"Uptime: {time.perf_counter() - client.first_execution:.3f} seconds ({(time.perf_counter() - client.first_execution)/86400:.3f} days)")
		log.info(f"Bot shutdown initiated at {datetime.utcnow().__str__()} by {message.author.name}#{message.author.discriminator}")
		await client.on_shutdown()

	return


@client.command(trigger="_exit")
async def emergency_suicide(command: str, message: discord.Message):
	if message.author.id not in shutdown_users:
		try:
			await message.add_reaction("❌")
		except:
			pass
		finally:
			return
	else:
		await message.channel.send("Shutting down bot...")
		os._exit(2)
