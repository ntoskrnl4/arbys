from client import client
from modules import __common__
from typing import List, Union

import discord


primary_channels: List[int] = [
	364488710995050496,  # general
]

ham_radio_channels: List[int] = [
	364489754839875586,  # general-ham
	376859556858298378,  # weekly-net
	364489808674029578,  # help-and-questions
	364489783059152896,  # qsos-and-contesting
	364489910759063552,  # equipment
	427917747838779393,  # ham-voice-text
]

other_channels: List[int] = [
	421832212120338442,  # college
	427925486908473344,  # dev
	403544637320593408,  # memes
	377206780700393473,  # bot
]

public_voice_channels: List[int] = [
	422047295941640212,  # ham-voice
]

yarc_role = client.get_guild(364480908528451584).get_role(425443973700648971)


@client.command(trigger="lock", aliases=["l"])
async def lock(command: str, message: discord.Message):
	if message.guild.id != 364480908528451584:
		if message.guild.id != 452274699641159683:
			# wrong guild
			await message.channel.send("Invalid server")
			return
	else:
		if 639519325287350272 not in [x.id for x in message.author.roles]:
			# user is not a mod
			await message.add_reaction("❌")
			return

	parts = command.split(" ")
	# parts = ['lock', arg1]

	# Define it so we can use typing without cluttering it up later
	target: Union[discord.TextChannel, discord.VoiceChannel] = None

	if len(parts) == 1:
		if message.author.voice is not None:
			target = message.author.voice.channel
		else:
			target = message.channel
	else:
		target = message.guild.get_channel(parts[1][2:-1])
	if (target.id not in primary_channels + ham_radio_channels + other_channels + public_voice_channels) and \
		(message.guild.id != 452274699641159683):
		await message.add_reaction("❌")
		return

	# Take away the proper write/speak permission
	if isinstance(target, discord.TextChannel):
		await target.set_permissions(target=target.guild.default_role, overwrite=discord.PermissionOverwrite(send_messages=False))
		await message.delete()
		return
	if isinstance(target, discord.VoiceChannel):
		await target.set_permissions(target=target.guild.default_role, overwrite=discord.PermissionOverwrite(speak=False))
		await message.delete()
		return


@client.command(trigger="unlock", aliases=["ul"])
async def unlock(command: str, message: discord.Message):
	if message.guild.id != 364480908528451584:
		if message.guild.id != 452274699641159683:
			# wrong guild
			await message.channel.send("Invalid server")
			return
	else:
		if 639519325287350272 not in [x.id for x in message.author.roles]:
			# user is not a mod
			await message.add_reaction("❌")
			return

	parts = command.split(" ")
	# parts = ['unlock', arg1]

	# Define it so we can use typing without cluttering it up later
	target: Union[discord.TextChannel, discord.VoiceChannel] = None

	if len(parts) == 1:
		if message.author.voice is not None:
			target = message.author.voice.channel
		else:
			target = message.channel
	else:
		target = message.guild.get_channel(__common__.stripMentionsToID(parts[1]))
	if (target.id not in primary_channels + ham_radio_channels + other_channels + public_voice_channels) and \
		(message.guild.id != 452274699641159683):
		await message.add_reaction("❌")
		return

	# Set the proper write/speak permission
	if isinstance(target, discord.TextChannel):
		await target.set_permissions(target=target.guild.default_role, overwrite=discord.PermissionOverwrite(send_messages=True))
		await message.delete()
		return
	if isinstance(target, discord.VoiceChannel):
		await target.set_permissions(target=target.guild.default_role, overwrite=discord.PermissionOverwrite(speak=True))
		await message.delete()
		return


@client.command(trigger="purge", aliases=["nuke"])
async def nuke_old_chat(command: str, message: discord.Message):
	if message.guild.id != 364480908528451584:
		if message.guild.id != 452274699641159683:
			# wrong guild
			await message.channel.send("Invalid server")
			return
	else:
		if 639519325287350272 not in [x.id for x in message.author.roles]:
			# user is not a mod
			await message.add_reaction("❌")
			return

	parts = command.split(" ")
	if len(parts) == 1:
		count = 25
	else:
		count = int(parts[1])

	target_msgs = await message.channel.history(limit=count).flatten()
	assert isinstance(message.channel, discord.TextChannel)
	assert isinstance(message.guild, discord.Guild)
	await message.channel.delete_messages(target_msgs)
	return

