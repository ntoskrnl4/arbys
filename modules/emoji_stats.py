from collections import Counter
from client import client
import discord
import re

stats = Counter()

@client.reaction_add
async def reaction_use(reaction: discord.Reaction, source):
	if reaction.custom_emoji:
		stats[reaction.emoji.name] += 1

@client.reaction_remove
async def unreact(reaction, source):
	if reaction.custom_emoji:
		stats[reaction.emoji.name] -= 1

@client.message()
async def check_messages(message):
	for emoji_id in [re.search("<:[a-zA-Z0-9_]{2,32}:", x).group()[2:-1] for x in re.findall(r"<:[a-zA-Z0-9_]{2,32}:\d{18}>", message.content)]:
		# List[int] cooresponding to custom emoji IDs
		stats[emoji_id] += 1
