from client import client
from modules import __common__
import markovify
import discord


cmd_name = "markov"

client.basic_help(title=cmd_name, desc="creates a message from a markov chain based on previous messages in a channel")

detailed_help = {
	"Usage": f"{client.default_prefix}{cmd_name} [id]",
	"Arguments": "`id` - (optional) channel to generate markov chain from\n`\"src=cache\"` - use messages from bot's cache as source (*all* messages the bot has seen)",
	"Description": "This command creates a message based on a markov chain generated from recent messages in the channel or from a channel mention passed as an argument.\nNote that this command requires the Read Message History permission.",
}
client.long_help(cmd=cmd_name, mapping=detailed_help)


@client.command(trigger=cmd_name)
async def command(command: str, message: discord.Message):
	command = command.split(" ")
	try:
		command[1]
	except IndexError:
		c = message.channel
	else:
		try:
			c = client.get_channel(__common__.stripMentionsToID(command[1]))
		except:
			c = message.channel
		else:
			if c.id == 473570993072504832:
				c = message.channel

	try:
		a = client.get_user(__common__.stripMentionsToID(command[1]))
		if a is not None:
			target_user_id = a.id
		else:
			target_user_id = None
	except:
		target_user_id = None

	async with message.channel.typing():
		if "src=cache" in command:
			msg_hist = list(client._connection._messages)
			await message.channel.send(f"[Generating markov chain from {len(client._connection._messages)} messages in cache...]")
		elif target_user_id is not None:
			msg_hist = []
			for ch in message.guild.text_channels:
				if ch.id == 473570993072504832:
					continue
				try:
					msg_hist.extend(await ch.history(limit=300).flatten())
				except:
					continue
			msg_hist = [x for x in msg_hist if x.author.id == target_user_id]
		else:
			msg_hist = await c.history(limit=3000).flatten()
		msg_hist_content = [x.clean_content for x in msg_hist]
		src_str = "\n".join(msg_hist_content)
		model = markovify.NewlineText(src_str)
		for _ in range(10):
			ret = model.make_short_sentence(500)
			if ret is not None:
				break
		else:
			ret = "<Error: For some reason the chain did not generate an acceptable sentence. Please rerun the command.>"
	await message.channel.send(ret)
	return

