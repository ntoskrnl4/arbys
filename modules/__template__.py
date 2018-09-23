from client import client
import discord


cmd_name = "command"

client.basic_help(title=cmd_name, desc="This is what my command does, in a sentence.")

detailed_help = {
	"Usage": f"{client.default_prefix}{cmd_name}",
	"Arguments": "None",
	"Description": "This is what the command does!",
	# NO Aliases field, this will be added automatically!
}
client.long_help(cmd=cmd_name, mapping=detailed_help)


@client.command(trigger=cmd_name,
				aliases=[])  # aliases is a list of strs of other triggers for the command
async def command(command: str, message: discord.Message):
	# Awesome stuff happens here!
	return
