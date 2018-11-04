from client import client
import discord
import key


@client.message()
async def ft8_checker(message: discord.Message):
	if (message.guild.id == 364480908528451584) and ("uwu" in message.content.lower().replace(" ", "")):
		try:
			await message.add_reaction(discord.utils.find(lambda x: x.id == key.uwu_emoji, message.guild.emojis))
		except:  # thats ok, this is only a fun little joke
			pass