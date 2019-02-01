from client import client

import discord
import prefix


@client.message()
async def ping_reaction(message: discord.Message):
	is_cmd, _ = prefix.check_bot_prefix(message.content, client.prefixes)
	if not is_cmd:
		if (f"<@!{client.user.id}>" in message.content) or (f"<@{client.user.id}>" in message.content):
			try:
				await message.add_reaction(discord.utils.find(lambda x: x.id == 476571656375238657, client.emojis))
			except Exception:  # thats ok, its fine
				return
