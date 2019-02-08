from client import client

import asyncio
import datetime
import discord
import subprocess


@client.command(trigger="ntp", aliases=["ntpq"])
async def get_ntp_stats(command: str, message: discord.Message):
	try:
		sub = subprocess.Popen(["ntpq", "-c", "rv"], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
		await asyncio.sleep(0.1)
		stdout, stderr = sub.communicate(timeout=0.1)
	except subprocess.TimeoutExpired:
		sub.kill()
		alt = True
	except:
		alt = True
	else:
		alt = False

		# make this into a decently easily parsed list
		parts = stdout.decode().replace("\n", "").replace(" ", "").split(",")

		sync_status = [x for x in parts if x.startswith("sync_")][0]
		stratum = int([x for x in parts if x.startswith("stratum=")][0][8:])
		refid = [x for x in parts if x.startswith("refid=")][0][6:]  # this mess just gets the refid
		offset = float([x for x in parts if x.startswith("offset=")][0][7:])*1000
		freq = float([x for x in parts if x.startswith("frequency=")][0][10:])
		jitter = float([x for x in parts if x.startswith("sys_jitter=")][0][11:])*1000

	embed = discord.Embed(title="NTP Statistics",
						description="Current NTP statistics for the local machine")
	if alt:
		embed.description = embed.description + "\n\nUnknown error while getting statistics."

	if not alt:
		embed = embed.add_field(name="Sync Status", value=sync_status)
		embed = embed.add_field(name="System Peer RefID", value=refid)
		embed = embed.add_field(name="System Stratum", value=stratum)
		embed = embed.add_field(name="Offset", value=f"{offset} us")
		embed = embed.add_field(name="Jitter", value=f"{jitter} us")
		embed = embed.add_field(name="Frequency Drift", value=f"{freq} ppm")

	embed = embed.set_footer(text=datetime.datetime.utcnow().__str__())
	await message.channel.send(embed=embed)