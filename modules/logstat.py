from client import client
from collections import Counter
from modules import __common__
from typing import List, Dict, Union

import asyncio
import datetime
import discord
import log
import os
import re  # wish me luck
import time

try:
	from matplotlib import pyplot as plot
except ImportError:
	use_mpl = False
else:
	use_mpl = True

detailed_help = {
	"Usage": f"{client.default_prefix}logstat <days> <stat> [count]",
	"Arguments": "`days` - days to look back in logs\n`stat` - statistic to view. \"users\" or \"channels\"\n`count` (Optional) - how many to show in scoreboard (ignored if viewing channels)",
	"Description": "This command looks through all logs in the bot and shows a record of the top users and channels in a server. This requires the bot to be actually logging messages. This command may take a very long time to run, depending on the number of log messages.",
	"Related Commands": f"`{client.default_prefix}stats` - show running statistics for the bot",
}

client.long_help(cmd="logstat", mapping=detailed_help)

re_ts = re.compile(r"^\[2018-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{6}\] ")
re_lvl = re.compile(r" \[[DMIWECF]\] ")
re_server_raw = re.compile(r" \[[^(\[\]#).]+ - \d+\] ")  # this should work ...?
re_channel_raw = re.compile(r" \[#[a-z0-9_-]+ - \d{18}\] ")  # this was SOOOO MUCH EASIER thankfully (thanks Discord!)
re_msg_id = re.compile(r"\[message id: \d{18}\]")
re_user_raw = re.compile(r"\[[\w'-]+#\d{4} - \d+\]")


def get_channel_name(id, message) -> str:
	c = message.guild.get_channel(id)
	if c is None:
		return "Unknown channel"
	else:
		return f"#{c.name}"


async def get_human_id(id, message) -> str:
	m = message.guild.get_member(id)
	if m is not None:
		return f"@{m.name} ({m.display_name if m.display_name != m.name else ''})"
	else:
		m = await client.get_user_info(id)
		return f"@{m.name}#{m.discriminator}"


def match_loglevel(string) -> Union[str, None]:
	try:
		return re_lvl.search(string).group()[2]
	except AttributeError:
		return None


def match_server_name(string) -> Union[str, None]:
	try:
		return re_server_raw.search(string).group()[2:][:-23]
	except AttributeError:
		return None


def match_server_id(string) -> Union[int, None]:
	try:
		return int(re_server_raw.search(string).group()[-20:-2])
	except AttributeError:
		return None


def match_channel_id(string) -> Union[int, None]:
	try:
		return int(re_channel_raw.search(string).group()[-20:-2])
	except AttributeError:
		return None


def match_message_id(string) -> Union[int, None]:
	try:
		return int(re_msg_id.search(string).group()[-19:-1])
	except AttributeError:
		return None


def match_user_id(string) -> Union[int, None]:
	try:
		return int(re_user_raw.search(string).group()[-19:-1])
	except AttributeError:
		return None


@client.command(trigger="logstat")
async def logstat(command: str, message: discord.Message):
	global use_mpl
	if not __common__.check_permission(message.author):
		await message.add_reaction("❌")
		return

	profiling = "--profile" in message.content

	async with message.channel.typing():

		start = time.perf_counter()
		if "--test" not in message.content:
			target_guild = message.guild.id
			logfiles = [x for x in os.listdir("logs/")]  # list of all log files
			all_log_lines = []  # get every single line from those files
			for f in logfiles:
				with open("logs/"+f, "r", encoding="utf-8") as file:
					all_log_lines.extend(file.readlines())
					await asyncio.sleep(0.1)
		else:
			target_guild = 364480908528451584
			logfiles = [x for x in os.listdir("logstat_control_logs/")]  # list of all log files
			all_log_lines = []  # get every single line from those files
			for f in logfiles:
				with open("logs/"+f, "r", encoding="utf-8") as file:
					all_log_lines.extend(file.readlines())
		end = time.perf_counter()
		if profiling:
			await message.channel.send(f"profiling: Processing time to load all log lines was {(end-start)*1000:.4f} ms")

		parsed_logs: List[Dict] = []

		# we'll now loop through all the lines and parse them into dicts
		start = time.perf_counter()
		i = 0
		for line in all_log_lines:
			new_entry = {}

			try:
				new_entry["ts"] = datetime.datetime.strptime(line[:29], "[%Y-%m-%d %H:%M:%S.%f] ")
			except:
				continue  # if there's no timestamp, just move on

			line_lvl = match_loglevel(line)
			if line_lvl:
				new_entry["lvl"] = line_lvl
			else:
				continue  # all lines we're interested in looking at should have a loglevel on them anyways

			line_server_id = match_server_id(line)
			if line_server_id:
				new_entry["server_id"] = line_server_id
			else:
				continue

			line_channel_id = match_channel_id(line)
			if line_channel_id:
				new_entry["channel_id"] = line_channel_id
			else:
				continue

			line_message_id = match_message_id(line)
			if line_message_id:
				new_entry["message_id"] = line_message_id
			else:
				continue

			line_user_id = match_user_id(line)
			if line_user_id:
				new_entry["user_id"] = line_user_id
			else:
				continue

			# finally, we can add our parsed line into the list
			parsed_logs.append(new_entry)

			i += 1
			if i % 10000 is 0:
				await asyncio.sleep(0.01)

		# i = 0
		# split_workload = []
		# while True:
		# 	if i > 1000:
		# 		raise RecursionError("infinite loop ran away, abandoning operation (more than 75 000 000 log lines?!)")
		# 	split_workload.append(all_log_lines[(i*75000):((i+1)*75000)])
		# 	if not all_log_lines[(i * 75000):((i + 1) * 75000)]:
		# 		break
		# 	i += 1
		#
		# pool_event_loop = asyncio.new_event_loop()
		# with ProcessPoolExecutor() as pool:
		# 	results = [await pool_event_loop.run_in_executor(pool, parse_lines, workload) for workload in split_workload]
		# pool_event_loop.stop()
		# pool_event_loop.close()
		#
		# for x in results:
		# 	parsed_logs.extend(x)

		end = time.perf_counter()
		if profiling:
			await message.channel.send(f"profiling: Processing time to parse all log lines: {(end-start)*1000:.4f} ms ({((end-start)*1_000_000)/len(all_log_lines):.3f} us/line)")

		# now we can actually see what our user wants of us
		# args: logstat 30(days) users 25(top X)
		# first we need to check if there's enough arguments
		parts = command.split(" ")

		# check if they want textual format
		try:
			parts.pop(parts.index("--text"))
			use_mpl = False
		except ValueError:
			use_mpl = True if use_mpl else False

		if len(parts) < 3:
			await message.channel.send("Not enough arguments provided to command. See help for help.")
			return
		try:
			limit = datetime.datetime.utcnow()-datetime.timedelta(days=int(parts[1]))
		except ValueError:
			await message.channel.send("First argument to command `logstat` must be number of days behind log to check, as an int")
			return

		await asyncio.sleep(0.1)

		# now we'll filter by time and server
		# list comprehensions are used here because in testing they showed to be about 8x faster than filter()
		snipped_logs = [x for x in parsed_logs if (x["ts"] > limit)]
		filtered_logs = [x for x in snipped_logs if x["server_id"] == target_guild]

		if parts[2] in ["users", "user"]:
			# check if need to filter to a channel
			try:
				filter_channel = __common__.stripMentionsToID(parts[4])
			except TypeError:
				# ignore, we're not filtering to a channel
				pass
			except IndexError:
				# ignore, we're not filtering to a channel
				pass
			else:
				filtered_logs = [x for x in filtered_logs if x["channel_id"] == filter_channel]

		if parts[2] in ["channel", "channels"]:
			# check if we need to filter to a user
			try:
				filter_user = __common__.stripMentionsToID(parts[3])
			except TypeError:
				# ignore, we're not filtering to a user
				pass
			except IndexError:
				# ignore, we're not filtering to a user
				pass
			else:
				filtered_logs = [x for x in filtered_logs if x["user_id"] == filter_user]

		record = Counter()
		if parts[2] in ["users", "user"]:
			item = "users"
			try:
				scoreboard = int(parts[3])
			except:  # it's fine
				scoreboard = 25

			n = 0
			for entry in filtered_logs:
				record[entry["user_id"]] += 1
				n += 1
				if n % 5000 is 0:
					await asyncio.sleep(0.1)

			top = record.most_common(scoreboard)

			top_mentions = {await get_human_id(x, message): y for x, y in top}

		elif parts[2] in ["channel", "channels"]:
			item = "channels"
			scoreboard = len(message.guild.text_channels)

			start = time.perf_counter()
			for entry in filtered_logs:
				record[entry["channel_id"]] += 1
			end = time.perf_counter()
			log.debug(f"logstat: Processing time to count all users: {(end-start)*1000:.4f} ms ({((end-start)*1_000_000)/len(filtered_logs):.3f} us/entry)") if profiling else None

			top = record.most_common(scoreboard)
			top_mentions = {get_channel_name(x, message): y for x, y in top if y is not 0}
		elif parts[2] in ["active"]:
			for entry in filtered_logs:
				record[entry["user_id"]] += 1
			await message.channel.send(f"In the past {int(parts[1])} days, there have been {len(record.most_common())} active unique users.")
			return
		else:
			await message.channel.send("Unknown item to get records for. See help for help.")
			return

		if not use_mpl:
			data = ""
			i = 0
			for x, y in top_mentions.items():
				i += 1
				data += f"`{'0' if i < 100 else ''}{'0' if i < 10 else ''}{str(i)}: {'0' if y < 10000 else ''}{'0' if y < 1000 else ''}{'0' if y < 100 else ''}{'0' if y < 10 else ''}{str(y)} messages:` {x}\n"
			embed = discord.Embed(title=f"Logfile statistics for past {int(parts[1])} days", description=f"Here are the top {scoreboard} {item} in this server, sorted by number of messages.\nTotal messages: {len(record)}\n"+data)
			try:
				await message.channel.send(embed=embed)
			except:
				await message.channel.send("Looks like that information was too long to post, sorry. It's been dumped to the log instead.")
				log.info(f"logstat command could not be output back (too many items). here's the data:\n{data}")

		if use_mpl:
			plot.rcdefaults()
			plot.rcParams.update({'figure.autolayout': True})
			figure, ax = plot.subplots()

			ax.barh(range(len(top_mentions)), list(top_mentions.values()), align='center')
			ax.set_xticks(range(len(top_mentions)), list(top_mentions.keys()))
			ax.set_yticks(range(len(top_mentions)))
			ax.set_yticklabels(list(top_mentions.keys()))
			ax.invert_yaxis()
			plot.show()
	return
