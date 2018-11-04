from datetime import datetime, timedelta
from client import client
import discord
import re


ft8_last_sent = {}


@client.message()
async def ft8_checker(message: discord.Message):
	global ft8_last_sent
	try:
		if message.channel.id == 491411457963982848:
			modified = re.sub(r"<:[a-zA-Z0-9_]{2,32}:\d{18}>", "a", message.content)
			modified = re.sub(r"`", "", modified)
			modified = re.sub(r"\(*\)", "", modified)
			modified = re.sub(r"<@!?\d{17,18}>", "123456", modified)
			modified = modified.replace("*", "")
			modified = modified.replace("_", "")
			modified = modified.replace("~", "")
			if ((datetime.utcnow() - timedelta(seconds=15)) < ft8_last_sent.get(message.author.id, datetime(2011, 1, 1, 0, 0, 0))) or len(modified) > 17:
				# violation
				try:
					await message.delete()
				except:
					await message.add_reaction("❌")
			else:
				# message is good
				ft8_last_sent[message.author.id] = datetime.utcnow()
	except:
		pass