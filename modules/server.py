"""Module allowing interaction with the bot from outside of Discord."""

from client import client

import asyncio
import datetime
import discord
import json
import log
import modules
import os
import psutil
import socket
import struct
import time

port = 40934


# Struct cheat sheet
# < - LE
# > - BE					Type		Width	Range
# c - char					bytes[1]	1		[ASCII character]
# b - signed char			int			1		-128 - 127
# B - unsigned char			int			1		0 - 255
# ? - bool					bool		1		True / False
# h - short					int			2		-32768 - 32767
# H - unsigned short		int			2		0 - 65535
# i - int					int			4		-(2^31) - (2^31)-1
# I - unsigned int			int			4		0 - (2^32)-1
# l - long					int			4		-(2^31) - (2^31)-1
# L - unsigned long			int			4		0 - (2^32)-1
# q - long long				int			8		-(2^63) - (2^63)-1
# Q - unsigned long long	int			8		0 - (2^64)-1
# e - half float			float		2		6.1e-05 - 6.5e+04
# f - float					float		4		+/- 3.4e+038
# d - double				float		8		+/- 1.8e+308


async def handle_connection(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
	# first get the other end's info
	try:
		remote_addr, remote_port = writer.get_extra_info("peername")
	except:
		remote_addr, remote_port = "?.?.?.?", -1

	log.info(f"server: New client connected from {remote_addr} on port {remote_port}")

	while not reader.at_eof():
		try:  # we don't want a broken client to kill the entire bot
			next_len, = struct.unpack(">L", await reader.read(4))
			in_data = json.loads(await reader.readexactly(next_len))
			await handle_input(in_data, writer)
		except Exception as e:
			pass


async def handle_input(data, writer: asyncio.StreamWriter):
	format = data.get("type", None)
	if format is None:
		# if the client won't tell us what they're sending why should we even bother
		log.warning(f"server: Broken client sent data without a type. Dropping")
		raise TypeError("Invalid packet (no type given)")

	if format == "ping":
		# Send back a double with ping time in ms
		writer.write(struct.pack(">d", client.latency*1000))
		await writer.drain()
		return

	if format == "status":

		# Send back a whole dict of information
		response = {
			"time": time.time(),
			"active": client.active,
			"uptime": time.perf_counter() - client.first_execution,
			"latency": client.latency * 1000,
			"servers": len(client.guilds),
			"msg_count": client.message_count,
			"cmd_count": client.command_count,
			"cache_len": len(client._connection._messages),
			"pid": os.getpid(),
			"hostname": socket.gethostname(),
			"cpu_temp": psutil.sensors_temperatures()['cpu-thermal'][0].current,
		}

		response = json.dumps(response).encode()
		length = len(response)
		response = struct.pack(">L", length) + response
		writer.write(response)
		await writer.drain()
		return

	if format == "msg_send":

		target_id = data.get("id", None)
		message = data.get("msg", "")
		if target_id is None:
			raise ValueError("No target provided")
		if message == "":
			raise ValueError("No message provided")

		target: discord.User = client.get_user(target_id)
		if target is None:
			target: discord.TextChannel = client.get_channel(target_id)
			if target is None:
				raise LookupError("Unknown recipient")
			assert isinstance(target, discord.TextChannel)
		else:
			assert isinstance(target, discord.User)

		try:
			msg = await target.send(message)
		except discord.Forbidden as exc:
			response = {
				"success": False,
				"error": "Invalid Permissions",
				"description": f"Forbidden: {str(exc)}"
			}
		except discord.HTTPException as exc:
			response = {
				"success": False,
				"error": "Message Send Failure",
				"description": f"HTTPException: {str(exc)}"
			}
		except Exception as exc:
			response = {
				"success": False,
				"error": "Unknown error",
				"description": str(exc)
			}
		else:
			response = {
				"success": True,
				"time": str(msg.created_at),
				"guild": msg.guild.name,
				"channel": msg.channel.name,
			}
		response = json.dumps(response).encode()
		response = struct.pack(">L", len(response)) + response
		writer.write(response)
		await writer.drain()
		return

	if format == "enable":
		client.active = True
		writer.write(struct.pack(">L?", 1, True))
		await writer.drain()
		return

	if format == "disable":
		client.active = False
		writer.write(struct.pack(">L?", 1, True))
		await writer.drain()


asyncio.ensure_future(asyncio.start_server(handle_connection, host="", port=port))
log.info(f"Local server interface started on port {port}")
