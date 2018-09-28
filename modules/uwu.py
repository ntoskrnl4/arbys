from client import client
import discord
import key


@client.message
async def ft8_checker(message: discord.Message):
	if (message.author.id in key.uwu_users) and ("uwu" in message.content.lower()):
		try:
			await message.add_reaction(discord.utils.find(lambda x: x.id == key.uwu_emoji, message.guild.emojis))
		except:  # thats ok, this is only a fun little joke
			pass