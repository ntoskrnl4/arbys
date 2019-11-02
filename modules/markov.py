from client import client
from datetime import datetime
from modules import __common__
from typing import Tuple

import asyncio
import discord
import markovify


cmd_name = "markov"

client.basic_help(title=cmd_name, desc="creates a message from a markov chain based on previous messages in a channel")

detailed_help = {
	"Usage": f"{client.default_prefix}{cmd_name} [mention] [--charlimit x] [--size y] [--attempts z]",
	"Arguments": "`mention` - (optional) mention or ID of a channel or user to generate markov chain from (not provided = current channel)\n`--charlimit` - (optional) specifies a custom maximum amount of permitted characters (default 1500 - lower values may require more --attempts)\n`--size` - (optional) specifies the size of the markov chain. For text 2 or 3 is most common, for very large sources 4 may work. (default 3)\n`--attempts` - (optional) specifies how many times the markov chain should attempt to generate valid output before giving up (default 25 - higher values have a better chance of succeeding for small sources)\n",
	"Description": "This command reads input from a given source and feeds messages into a markov chain, which is then used to generate a random sentence that is similar to that of the input. Acceptable sources include the current channel (nothing given for `mention` argument), a specific user (that user's mention or preferably ID given for `mention` argument), or a specific channel (that channel's mention or ID given for `mention` argument).",
}
client.long_help(cmd=cmd_name, mapping=detailed_help)

forbidden_channels = [
	473570993072504832
]


async def get_user_markov(user: int, message: discord.Message, size: int, charlimit: int, attempts: int) -> Tuple[int, str]:
	input_messages = [x for x in client._connection._messages if x.author.id == user]
	await asyncio.sleep(0.1)
	input_messages = [x for x in input_messages if getattr(x.guild,'id',-1) == message.guild.id]
	await asyncio.sleep(0.1)
	input_messages = [x for x in input_messages if x.channel.id not in forbidden_channels]
	await asyncio.sleep(0.1)

	# backup code if that's not enough
	if len(input_messages) < 400:
		input_messages = []
		for ch in message.guild.text_channels:
			if ch.id in forbidden_channels:
				continue
			try:
				input_messages.extend([x for x in await ch.history(limit=500).flatten() if x.author.id == user])
			except:
				continue

	input_messages = [x.content for x in input_messages]
	src_string = "\n".join(input_messages)
	model = markovify.NewlineText(src_string, state_size=size)
	await asyncio.sleep(0.1)
	return len(input_messages), model.make_short_sentence(max_chars=charlimit, tries=attempts)


async def get_channel_markov(channel: discord.TextChannel, size: int, charlimit: int, attempts: int) -> Tuple[int, str]:
	try:
		input_messages = await channel.history(limit=3000).flatten()
	except discord.Forbidden:
		return None, None  # we can't read the channel so this is noootttt going to work at all

	input_messages = [x.content for x in input_messages]
	src_string = "\n".join(input_messages)
	model = markovify.NewlineText(src_string, state_size=size)
	return len(input_messages), model.make_short_sentence(max_chars=charlimit, tries=attempts)


@client.command(trigger=cmd_name)
async def command(parts: str, message: discord.Message):
	parts = parts.split(" ")

	response = discord.Embed()

	# get all optional arguments and check them
	try:
		charlimit = parts.pop(parts.index("--charlimit")+1)
		parts.pop(parts.index("--charlimit"))
	except IndexError:
		response.colour = 0xb81209
		response.title = "Markov function error"
		response.description = "Argument error: No number provided after --charlimit argument"
		response.set_footer(text=datetime.utcnow().__str__())
		await message.channel.send(embed=response)
		return
	except ValueError:
		charlimit = 2000

	try:
		attempts = parts.pop(parts.index("--attempts")+1)
		parts.pop(parts.index("--attempts"))
	except IndexError:
		response.colour = 0xb81209
		response.title = "Markov function error"
		response.description = "Argument error: No number provided after --attempts argument"
		response.set_footer(text=datetime.utcnow().__str__())
		await message.channel.send(embed=response)
		return
	except ValueError:
		attempts = 50

	try:
		size = parts.pop(parts.index("--size")+1)
		parts.pop(parts.index("--size"))
	except IndexError:
		response.colour = 0xb81209
		response.title = "Markov function error"
		response.description = "Argument error: No number provided after --size argument"
		response.set_footer(text=datetime.utcnow().__str__())
		await message.channel.send(embed=response)
		return
	except ValueError:
		size = 3

	try:
		charlimit = int(charlimit)
	except ValueError:
		response.colour = 0xb81209
		response.title = "Markov function error"
		response.description = "Argument error: Invalid number passed as --charlimit argument"
		response.set_footer(text=datetime.utcnow().__str__())
		await message.channel.send(embed=response)
		return

	try:
		attempts = int(attempts)
	except ValueError:
		response.colour = 0xb81209
		response.title = "Markov function error"
		response.description = "Argument error: Invalid number passed as --attempts argument"
		response.set_footer(text=datetime.utcnow().__str__())
		await message.channel.send(embed=response)
		return

	try:
		size = int(size)
	except ValueError:
		response.colour = 0xb81209
		response.title = "Markov function error"
		response.description = "Argument error: Invalid number passed as --size argument"
		response.set_footer(text=datetime.utcnow().__str__())
		await message.channel.send(embed=response)
		return

	# determine our target.
	target = None
	target_type = "unknown"
	# check for nothing
	if len(parts) is 1:
		target = message.channel
		target_type = "channel"

	if len(parts) > 1:

		# get channel if it is one
		c = client.get_channel(__common__.strip_to_id(parts[1]))
		if c is not None:
			target = c
			target_type = "channel"

		u = client.get_user(__common__.strip_to_id(parts[1]))
		if u is not None:
			target = u
			target_type = "user"

	if target_type == "unknown":
		response.colour = 0xb81209
		response.title = f"Markov function failed"
		response.description = "Error running markov function: Unknown object specified"
		response.set_footer(text=f"{datetime.utcnow().__str__()} | Markov run by @{message.author.display_name}")
		await message.channel.send(embed=response)

	# run different outputs for different input types
	if target_type == "user":
		async with message.channel.typing():
			target_member = message.guild.get_member(target.id)
			if target_member is not None:
				display_target = f"{target_member.display_name}"
			else:
				display_target = f"{target.name}#{target.discriminator}"

			try:
				count, result = await get_user_markov(target.id, message, size, charlimit, attempts)
			except KeyError:
				await message.channel.send(f"{message.author.mention} The user you have specified has had no recent messages. This function only works on users who have been active recently.")
				return

			if result is None:
				response.colour = 0xb81209
				response.title = "Markov function failed"
				response.description = "Unable to run markov chain - try running the command again"
				response.set_author(name=display_target, icon_url=target.avatar_url_as(format="png", size=128))
				response.set_footer(text=f"{datetime.utcnow().__str__()} | Markov run by @{message.author.display_name} | {count} messages in input")
				await message.channel.send(embed=response)
				return

			response.colour = 0x243b61
			response.description = result
			response.set_author(name=display_target, icon_url=target.avatar_url_as(format="png", size=128))
			response.set_footer(text=f"{datetime.utcnow().__str__()} | Markov run by @{message.author.display_name} | {count} messages in input")
		await message.channel.send(embed=response)
		return

	if target_type == "channel":
		async with message.channel.typing():
			count, result = await get_channel_markov(target, size, charlimit, attempts)

			if count is None:  # permissions error
				response.colour = 0xb81209
				response.title = "Markov chain failed"
				response.description = "Unable to run markov chain: Insufficient permissions to read channel history"
				response.set_footer(text=f"{datetime.utcnow().__str__()} | Markov run by @{message.author.display_name}")
				response.set_author(name=f"#{target.name}")
				# if we can't read the channel we should check if we can write to it also
				try:
					await message.channel.send(embed=response)
				except discord.Forbidden:
					pass

			if result is None:
				response.colour = 0xb81209
				response.title = "Markov function failed"
				response.description = "Unable to run markov chain - try running the command again"
				response.set_footer(text=f"{datetime.utcnow().__str__()} | Markov run by @{message.author.display_name} | {count} messages in input")
				response.set_author(name=f"#{target.name}")
				await message.channel.send(embed=response)
				return

			response.colour = 0x243b61
			response.description = result
			response.set_footer(text=f"{datetime.utcnow().__str__()} | Markov run by @{message.author.display_name} | {count} messages in input")
			response.set_author(name=f"#{target.name}")
		await message.channel.send(embed=response)
		return
	return
