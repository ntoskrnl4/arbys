from client import client
from datetime import datetime

import asyncio
import discord
import subprocess
import time

client.basic_help(title="time", desc="Shows the current time, accounting for delays.")
client.long_help(cmd="time", mapping={
	"Usage": f"`{client.default_prefix}time",
	"Description": "This command shows the current UTC time as per the system clock, synchronized to a GPS receiver.\n"
				"Typical accuracy of the clock is <500ns.\nDelays due to message sending in Discord are accounted "
				"for with two test messages before recording and fudging the current time, and sending it back to you.\n"
				"For further information on the clock synchronization on this machine, run the "
				f"`{client.default_prefix}ntp` command.",
})

last_run = 0


@client.command(trigger="time")
async def show_simple_time(command: str, message: discord.Message):
	global last_run

	if (time.time()-last_run) < 15.0:  # if cooldown,
		await message.add_reaction("❌")  # reject the command
		return
	last_run = time.time()

	test_send_1 = await message.channel.send(".")  # First send a quick test message or 2 so that we "warm up" the pipes
	# test_send_2 = await message.channel.send(".")  # First send a quick test message or 2 so that we "warm up" the pipes

	# Before we start doing any work we'll try to get the system offset, also to give time for ^ to process
	try:
		# Try and run `ntpq -c rv`
		ntpq = subprocess.Popen(["ntpq", "-c", "rv"], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
		# Give it time to process
		await asyncio.sleep(0.1)
		# Get the results
		stdout, stderr = ntpq.communicate(timeout=0.1)
	except subprocess.TimeoutExpired:
		# If it's taking too long just kill it and tell the user the offset is unknown
		ntpq.kill()
		return_offset = "unknown"
	except:
		# If there was some other error (ntpq doesn't exist?) report unknown
		return_offset = "unknown"
	else:
		# If getting the info did work, split the result into parts...
		parts = stdout.decode().split(", ")
		# ..then search for the offset and read that...
		offset = float([x for x in parts if x.startswith("offset=")][0][7:])
		# ..then search for the jitter and read that too.
		jitter = float([x for x in parts if x.startswith("sys_jitter=")][0][11:])

		if abs(offset) < abs(jitter*1.5):
			# If the offset is less than jitter (*1.5 for leeway) report the jitter as the offset
			return_offset = f"<{jitter*1_500_000:.1f}us"
		else:
			# If the offset is more than the jitter just report the offset directly
			return_offset = f"{offset*1_000_000:.2f}us"

	# Send another test message now that stuff's warmed up, this one we'll measure off of.
	test_send_3 = await message.channel.send(".")

	# Record the instant we regain execution after sending a test message
	now = time.time()
	now_dt = datetime.utcfromtimestamp(now)
	# and compute the processing delay in sending a message.
	delay = (now_dt - test_send_3.created_at).total_seconds()

	# We'll grab our time and add in the delay in sending a message, *1.05 to account for jitter and delay below
	now = time.time() + (delay*1.05)
	now = datetime.utcfromtimestamp(now)
	embed = discord.Embed()
	embed = embed.add_field(name=now.__str__()+" UTC",
							value=f"Message send delay measured at `{delay*1000:.2f} ms`\n"
								f"System time synchronization offset is `{return_offset}`")
	embed = embed.set_footer(text="Command now on cooldown for 15 seconds.")
	await message.channel.send(embed=embed)

	# Finally, clean up and remove our test messages.
	# delete_after argument of send() was specifically not used earlier so that it wouldn't interfere with us.
	await test_send_1.delete()
	# await test_send_2.delete()
	await test_send_3.delete()
