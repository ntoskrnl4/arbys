from client import client
import discord


@client.command(trigger="cqdx")
async def command(command: str, message: discord.Message):
	await message.channel.send("https://www.youtube.com/watch?v=5_bHuCwKmkI")
	return
