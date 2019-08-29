from client import client
from typing import List, Union

import discord

standard_channels: List[int] = [
	364488710995050496,  # general
	508720528035676167,  # general-voice-text
	364489754839875586,  # general-ham
	376859556858298378,  # weekly-net
	364489783059152896,  # qsos-and-contesting
	364489910759063552,  # equipment
	364489808674029578,  # new-hams
	427917747838779393,  # ham-voice-text
	421832212120338442,  # college
	427925486908473344,  # dev
	403544637320593408,  # memes
	377206780700393473,  # bot
	526499196262678548,  # other-radio
]

yarc_channels: List[int] = [
	425443572720861205,  # general-yarc
	513094354005393428,  # yarc-voice-text
]

standard_voice: List[int] = [
	508127065053331456,  # general-voice
	422047295941640212,  # ham-voice
]

yarc_voice: List[int] = [
	425443651527770123,  # yarc-voice
]

yarc_role = client.get_guild(364480908528451584).get_role(425443973700648971)


@client.command(trigger="lock", aliases=["l"])
async def lock(command: str, message: discord.Message):
	if 377540982478209024 not in [x.id for x in message.author.roles]:
		# user is not a mod
		await message.channel.send(client.unknown_command)
		return

	if message.guild.id != 364480908528451584:
		# wrong guild
		await message.channel.send(client.unknown_command)
		return

	parts = command.split(" ")
	# parts = ['lock', arg1]

	# Define it so we can use typing without cluttering it up later
	target: Union[discord.TextChannel, discord.VoiceChannel] = None

	if len(parts) == 1:
		if message.author.voice.channel is not None:
			target = message.author.voice.channel
		else:
			target = message.channel
	else:
		target = message.guild.get_channel(parts[1][2:-1])
	if target.id not in standard_channels + yarc_channels + standard_voice + yarc_voice:
		await message.add_reaction("❌")
		return

	# Take away the proper write/speak permission
	if target.id in standard_channels:
		await target.set_permissions(target=target.guild.default_role, send_messages=False)
		await message.delete()
		return
	if target.id in yarc_channels:
		await target.set_permissions(target=yarc_role, send_messages=False)
		await message.delete()
		return
	if target.id in standard_voice:
		await target.set_permissions(target=target.guild.default_role, speak=False)
		await message.delete()
		return
	if target.id in yarc_voice:
		await target.set_permissions(target=yarc_role, speak=False)
		await message.delete()
		return


@client.command(trigger="unlock", aliases=["ul"])
async def lock(command: str, message: discord.Message):
	if 377540982478209024 not in [x.id for x in message.author.roles]:
		# user is not a mod
		await message.channel.send(client.unknown_command)
		return

	if message.guild.id != 364480908528451584:
		# wrong guild
		await message.channel.send(client.unknown_command)
		return

	parts = command.split(" ")
	# parts = ['lock', arg1]

	# Define it so we can use typing without cluttering it up later
	target: Union[discord.TextChannel, discord.VoiceChannel] = None

	if len(parts) == 1:
		if message.author.voice.channel is not None:
			target = message.author.voice.channel
		else:
			target = message.channel
	else:
		target = message.guild.get_channel(parts[1][2:-1])
	if target.id not in standard_channels + yarc_channels + standard_voice + yarc_voice:
		await message.add_reaction("❌")
		return

	# Take away the proper write/speak permission
	if target.id in standard_channels:
		await target.set_permissions(target=target.guild.default_role, send_messages=True)
		await message.delete()
		return
	if target.id in yarc_channels:
		await target.set_permissions(target=yarc_role, send_messages=True)
		await message.delete()
		return
	if target.id in standard_voice:
		await target.set_permissions(target=target.guild.default_role, speak=True)
		await message.delete()
		return
	if target.id in yarc_voice:
		await target.set_permissions(target=yarc_role, speak=True)
		await message.delete()
		return
