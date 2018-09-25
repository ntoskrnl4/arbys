from client import client
import discord
import random


images = ["https://cdn.discordapp.com/attachments/384730762852958208/398659159416897537/piggy.png",
"https://cdn.discordapp.com/attachments/384730762852958208/398659602612486144/pig_thm.png",
"https://cdn.discordapp.com/attachments/384730762852958208/398659744954581002/310.png",
"https://cdn.discordapp.com/attachments/384730762852958208/398661546735304705/beef_bot_pig_bacon.png",
"https://cdn.discordapp.com/attachments/384730762852958208/398661976957517824/latest.png",
"https://cdn.discordapp.com/attachments/377206780700393473/398867965426139137/image.jpg",
"https://cdn.discordapp.com/attachments/377206780700393473/398867977639821313/image.jpg",
"https://cdn.discordapp.com/attachments/377206780700393473/398867995096645633/image.jpg",
"https://cdn.discordapp.com/attachments/377206780700393473/398868005867487232/image.jpg",
"https://cdn.discordapp.com/attachments/377206780700393473/398868036205150218/image.jpg",
"https://cdn.discordapp.com/attachments/377206780700393473/398868053850587136/image.jpg",
"https://cdn.discordapp.com/attachments/364489808674029578/494152743309541377/unknown.png",
]

@client.command(trigger="ham",
				aliases=[])  # aliases is a list of strs of other triggers for the command
async def command(command: str, message: discord.Message):
	e = discord.Embed(title=discord.Embed.Empty, description=discord.Embed.Empty, colour=discord.Embed.Empty)
	e = e.set_image(url=random.choice(images))
	await message.channel.send(embed=e)
	return
