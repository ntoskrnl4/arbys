from client import client
import discord
import random


images = ["https://cdn.discordapp.com/attachments/377206780700393473/410544474339541014/Screenshot_at_2018-02-06_15-56-58.png",
"https://cdn.discordapp.com/attachments/348223594825908224/410566584529190922/unknown.png",
"https://cdn.discordapp.com/attachments/348223594825908224/410564139300159499/unknown.png",
"https://cdn.discordapp.com/attachments/348223594825908224/410566403821797376/unknown.png",
]


@client.command(trigger="spaceman")
async def command(command: str, message: discord.Message):
	e = discord.Embed(title=discord.Embed.Empty, description=discord.Embed.Empty, colour=discord.Embed.Empty)
	e = e.set_image(url=random.choice(images))
	await message.channel.send(embed=e)
	return
