from client import client
import discord
import random

images = ["https://cdn.discordapp.com/attachments/364488710995050496/398597078873407499/vRutZA3.jpg",
"https://vignette.wikia.nocookie.net/uncyclopedia/images/0/0d/Fat_cow.jpg",
"https://i.ytimg.com/vi/J3X-ufvxmdo/hqdefault.jpg",
"http://www.healthwantcare.com/wp-content/uploads/2014/07/cow-600x337.jpg",
]


@client.command(trigger="thiccbeef")
async def command(command: str, message: discord.Message):
	e = discord.Embed(title=discord.Embed.Empty, description=discord.Embed.Empty, colour=discord.Embed.Empty)
	e = e.set_image(url=random.choice(images))
	await message.channel.send(embed=e)
	return
