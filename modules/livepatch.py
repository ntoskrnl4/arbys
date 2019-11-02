"""Module to assist livepatching in new or updated modules."""

from client import client
from modules import __common__

import discord
import importlib
import modules

# client.basic_help("livepatch",
# 				  "A system of commands to assist in livepatching modules")

detailed_help = {
	"Usage": f"`{client.default_prefix}livepatch <subcommands> []`",
	"Description": "This command is a kit of commands that can load and unload "
		"modules on the fly while a bot is running, and show information about "
		"currently loaded commands. Beware this command can disable itself."
}

client.long_help("livepatch", detailed_help)

permissible_users = [  # list of IDs permitted to use the command
	288438228959363073
]


async def display_commands(command: str, message: discord.Message):
	# Return info about all operational commands
	embed = discord.Embed()
	for name, func in client._command_lookup.items():
		if name in client.alias_lookup.keys():
			continue
		embed = embed.add_field(
					name=f"{name} (ID {id(func)})",
					value=f"{func.__module__}.{func.__name__}",
					inline=False)
	await message.channel.send(embed=embed)


@client.command(trigger="livepatch", aliases=["lp"])
async def main(command: str, message: discord.Message):
	if message.author.id not in permissible_users:
		await __common__.failure(message)
		return

	parts = command.split(" ")
	# parts: [livepatch, sub1, arg1, arg2]

	if len(parts) == 1:
		await message.channel.send("Argument error: Not enough arguments provided")
		return

	if parts[1] == "commands":
		await display_commands(command, message)
		return

	if parts[1] == "load":
		if len(parts) == 2:
			await message.channel.send("Argument error: Please specify module to load")
			return
		importlib.invalidate_caches()
		importlib.reload(modules)
		exec(f"modules.{parts[2]} = importlib.import_module('modules.{parts[2]}')")
		await __common__.confirm(message)
		return

	if parts[1] == "reload":
		if len(parts) == 2:
			await message.channel.send("Argument error: Please specify module to reload")
			return
		importlib.invalidate_caches()
		importlib.reload(modules)
		importlib.reload(eval("modules." + parts[2]))
		await __common__.confirm(message)
		return
	
	if parts[1] == "unload":
		if len(parts) == 2:
			await message.channel.send("Argument error: Please specify module to unload")
			return
		# Correct for framework version 0.6
		# As of 0.7 these remove the leading underscore
		client_lists = [
			# a list of all handlers the bot has
			client._background_tasks,
			client._ready_handlers,
			client._shutdown_handlers,
			client._message_handlers,
			client._member_join_handlers,
			client._member_remove_handlers,
			client._reaction_add_handlers,
			client._reaction_remove_handlers,
		]
		for list in client_lists:
			list = [x for x in list if x.__module__ != parts[2]]
		
		client._command_lookup = {
			x: y
			for x, y in client._command_lookup.items()
			if y.__module__ != parts[2]
		}
		
		# todo: remove basic/long help when a module is removed. Currently it
		#  doesn't have any attributes defining what it's from. This could also
		#  be a feature to add for the help itself (what module it's from)
		await __common__.confirm(message)
		return
