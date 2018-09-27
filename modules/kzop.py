from client import client
import datetime
import discord


client.basic_help(title="kzop", desc="returns the time until Caleb/KZ0P's return from his two year leave")

@client.message()
async def info_response(message: discord.Message):
	if any([x in message.content for x in ["<@76770999290306560>", "<@!76770999290306560>"]]):
		try:
			await message.channel.send(f"Hey there {message.author.mention}! You mentioned or pinged cSmith/KZ0P in your message, but he is on a two year long break. To send a message to him, please talk to @ntoskrnl#4435 instead.")
		except:  # we literally don't care
			pass


@client.command(trigger="kzop", aliases=["kz0p", "zop", "caleb"])
async def timer(command: str, message: discord.Message):
	await message.channel.send(str(datetime.datetime(2020, 5, 25)-datetime.datetime.now()))
	return
