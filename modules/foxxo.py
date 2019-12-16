from client import client
from typing import List, Tuple

import discord
import log
import random

if client.is_ready():
	foxxo_channel = client.get_channel(526155899295891456)
	foxxo_channel_cache = []
	
	wolfie_channel = client.get_channel(565247287534682112)
	wolfie_channel_cache = []
	
	doggo_channel = client.get_channel(564533446504873986)
	doggo_channel_cache = []
	
	raccoon_channel = client.get_channel(563314782141153321)
	raccoon_channel_cache = []
else:
	foxxo_channel = None
	foxxo_channel_cache = None
	
	wolfie_channel = None
	wolfie_channel_cache = None
	
	doggo_channel = None
	doggo_channel_cache = None
	
	raccoon_channel = None
	raccoon_channel_cache = None

@client.ready
async def initialize():
	global foxxo_channel, foxxo_channel_cache, wolfie_channel, wolfie_channel_cache, doggo_channel, doggo_channel_cache, raccoon_channel, raccoon_channel_cache
	foxxo_channel = client.get_channel(526155899295891456)
	foxxo_channel_cache = []
	
	wolfie_channel = client.get_channel(565247287534682112)
	wolfie_channel_cache = []
	
	doggo_channel = client.get_channel(564533446504873986)
	doggo_channel_cache = []
	
	raccoon_channel = client.get_channel(563314782141153321)
	raccoon_channel_cache = []


async def get_channel_images(channel: discord.TextChannel) -> List[Tuple[str, int]]:
	"""
	Get all the images from a channel, including URL and their message ID.

	:param channel: The channel to retrieve images from.
	:return: A list of (URL, Message ID) of all images in the channel.
	"""
	global foxxo_channel_cache, doggo_channel_cache, wolfie_channel_cache, raccoon_channel_cache

	images: List[Tuple[str, int]] = []
	if channel == foxxo_channel:
		if not foxxo_channel_cache:
			messages = await channel.history(limit=None).flatten()
			foxxo_channel_cache = messages
		else:
			messages = foxxo_channel_cache

	if channel == doggo_channel:
		if not doggo_channel_cache:
			messages = await channel.history(limit=None).flatten()
			doggo_channel_cache = messages
		else:
			messages = doggo_channel_cache

	if channel == wolfie_channel:
		if not wolfie_channel_cache:
			messages = await channel.history(limit=None).flatten()
			wolfie_channel_cache = messages
		else:
			messages = wolfie_channel_cache

	if channel == raccoon_channel:
		if not raccoon_channel_cache:
			messages = await channel.history(limit=None).flatten()
			raccoon_channel_cache = messages
		else:
			messages = raccoon_channel_cache

	# Get attachments
	for message in messages:
		for attachment in message.attachments:
			images.append((attachment.url, message.id))
	# Get images
	for x in messages:
		if (x.content[-4:] in [".jpg", ".png", "webm", "webp", ".gif", "gifv", ".mp4"]) and \
			(
					x.content.startswith("https://i.redd.it/") or
					x.content.startswith("https://cdn.discordapp.com/"),
					x.content.startswith("https://media.discordapp.net")
			):
			images.append((x.content, x.id))

	# images should now be a List[str] of image URLs we can choose from
	log.debug(f"modules.foxxo.get_channel_images: Got {len(images)} images from #{str(channel)}")
	return images


@client.message()
async def check_cache(message: discord.Message):
	global foxxo_channel_cache, doggo_channel_cache, wolfie_channel_cache, raccoon_channel_cache

	if message.channel == foxxo_channel:
		foxxo_channel_cache.append(message)
	if message.channel == wolfie_channel:
		wolfie_channel_cache.append(message)
	if message.channel == raccoon_channel:
		raccoon_channel_cache.append(message)
	if message.channel == doggo_channel:
		doggo_channel_cache.append(message)


@client.command(trigger="foxxo", aliases=["f", "fox"])
async def get_foxxo(command: str, message: discord.Message):
	await message.channel.trigger_typing()

	images = []
	if len(command.split(" ")) == 1:
		# No argument provided. Default #cute-foxxos
		images.extend(await get_channel_images(foxxo_channel))

	if "--fox" in command or \
		("--foxxo" in command) or \
		("-f" in command):
		images.extend(await get_channel_images(foxxo_channel))

	if "--wolf" in command or \
		("--wuffie" in command) or \
		("--wuffo" in command) or \
		("--wolfie" in command) or \
		("-w" in command):
		images.extend(await get_channel_images(wolfie_channel))

	if "--raccoon" in command or \
		("--coon" in command) or \
		("--racc" in command) or \
		("-r" in command):
		images.extend(await get_channel_images(raccoon_channel))

	if "--dog" in command or \
		("--doggo" in command) or \
		("--doggie" in command) or \
		("-d" in command):
		images.extend(await get_channel_images(doggo_channel))

	if not images:
		await message.channel.send("Invalid argument")
		return
	image_url, image_id = random.choice(images)
	log.debug(f"modules.foxxo.command: Had {len(images)} choices and chose one from Message ID {image_id}")
	embed = discord.Embed()
	embed = embed.set_image(url=image_url)
	embed = embed.set_footer(text=f"Message ID {image_id}")
	await message.channel.send(embed=embed)
