from client import client
import discord


@client.message(receive_self=True)
async def nou(message: discord.Message):
	if message.content.lower().endswith("arbys shut down"):
		try:
			await message.channel.send("no u")
		except:  # that's fine, we don't care
			pass


@client.message(receive_self=False)
async def nou_chain(message: discord.Message):
	if message.content.lower() == "no u":
		hist = await message.channel.history(limit=9).flatten()
		if hist[1].author.id == client.user.id:
			await message.channel.send("no u")
