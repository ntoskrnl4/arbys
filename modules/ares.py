from client import client
import discord


@client.command(trigger="ares")
async def ares(command: str, message: discord.Message):
	embed = discord.Embed(title=discord.Embed.Empty, description=discord.Embed.Empty, colour=discord.Embed.Empty)
	embed = embed.set_image(url="https://cdn.discordapp.com/attachments/504486947146694668/504487306107944960/lo6bX.png")
	embed = embed.set_footer(text="Command idea credit to @Zarya#6780 (K2RCN)")
	await message.channel.send(embed=embed)
	return
