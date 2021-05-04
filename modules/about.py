from client import client
from modules import __common__

import discord
import sys


cmd_name = "about"

client.basic_help(title=cmd_name, desc=f"Returns information about {client.bot_name}")

detailed_help = {
    "Usage": f"{client.default_prefix}{cmd_name}",
    "Description": "Shows information about the bot.",
}
client.long_help(cmd=cmd_name, mapping=detailed_help)


@client.command(trigger=cmd_name, aliases=['a'])  # aliases is a list of strs of other triggers for the command
async def return_bot_info(command: str, message: discord.Message):
    owner = client.get_user(288438228959363073)
    
    python_version = f"Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    if sys.version_info[3] == "alpha":
        python_version += f"a{sys.version_info.serial}"
    if sys.version_info[3] == "beta":
        python_version += f"b{sys.version_info.serial}"
    if sys.version_info[3] == "candidate":
        python_version += f"rc{sys.version_info.serial}"
    
    embed = discord.Embed(title=f"{client.bot_name} info", description=discord.Embed.Empty, color=0x404040)
    embed = embed.add_field(name="Version", value=f"Framework version {client.__version__}")
    embed = embed.add_field(name="Creator", value=f"{owner.name}#{owner.discriminator}\nID {owner.id}\n{owner.mention}")
    embed = embed.add_field(name="Github", value="`ntoskrnl4/arbys`\nhttps://www.github.com/ntoskrnl4/arbys", inline=False)
    embed = embed.add_field(name="Built with", value=f"Running on {python_version}\ndiscord.py library version {discord.__version__}\nntoskrnl-bot framework (`ntoskrnl4/ntoskrnl-bot`)")
    embed = embed.add_field(name="Invite Link", value=discord.utils.oauth_url(client.user.id), inline=False)
    embed = embed.add_field(name="Usage Notice", value="This bot may log messages to disk as part of moderation duties, development debugging, and command usage. Logs will never be used maliciously, are not stored in the cloud, and will not be given to any third party. For comments, questions, concerns, deletion orders, or retrieval requests, please contact ntoskrnl.")
    embed = embed.set_footer(text=__common__.get_timestamp())
    await message.channel.send(embed=embed)
    return
