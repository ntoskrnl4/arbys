from client import client
from modules import __common__

import asyncio
import datetime
import discord
import importlib
import log
import modules
import sys
import time



@client.command(trigger="_exec", aliases=[])
async def command(command: str, message: discord.Message):
	if message.author.id != 288438228959363073:
		await __common__.failure(message)
		return
	else:
		pass

	parts = command.split(" ", 2)
	# parts: exec var code
	try:
		parts[1]
	except IndexError:
		# no var provided
		await message.channel.send("No target variable provided")
		return
	else:
		# got a target variable
		try:
			parts[2]
		except IndexError:
			try:
				exec(f"global {parts[1].split('.')[0]}")
				await message.channel.send(f"`{parts[1]} = {eval(parts[1])}`")
			except Exception as e:
				await message.channel.send(f"`{sys.exc_info()[0].__name__}: {str(sys.exc_info()[1])}`")
				return
		else:
			exec(f"global {parts[1]}")
			exec(f"{parts[1]} = {parts[2]}", locals(), globals())
			exec(f"global {parts[1]}")
			await message.channel.send(f"Updated `{parts[1]}`: `{eval(parts[1])}`")
			await __common__.confirm(message)
			return
	return
