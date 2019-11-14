from client import client
from datetime import datetime

import discord
import requests


#client.basic_help(title="call", desc="Looks up a callsign from the callook.info database.")

detailed_help = {
	"Usage": f"{client.default_prefix}call <callsign>",
	"Arguments": "`<callsign>` - the callsign to look up",
	"Description": "This command is a reimplementation of HamTheMan's `htm call` command. It retrieves information about a specified callsign and returns some info about it. This command exists in here because Ben doesn't know how to keep a bot online :P",
	# NO Aliases field, this will be added automatically!
}
#client.long_help(cmd="call", mapping=detailed_help)


@client.command(trigger="call")
async def call(command: str, message: discord.Message):

	await message.channel.send("This command is deprecated. Please use `htm call` instead.")
	return
	

	# try:
	# 	requested_call = command.split(" ", 1)[1].lower()
	# except TypeError:
	# 	await message.channel.send("Argument error: Callsign argument not given")
	# 	return
	# if requested_call[0] not in ["w", "a", "n", "k"]:
	# 	await message.channel.send(f"Argument error: The underlying API only retrieves information for US calls (prefixes `N`, `K`, `W`, and `AA-AL`).\nFor non-US calls please use HamTheMan instead: `htm call {requested_call}`")
	# 	return
	# if requested_call[0] == "a" and requested_call[1] not in "abcdefghijkl":
	# 	await message.channel.send(f"Argument error: The underlying API only retrieves information for US calls (prefixes `N`, `K`, `W`, and `AA-AL`).\nFor non-US calls please use HamTheMan instead: `htm call {requested_call}`")
	# 	return
	#
	# async with message.channel.typing():
	# 	data = requests.get(f"https://callook.info/{requested_call}/json").json()
	# 	if data["status"] == "INVALID":
	# 		embed = discord.Embed(title=f"Callsign lookup for {requested_call}", description="No such callsign.", colour=0xdb6415)
	# 		embed = embed.set_footer(text=f"Lookup requested by @{message.author.name}#{message.author.discriminator} at {datetime.utcnow().__str__()}")
	# 	if data["status"] == "VALID":
	# 		embed = discord.Embed(title=f"Callsign lookup for {requested_call}", description=discord.Embed.Empty, colour=0x06b206)
	# 		embed = embed.add_field(name="Callsign", value=data["current"]["callsign"])
	# 		if data["type"] == "PERSON":
	# 			embed = embed.add_field(name="Class", value=data["current"]["operClass"])
	# 			embed = embed.add_field(name="Name", value=data["name"])
	# 			embed = embed.add_field(name="Location", value=f"{data['address']['line1']}, {data['address']['line2']}", inline=False)
	# 			embed = embed.add_field(name="Grid Square", value=data["location"]["gridsquare"])
	# 			embed = embed.add_field(name="Lat/Long", value=f"{data['location']['latitude']}, {data['location']['longitude']}")
	# 			embed = embed.add_field(name="License Granted", value=data['otherInfo']['grantDate'])
	# 			embed = embed.add_field(name="License Last Action", value=data['otherInfo']['lastActionDate'])
	# 			embed = embed.add_field(name="License Expires", value=data['otherInfo']['expiryDate'])
	#
	# 		if data["type"] == "CLUB":
	# 			embed = embed.add_field(name="Name", value=data["name"])
	# 			embed = embed.add_field(name="Trustee Name and Callsign", value=f"{data['trustee']['name']} (call: {data['trustee']['callsign']})")
	# 			embed = embed.add_field(name="Location", value=f"{data['address']['line1']}, {data['address']['line2']}", inline=False)
	# 			embed = embed.add_field(name="Grid Square", value=data["location"]["gridsquare"])
	# 			embed = embed.add_field(name="Lat/Long", value=f"{data['location']['latitude']}, {data['location']['longitude']}")
	# 			embed = embed.add_field(name="License Granted", value=data['otherInfo']['grantDate'])
	# 			embed = embed.add_field(name="License Last Action", value=data['otherInfo']['lastActionDate'])
	# 			embed = embed.add_field(name="License Expires", value=data['otherInfo']['expiryDate'])
	#
	# await message.channel.send(embed=embed)
	# return
