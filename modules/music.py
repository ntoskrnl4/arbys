from client import client
import discord


client.basic_help(title="music", desc="This is what my command does, in a sentence.")

detailed_help = {
	"Usage": f"{client.default_prefix}music <subcommand> [args]",
	"Arguments": "`subcommand` - subcommand to run\n`args` - (optional) arguments specific to the subcommand being run",
	"Description": "This command manages music related functionality within the bot. Music is available to several servers at once.",
	"Subcommands": "`music join [optional_id]` - join your current voice channel, or the one with the given id\n`music add [filename or youtube url]` - add that song to the queue\n`music play` - start playing music in the queue\n`music volume [float from 0-2]` - change volume of music\n`music skip` - skip currently playing song\n`music exit` - exit from voice chat",
}
client.long_help(cmd="music", mapping=detailed_help)


@client.command(trigger="music")
async def command(command: str, message: discord.Message):
	await message.channel.send("Sorry, but this command has been temporarily removed as it is currently being rewritten.")
	return
