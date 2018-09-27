from client import client
import discord
import random

images = [
	"https://cdn.discordapp.com/attachments/399714898080169995/475819387283046400/20180805_105230.jpg",
	"https://cdn.discordapp.com/attachments/399714898080169995/475819387723710484/20180805_131915.jpg",
	"https://cdn.discordapp.com/attachments/399714898080169995/475819387723710485/20180805_112054.jpg",
]


@client.command(trigger="thiccseal")
async def command(command: str, message: discord.Message):
	e = discord.Embed(title=discord.Embed.Empty, description=discord.Embed.Empty, colour=discord.Embed.Empty)
	e = e.set_image(url=random.choice(images))
	await message.channel.send(embed=e)
	return
