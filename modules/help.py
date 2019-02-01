from client import client

import datetime
import discord


@client.command(trigger="help", aliases=[])
async def help_command(command: str, message: discord.Message):

	if command.lower() == "help":
		# basic help route
		embed = discord.Embed(title=f"Help for {client.bot_name}", description=f"For help on a specific command, run `{client.default_prefix}help <command>`", colour=0x06b206)

		for cmd, desc in client._basic_help.items():
			embed = embed.add_field(name=f"{cmd}", value=desc, inline=False)
		embed.set_footer(text=datetime.datetime.utcnow().__str__())
		await message.channel.send(embed=embed)

	if command.lower().startswith("help "):  # a trailing space means there's text after it (Discord strips whitespace)

		sub_help = command.lower()[5:]
		sub_help = client._long_help.get(sub_help, client._long_help.get(client.alias_lookup.get(sub_help, None)))

		if sub_help is None:
			# unknown command branch
			embed = discord.Embed(title=f"Help for command `{command.lower()[5:]}`", description=f"Unknown command", colour=0xa20303)
			embed = embed.set_footer(text=datetime.datetime.utcnow().__str__())
			await message.channel.send(embed=embed)

		elif type(sub_help) == dict:
			embed = discord.Embed(title=f"Help for command `{command.lower()[5:]}`", description=sub_help.get("_description", discord.Embed.Empty), colour=0x06b206)
			for title, text in sub_help.items():
				embed = embed.add_field(name=title, value=text, inline=False)
			if client.cmd_aliases.get(command.lower()[5:], []):
				embed = embed.add_field(name="Aliases", value="\n".join(client.cmd_aliases.get(command.lower()[5:], [])))
			embed = embed.set_footer(text=datetime.datetime.utcnow().__str__())
			await message.channel.send(embed=embed)

client.basic_help("help [command]", "Get help with the bot or a certain command")

help_long_help = {
	"Usage:": f"`{client.default_prefix}help [command]`",
	"Arguments": "`command` - (Optional) Bot command to fetch detailed help with.",
	"Description": "This command fetches help information for a command or for all commands."
}
client.long_help("help", help_long_help)
