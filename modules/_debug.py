from client import client
import discord


cmd_name = "_debug"


@client.command(trigger=cmd_name, aliases=[])
async def command(command: str, message: discord.Message):
	raise Exception("Test exception")
	return
