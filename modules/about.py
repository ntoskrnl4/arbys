from client import client

import datetime
import discord
import key


cmd_name = "about"

client.basic_help(title=cmd_name, desc=f"returns information about {client.bot_name}")

detailed_help = {
	"Usage": f"{client.default_prefix}{cmd_name}",
	"Description": "Shows information about the bot.",
	# NO Aliases field, this will be added automatically!
}
client.long_help(cmd=cmd_name, mapping=detailed_help)


@client.command(trigger=cmd_name)  # aliases is a list of strs of other triggers for the command
async def handle(command: str, message: discord.Message):
	embed = discord.Embed(title=f"{client.bot_name} info", description=discord.Embed.Empty, color=0x404040)
	embed = embed.add_field(name="Version", value=f"Framework version {client.__version__}\nBot version 0.8")
	embed = embed.add_field(name="Creator", value=key.creator)
	embed = embed.add_field(name="Github", value=key.github_info)
	embed = embed.add_field(name="Built with", value=key.built_with)
	embed = embed.add_field(name="Invite Link", value=key.invite_url)
	embed = embed.set_footer(text=datetime.datetime.utcnow().__str__())
	await message.channel.send(embed=embed)
	return
