from client import client


@client.command(trigger="call")
async def command(command: str, message):
	await message.channel.send(embed=f"{message.author.mention} This command has been deprecated. Please use the `htm call` command instead.", delete_after=10)
	return
