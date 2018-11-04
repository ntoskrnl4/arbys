from client import client
import discord


@client.message()
async def nou(message: discord.Message):
	if message.content.lower().endswith("arbys shut down"):
		try:
			await message.channel.send("no u")
		except:  # that's fine, we don't care
			pass