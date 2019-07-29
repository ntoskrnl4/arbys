import datetime
import discord

from collections import defaultdict
from client import client


ping_record: defaultdict = defaultdict(list)


def flush_record():
	global ping_record
	for user, record in ping_record.items():
		for item in record:
			if (datetime.datetime.utcnow() - item[1]) > datetime.timedelta(minutes=1):
				record.pop(record.index(item))
		ping_record[user] = record  # *Modifying* a dict while iterating over it is okay


async def kick_user(message: discord.Message):
	try:
		await message.author.kick()
	except:
		# await client.get_channel(473570993072504832).send(f"Failed kicking user for ping spam: {message.channel.mention}")
		pass
	else:
		# await client.get_channel(473570993072504832).send(f"Automatically kicked user for ping spam (in {message.channel.mention}):"
		# 											f"{message.author.name}#{message.author.discriminator} (ID {message.author.id})")
		await message.author.send("Heya, you were spamming pings a bit much, and so you've been automatically kicked in case "
							"you're a spambot.\nIf you're not a spambot, sorry about that! Please accept our apologies "
							"and rejoin the server (the link can be found on our website, yarc.world).\nWhen you rejoin,"
							" wait a few minutes before sending another ping (so you don't get kicked again) and be "
							"careful not to spam pings in the future.\nFor reference, I take note when you spam too many"
							" individual people (8+ in 1m), or when you spam too many pings total (30+ in 1m).")


@client.message(receive_self=False)
async def check_ping_spam(message: discord.Message):
	flush_record()

	if not message.guild:
		return

	if message.author.bot:
		return

	if message.guild.id != 364480908528451584:
		return

	if 377540982478209024 in [x.id for x in message.author.roles]:
		return

	for ping in message.raw_mentions:
		ping_record[message.author.id].append((ping, datetime.datetime.utcnow()))

	if len(ping_record[message.author.id]) >= 30:
		await kick_user(message)  # Kick if 30+ pings in last 1m

	if len(set([x[0] for x in ping_record[message.author.id]])) >= 8:
		await kick_user(message)  # Kick if 8+ different users pinged in last 1m
