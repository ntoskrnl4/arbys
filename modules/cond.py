from client import client
from io import BytesIO
import requests
import discord
import time


cmd_name = "cond"

client.basic_help(title=cmd_name, desc="Shows current band conditions.")

detailed_help = {
	"Usage": f"{client.default_prefix}{cmd_name}",
	"Description": "This command shows the latest Amateur HF band conditions. This should not be relied upon like a bible; it is purely calculated and is not a measure of actual current HF conditions.",
}
client.long_help(cmd=cmd_name, mapping=detailed_help)

last_cond_update = 0
cond_cache_time = 7200

last_file = None

@client.command(trigger=cmd_name)
async def command(command: str, message: discord.Message):
	await message.channel.send("just turn on your radio and try for yourself because the image was never accurate and shouldn't've even been relied on a single bit <:galen_irl:466725951133450242>")
	return


	global cond_cache_time, last_cond_update, last_file
	if command == "update":
		last_cond_update = 1
	if (time.time() - last_cond_update) >= cond_cache_time:
		req = requests.get("http://www.hamqsl.com/solar101vhf.php")
		data = b""
		for block in req.iter_content(16384):
			data += block
		last_cond_update = time.time()
		await message.channel.send(file=discord.File(BytesIO(data), filename=f"{int(last_cond_update)}.gif"))
		last_file = data
	else:
		await message.channel.send(f"Using cached image from {int(time.time()-last_cond_update)} seconds ago ({int((time.time()-last_cond_update)/60)} minutes ago)")
		await message.channel.send(file=discord.File(last_file, filename=f"{int(last_cond_update)}.gif"))
	return
