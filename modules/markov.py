from client import client
from datetime import datetime
from modules import __common__
from typing import Tuple

import asyncio
import discord
import markovify


cmd_name = "markov"

client.basic_help(title=cmd_name, desc="creates a message from a markov chain based on previous messages in a channel")

detailed_help = {
    "Usage": f"{client.default_prefix}{cmd_name} [mention] [--charlimit x] [--size y] [--attempts z]",
    "Arguments": "`mention` - (optional) mention or ID of a channel or user to generate markov chain from (not provided = current channel)\n"
                 "`--charlimit` - (optional) specifies a custom maximum amount of permitted characters (default 1500 - lower values may require more --attempts)\n"
                 "`--size` - (optional) specifies the size of the markov chain. For text 2 or 3 is most common, for very large sources 4 may work. (default 3)\n"
                 "`--attempts` - (optional) specifies how many times the markov chain should attempt to generate valid output before giving up (default 50 - higher values have a better chance of succeeding for small sources)\n",
    "Description": "This command reads input from a given source and feeds messages into a markov chain, which is then used to generate a random sentence that is similar to that of the input. Acceptable sources include the current channel (nothing given for `mention` argument), a specific user (that user's mention or preferably ID given for `mention` argument), or a specific channel (that channel's mention or ID given for `mention` argument).",
}
client.long_help(cmd=cmd_name, mapping=detailed_help)

forbidden_channels = [
    473570993072504832,
    826099521032290334,
    826868270740013116,
    829321559217930240,
    830263185088708660
]


async def get_user_markov(user: int, message: discord.Message):
    input_messages = [x for x in client._connection._messages if x.author.id == user]
    await asyncio.sleep(0.1)
    input_messages = [x for x in input_messages if getattr(x.guild, 'id', -1) == message.guild.id]
    await asyncio.sleep(0.1)
    if message.channel.id not in forbidden_channels:
        input_messages = [x for x in input_messages if x.channel.id not in forbidden_channels]
        await asyncio.sleep(0.1)
    
    # backup code if that's not enough
    if len(input_messages) < 400:
        input_messages = []
        for ch in message.guild.text_channels:
            if ch.id in forbidden_channels:
                continue
            try:
                input_messages.extend([x for x in await ch.history(limit=500).flatten() if x.author.id == user])
            except:
                continue
    
    return input_messages


async def get_channel_markov(channel: discord.TextChannel):
    try:
        input_messages = await channel.history(limit=3000).flatten()
    except discord.Forbidden:
        return None  # we can't read the channel so this is noootttt going to work at all

    return input_messages


@client.command(trigger=cmd_name)
async def command(parts: str, message: discord.Message):
    parts = parts.split(" ")
    
    response = discord.Embed()
    
    try:
        parts, arguments = __common__.parse_arguments(parts, {
            "charlimit": 1500,
            "attempts": 50,
            "size": -1
        })
    except RuntimeError as e:
        response.colour = 0xb81209
        response.title = "Markov function error"
        response.description = str(e) + "\n\nFor help on using this command, run `cqdx help markov`"
        response.set_footer(text=__common__.get_timestamp())
        await message.channel.send(embed=response)
        return
    
    size = arguments["size"]
    charlimit = arguments["charlimit"]
    attempts = arguments["attempts"]
    
    # determine our target.
    target = None
    target_type = "unknown"
    # check for nothing
    if len(parts) is 1:
        target = message.channel
        target_type = "channel"
    
    if len(parts) > 1:
        
        # get channel if it is one
        if parts[1].startswith("<#"):
            target = message.channel_mentions[0]
            target_type = "channel"
        
        if parts[1].startswith("<@") or parts[1].startswith("<!@"):
            target = message.mentions[0]
            target_type = "user"
    
    if target_type == "unknown":
        try:
            user = message.guild.get_member(__common__.strip_to_id(parts[1]))
        except TypeError:
            await message.channel.send("Argument error: Invalid object or user/channel mention")
            return
        channel = message.guild.get_channel(__common__.strip_to_id(parts[1]))
        if user is not None:
            target_type = "user"
            target = user
        if channel is not None:
            target_type = "channel"
            target = channel
    
    if target_type == "unknown":
        await message.channel.send("Argument error: Invalid object or user/channel mention")
    
    # run different outputs for different input types
    async with message.channel.typing():

        if target_type == "user":
            target_member = message.guild.get_member(target.id)
            if target_member is not None:
                display_target = f"{target_member.display_name}"
            else:
                display_target = f"{target.name}#{target.discriminator}"

            response.set_author(name=display_target, icon_url=target.avatar_url_as(format="png", size=128))
            
            try:
                input_messages = await get_user_markov(target.id, message)
            except KeyError:
                await message.channel.send(f"{message.author.mention} The user you have specified has had no recent messages. This function only works on users who have been active recently.")
                return

        if target_type == "channel":
            if target.guild.id != message.guild.id:
                await message.channel.send("Argument error: Channel provided is not in current server")
                return
            input_messages = await get_channel_markov(target)

            if input_messages is None:  # permissions error
                response.colour = 0xb81209
                response.title = "Markov chain failed"
                response.description = "Unable to run markov chain: Insufficient permissions to read channel history"
                response.set_footer(text=f"{__common__.get_timestamp()}")
                response.set_author(name=f"#{target.name}")
                # if we can't read the channel we should check if we can write to it also
                try:
                    await message.channel.send(embed=response)
                except discord.Forbidden:
                    pass

            response.set_author(name=f"#{target.name}")

        if size == -1:
            if len(input_messages) < 500:
                size = 2
            elif 500 < len(input_messages) < 1000:
                size = 3
            elif 1000 < len(input_messages):
                size = 4

        src_string = "\n".join([x.content for x in input_messages])
        model = markovify.NewlineText(src_string, state_size=size)
        await asyncio.sleep(0.1)
        result = model.make_short_sentence(max_chars=charlimit, tries=attempts)

        if result is None:
            response.colour = 0xb81209
            response.title = "Markov function failed"
            response.description = "Unable to run markov chain - try running the command again"
        else:
            response.colour = 0x243b61
            response.description = result

        response.set_footer(text=f"{__common__.get_timestamp()} | "
                                 f"{len(input_messages)} messages in input | "
                                 f"Size: {size}")
        await message.channel.send(embed=response)
        return
