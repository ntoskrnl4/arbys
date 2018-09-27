from client import client
import discord


@client.command(trigger="relay")
async def command(command: str, message: discord.Message):
	await message.channel.send("*clickclickclickclickclickclickclickclickclickclickclickclickclick*")
	return
