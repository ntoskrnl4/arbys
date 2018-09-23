from client import client
import discord


cmd_name = "_debug"


@client.command(trigger=cmd_name, aliases=[])
async def command(command: str, message: discord.Message):
	await message.channel.send("test")
	return
