from client import client
import discord


@client.command(trigger="htm")
async def handle(command: str, message: discord.Message):
	e = discord.Embed(title="htm irl", description=discord.Embed.Empty, colour=discord.Embed.Empty)
	e.set_image(url="https://cdn.discordapp.com/attachments/377206780700393473/469686997066317824/unknown.png")
	e.set_footer(text="Command idea by @Hunter#4540")
	await message.channel.send(embed=e)
	return
