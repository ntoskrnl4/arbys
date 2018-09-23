from client import client
import discord
import random

client.basic_help(title="59", desc="Returns a picture showing 59 signal reception")

fivenine = ["https://cdn.discordapp.com/attachments/377206780700393473/409899331584524308/20180204_213324.jpg",
"https://cdn.discordapp.com/attachments/364489866119217153/412786093327384577/image.jpg",
"https://cdn.discordapp.com/attachments/364489866119217153/412784280809242624/image.jpg",
"https://cdn.discordapp.com/attachments/377206780700393473/414858156741754880/20180218_135538.jpg",
"https://cdn.discordapp.com/attachments/377206780700393473/416371229428285467/20180222_180823.jpg",
"https://cdn.discordapp.com/attachments/364489910759063552/440596315315896331/IMG_20180428_183441.jpg",
]

@client.command(trigger="59", aliases=["fivenine"])
async def command(command: str, message: discord.Message):
	e = discord.Embed(title=discord.Embed.Empty, description=discord.Embed.Empty, colour=discord.Embed.Empty)
	e = e.set_image(url=random.choice(fivenine))
	await message.channel.send(embed=e)
	return
