"""Due to a quirk of Discord we hve to reset the 'Playing...' status every once in a while."""

from client import client

import discord
import datetime
import log

if client.__version__ == "0.7":
	# todo: v0.7 - update references
	raise RuntimeError("TODO: Update references")


@client.background(period=600)
async def game_resetter():
	await client.change_presence(activity=discord.Game(name="cqdx help"))
