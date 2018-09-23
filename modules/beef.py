from client import client
import discord
import random


cmd_name = "beef"

detailed_help = {
	"Usage": f"{client.default_prefix}{cmd_name}",
	"Arguments": "None",
	"Description": "Shows some beef",
}
client.long_help(cmd=cmd_name, mapping=detailed_help)


images = ["https://cdn.discordapp.com/attachments/364488710995050496/398596887579459597/download_1.jpg",
		"https://cdn.discordapp.com/attachments/364488710995050496/398596933943558157/2226995-bigthumbnail.png",
		"http://groruddalen.no/bilder/nyheter/nyhetbig/15952.jpg",
]


@client.command(trigger=cmd_name,
				aliases=[])  # aliases is a list of strs of other triggers for the command
async def command(command: str, message: discord.Message):
	e = discord.Embed(title=discord.Embed.Empty, description=discord.Embed.Empty, colour=discord.Embed.Empty)
	e = e.set_image(url=random.choice(images))
	await message.channel.send(embed=e)
	return
