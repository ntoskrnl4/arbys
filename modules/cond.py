from client import client

import discord


@client.command(trigger="cond")
async def command(command: str, message: discord.Message):
    await message.channel.send("just turn on your radio and try for yourself because the image was never accurate and "
                               "shouldn't've even been relied on a single bit <:abby_irl:676523172480417795>")
    return
