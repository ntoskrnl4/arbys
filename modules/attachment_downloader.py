from client import client

import discord
import log
import os
import time

os.makedirs("attachments/", exist_ok=True)


@client.message(receive_self=False)
async def download_attachments(message: discord.Message):
	if not message.attachments:
		# No attachments
		return
	for attachment in message.attachments:
		path = f"attachments/{message.channel.id}_{message.id}_{attachment.filename}"
		with open(f"{path}", "wb") as target_fp:
			write_size = await attachment.save(target_fp)
		if write_size != attachment.size:
			log.warn(f"Downloaded attachment not same size as attachment uploaded")


@client.background(period=86400)
async def clear_old_files():
	files = os.listdir("attachments/")
	for file in files:
		if (time.time() - os.path.getctime("attachments/"+file)) > (7*86400):
			os.remove(f"attachments/{file}")
