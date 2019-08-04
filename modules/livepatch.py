"""Module to assist livepatching in new or updated modules."""

from client import client

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


async def handle_info(command: str, message: discord.Message):
	# Return info about all operational commands
	embed = discord.Embed()
	for name, func in client._command_lookup.items():
		if name in client.alias_lookup.keys():
			continue
		embed = embed.add_field(name=f"{name} ({id(func)})", value=discord.Embed.Empty)
	await message.channel.send(embed=embed)


@client.command(trigger="livepatch", aliases=["lp"])
async def main(command: str, message: discord.Message):
	if message.author.id not in permissible_users:
		await message.add_reaction("❌")
		return

	parts: list = command.split(" ")
	# parts: [livepatch, sub1, arg1, arg2]

	if len(parts) == 1:
		await message.channel.send("Argument error: Not enough arguments provided")
		return

	if parts[1] == "info":
		await handle_info(command, message)
		return

	if parts[1] == "load":
		if len(parts) == 2:
			await message.channel.send("Argument error: Please specify module to load")
			return
		importlib.invalidate_caches()
		importlib.reload(modules)
		exec(f"modules.{parts[2]} = importlib.import_module('modules.{parts[2]}')")
		await message.add_reaction("☑")
		return

	if parts[1] == "reload":
		if len(parts) == 2:
			await message.channel.send("Argument error: Please specify module to reload")
			return
		importlib.invalidate_caches()
		importlib.reload(modules)
		importlib.reload(eval("modules." + parts[2]))
		await message.add_reaction("☑")
		return
