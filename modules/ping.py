from client import client

import discord


@client.command(trigger="ping", aliases=["p"])
async def help_command(command: str, message: discord.Message):
	await message.channel.send(f"Latency to the connected Discord API endpoint: `{client.latency*1000:.0f} ms`")
	return

client.basic_help("ping", "Returns the bot's latency to its connected API endpoint.")

help_long_help = {
	"Usage:": f"`{client.default_prefix}ping`",
	"Description": "This command returns the bot's latency to the Discord API endpoint it is connected to."
}
client.long_help("ping", help_long_help)
