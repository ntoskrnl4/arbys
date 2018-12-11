from client import client
import discord
import log


@client.message()
async def message_checker(message: discord.Message):
	if message.guild.id != 364480908528451584:
		return

	faulty_attachments = []

	# attachment check
	if message.attachments:
		for file in message.attachments:
			if file.filename.endswith(".exe"):
				faulty_attachments.append(file)
			if file.filename.endswith(".sh"):
				faulty_attachments.append(file)
			if file.filename.endswith(".bat"):
				faulty_attachments.append(file)
			if file.filename.endswith(".cmd"):
				faulty_attachments.append(file)
			if file.filename.endswith(".vbs"):
				faulty_attachments.append(file)

		if faulty_attachments:
			try:
				await message.delete()
			except discord.Forbidden:
				log.warning("could not delete message with executable attachments (invalid permissions?)")
				await client.get_channel(473570993072504832).send("Failed to delete message with executable attachment!\n"
												f"Message link: {message.jump_to_url}\n"
												f"Sender: {message.author.name}#{message.author.discriminator}\n"
												f"Channel: {message.channel.mention}\n"
												f"Disallowed attachment filename: {' '.join([x.name for x in faulty_attachments])}\n"
												f"Time: {message.created_at.__str__()}")
				try:
					# if we can't delete the message we should also beware if we can't send a message back either (RO channel)
					await message.channel.send(f"{message.author.mention} Please do not post executable files.")
				except:
					log.warning("could not warn user for posting executable attachments (RO channel?)")
			else:
				log.debug("successfully deleted message with executable attachments")
				await client.get_channel(473570993072504832).send("Successfully deleted message with executable attachment:\n"
												f"Sender: {message.author.name}#{message.author.discriminator}\n"
												f"Channel: {message.channel.mention}\n"
												f"Disallowed attachment filename: {' '.join([x.name for x in faulty_attachments])}\n"
												f"Time: {message.created_at.__str__()}")
				await message.channel.send(f"{message.author.mention} Please do not post executable files.")
