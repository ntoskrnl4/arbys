from client import client
import discord
import random

images = [
	"https://cdn.discordapp.com/attachments/377206780700393473/440607748908908544/thiccom.jpg",
]


@client.command(trigger="thiccom")
async def command(command: str, message: discord.Message):
	e = discord.Embed(title=discord.Embed.Empty, description=discord.Embed.Empty, colour=discord.Embed.Empty)
	e = e.set_image(url=random.choice(images))
	await message.channel.send(embed=e)
	return
