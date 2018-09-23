from client import client
import discord


client.basic_help(title="cqdx", desc="SAY Q DX SAY Q DX SAY Q DXXXXX  SAY Q DX SAY Q DX SAY Q DXxXxXxXxX  CQDXCQDXCQDXCQDX")

@client.command(trigger="cqdx")
async def command(command: str, message: discord.Message):
	# Awesome stuff happens here!
	await message.channel.send("https://www.youtube.com/watch?v=5_bHuCwKmkI")
	return
