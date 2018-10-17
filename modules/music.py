from exceptions import AmbiguousChannelError, UnknownChannelError, NotConnectedException, MusicException
from client import client
from typing import Union
import discord
import log


client.basic_help(title="music", desc="Handles music functionality within the bot. (Currently disabled)")
detailed_help = {
	"Usage": f"{client.default_prefix}music <subcommand> [args]",
	"Arguments": "`subcommand` - subcommand to run\n`args` - (optional) arguments specific to the subcommand being run",
	"Description": "This command manages music related functionality within the bot. Music is available to several servers at once.",
	"Subcommands": "",
}
client.long_help(cmd="music", mapping=detailed_help)


class Song:
	def __init__(self, location: str):



def check_if_user_in_channel(channel: discord.VoiceChannel, user: Union[discord.User, int]) -> bool:
	return getattr(user, "id", user) in [x.id for x in channel.members]


def get_target_voice_connection(object: Union[discord.Member, discord.Guild, discord.VoiceChannel, int]) -> Union[discord.VoiceClient, MusicException]:
	target = None

	if isinstance(object, discord.Member):
		target = object.voice.channel
	if isinstance(object, discord.Guild):
		target = discord.utils.find(lambda x: x.id == object.id, client.voice_clients)
	if isinstance(object, discord.VoiceChannel):
		target = object

	if isinstance(object, int):
		# seriously :/
		log.warning("get_target_voice_channel() given a raw integer/ID; this probably should not happen but I'll try my best")

		channel = client.get_channel(object)
		guild = client.get_guild(object)
		if isinstance(guild, discord.Guild):
			target = discord.utils.find(lambda x: x.id == object, client.voice_clients)

		elif isinstance(channel, discord.VoiceChannel):
			target = channel

		else:
			target = None

	if not isinstance(target, discord.VoiceChannel):
		return UnknownChannelError("Requested channel is not known")
	# now we know that target is a VoiceChannel
	if not check_if_user_in_channel(target, client.user.id):
		# if we're not in the channel
		return NotConnectedException("We're not currently connected to this voice channel")
	else:
		return discord.utils.find(lambda x: x.id == client.user.id, target.members).voice


@client.command(trigger="music")
async def command(command: str, message: discord.Message):
	if "--bypass" not in command:
		await message.channel.send("Sorry, but this command has been temporarily removed as it is currently being rewritten.")
		return
