from client import client
import requests
import discord
import time


cmd_name = "cond"

client.basic_help(title=cmd_name, desc="Shows current band conditions.")

detailed_help = {
	"Usage": f"{client.default_prefix}{cmd_name}",
	"Arguments": "None",
	"Description": "This is what the command does!",
}
client.long_help(cmd=cmd_name, mapping=detailed_help)

last_cond_update = 0
cond_cache_time = 7200


@client.command(trigger=cmd_name)
async def command(command: str, message: discord.Message):
	global cond_cache_time, last_cond_update
	if command == "update":
		last_cond_update = 1
	if (time.time() - last_cond_update) >= cond_cache_time:
		req = requests.get("http://www.hamqsl.com/solar101vhf.php")
		with open("image.gif", "wb+") as tempfile:
			for block in req.iter_content(16384):
				tempfile.write(block)
			last_cond_update = time.time()
		await message.channel.send(file=discord.File("image.gif"))
	else:
		await message.channel.send(f"Using cached image from {int(time.time()-last_cond_update)} seconds ago ({int((time.time()-last_cond_update)/60)} minutes ago)")
		await message.channel.send(file=discord.File("image.gif"))
	return
