import datetime
import discord

import key
import log
import config
import os
import re  # wish me luck

from typing import List, Dict, Union
from collections import Counter
from client import client

detailed_help = {
	"usage": f"{client.default_prefix}logstat [days] [stat] <count>",
	"args": "`days` - days to look back in logs\n`stat` - statistic to view. \"users\" or \"channels\"\n`count` (Optional) - how many to show in scoreboard (ignored if viewing channels)",
	"desc": "This command looks through all logs in the bot and shows a record of the top users and channels in a server. This requires the bot to be actually logging messages. This command may take a very long time to run, depending on the number of log messages.",
	"sub": None,
	"ex": f"`{client.default_prefix}logstat 30 channels`\n`{client.default_prefix} logstat 7 users 25`",
	"perms": "Send Messages",
	"related": f"`{client.default_prefix}stats` - show running statistics for the bot",
}

client.long_help(cmd="logstat", mapping=detailed_help)

re_ts = re.compile(r"^\[2018-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{6}\] ")
re_lvl = re.compile(r" \[[DMIWECF]\] ")
re_server_raw = re.compile(r" \[[^(\[\]#).]+ - \d+\] ")  # this should work ...?
re_channel_raw = re.compile(r" \[#[a-z0-9_-]+ - \d{18}\] ")  # this was SOOOO MUCH EASIER thankfully (thanks Discord!)
re_msg_id = re.compile(r"\[message id: \d{18}\]")
re_user_raw = re.compile(r"\[\w+#\d{4} - \d+\]")


def match_date(string) -> Union[datetime.datetime, None]:
	try:
		return datetime.datetime.strptime(re_ts.search(string).group(), "[%Y-%m-%d %H:%M:%S.%f] ")
	except AttributeError:
		return None


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
	if key.mod_role_id not in [x.id for x in message.author.roles]:
		try:
			await message.add_reaction("❌")
		except:
			pass
		finally:
			return

	async with message.channel.typing():

		logfiles = [x for x in os.listdir("logs/")]  # list of all log files
		all_log_lines = []  # get every single line from those files
		for f in logfiles:
			with open("logs/"+f, "r", encoding="utf-8") as file:
				all_log_lines.extend(file.readlines())

		parsed_logs: List[Dict] = []

		# we'll now loop through all the lines and parse them into dicts
		for line in all_log_lines:
			new_entry = {}

			line_ts = match_date(line)
			if line_ts:
				new_entry["ts"] = line_ts
			else:
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
		# if you've got the above loop collapsed: all lines have been parsed into Dicts with the following properties:
		# ts (datetime), lvl (1char str), server_id, channel_id, message_id, and user_id

		# now we can actually see what our user wants of us
		# args: logstat 30(days) users 25(top X)
		# first we need to check if there's enough arguments
		parts = command.split(" ")
		if len(parts) < 3:
			await message.channel.send("Not enough arguments provided to command. See help for help.")
			return
		try:
			limit = datetime.datetime.utcnow()-datetime.timedelta(days=int(parts[1]))
		except ValueError:
			await message.channel.send("First argument to command `logstat` must be number of days behind log to check, as an int")
			return

		# now we'll trim to only the most recent days
		snipped_logs = [x for x in parsed_logs if (x["ts"] > limit)]
		# and then to what's in this server
		filtered_logs = [x for x in snipped_logs if x["server_id"] == message.guild.id]

		record = Counter()
		if parts[2] in ["users", "user"]:
			item = "users"
			try:
				scoreboard = int(parts[3])
			except:  # it's fine
				scoreboard = 25
			for entry in filtered_logs:
				record[entry["user_id"]] += 1

			top = record.most_common(scoreboard)
			top_mentions = [(getattr(message.guild.get_member(x), "mention", f"<@{x}>"), y) for x, y in top]

		elif parts[2] in ["channel", "channels"]:
			item = "channels"
			scoreboard = len(message.guild.channels)
			for entry in filtered_logs:
				record[entry["channel_id"]] += 1

			top = record.most_common(scoreboard)
			top_mentions = [(getattr(message.guild.get_channel(x), "mention", f"<#{x}>"), y) for x, y in top]
		elif parts[2] in ["active"]:
			for entry in filtered_logs:
				record[entry["user_id"]] += 1
			await message.channel.send(f"In the past {int(parts[1])} days, there have been {len(record.most_common())} active unique users.")
			return
		else:
			await message.channel.send("Unknown item to get records for. See help for help.")
			return

		data = ""
		i = 0
		for x, y in top_mentions:
			i += 1
			data += f"`{str(i).rjust(3)}: {str(y).rjust(5)} messages:` {x}"
		embed = discord.Embed(title=f"Logfile statistics for past {int(parts[1])} days", description=f"Here are the top {scoreboard} {item} in this server, sorted by number of messages.\n"+data)
		try:
			await message.channel.send(embed=embed)
		except:
			await message.channel.send("Looks like that information was too long to post, sorry. It's been dumped to the log instead.")
			log.info(f"logstat command could not be output back (too many items). here's the data:\n{data}")

	return
