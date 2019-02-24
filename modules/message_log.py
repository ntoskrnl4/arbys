from client import client

import discord
import log

do_not_log_channels = [
]

@client.message()
async def log_messages(message: discord.Message):
	if not client.log_all_messages:
		return
	if message.channel.id in do_not_log_channels:
		return

	if not message.attachments:  # no attachments
		try:
			log.msg(
					f"[{message.guild.name} - {message.guild.id}] "
					f"[#{message.channel.name} - {message.channel.id}] "
					f"[message id: {message.id}] "
					f"[{message.author.name}#{message.author.discriminator} - {message.author.id}] "
					f"{message.author.display_name}: {message.system_content}",
					ts=message.created_at)
		except AttributeError:
			log.msg(
					f"[DM] "
					f"[message id: {message.id}] "
					f"[{message.author.name}#{message.author.discriminator} - {message.author.id}] "
					f"{message.system_content}",
					ts=message.created_at)
	else:
		try:
			log.msg(
					f"[{message.guild.name} - {message.guild.id}] "
					f"[#{message.channel.name} - {message.channel.id}] "
					f"[message id: {message.id}] "
					f"[{message.author.name}#{message.author.discriminator} - {message.author.id}] "
					f"{message.author.display_name}: {message.system_content} "
					f"{' '.join([x.url for x in message.attachments])}",
					ts=message.created_at)
		except AttributeError:
			log.msg(
					f"[DM] "
					f"[message id: {message.id}] "
					f"[{message.author.name}#{message.author.discriminator} - {message.author.id}] "
					f"{message.system_content} "
					f"{' '.join([x.url for x in message.attachments])}",
					ts=message.created_at)
