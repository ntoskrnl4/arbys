from client import client
import datetime
import discord
import modules
import time
import log


@client.command(trigger="_exec", aliases=[])
async def command(command: str, message: discord.Message):
	if message.author.id != 288438228959363073:
		try:
			await message.add_reaction("❌")
		finally:
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
				exec(f"global {parts[1]}")
				await message.channel.send(f"`{parts[1]} = {eval(parts[1])}`")
			except NameError:
				await message.channel.send(f"`NameError: name {parts[1]} is not defined`")
				return
		else:
			exec(f"global {parts[1]}")
			exec(f"{parts[1]} = {parts[2]}", locals(), globals())
			exec(f"global {parts[1]}")
			await message.channel.send(f"Updated `{parts[1]}`: `{eval(parts[1])}`")
			await message.add_reaction("✅")
			return
	return
