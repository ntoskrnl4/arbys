from prefix import check_prefix
from client import client
import discord

@client.message()
async def ping_reaction(message: discord.Message):
	is_cmd, _ = check_prefix(message.content, client.prefixes)
	if not is_cmd:
		if ("<@!398599948557615130>" in message.content) or ("<@398599948557615130>" in message.content):
			try:
				await message.add_reaction(discord.utils.find(lambda x: x.id == 476571656375238657, client.emojis))
			except Exception:  # thats ok, its fine
				return
