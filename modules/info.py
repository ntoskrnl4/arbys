from client import client
from modules import __common__

import asyncio
import datetime
import discord


cmd_name = "info"

client.basic_help(title=cmd_name, desc="Shows information about a specified object.")

detailed_help = {
	"Usage": f"{client.default_prefix}{cmd_name} <object>",
	"Arguments": "`<object>` - a mention or ID to get information about",
	"Description": "This command shows various debugging information about the user, the server used in, and the channel. The ID of a user, server, or channel can be passed in as well.",
}
client.long_help(cmd=cmd_name, mapping=detailed_help)


def status_emoji(state: discord.Status) -> str:
	if state is discord.Status.online: return "<:status_online:534918510950744064>"
	if state is discord.Status.idle: return "<:status_idle:534918510548090882>"
	if state is discord.Status.dnd: return "<:status_dnd:534918509701103622>"
	if state is discord.Status.offline: return "<:status_offline:534918510652948501>"


def get_any_member(target: int):
	for guild in client.guilds:
		if guild.get_member(target) is not None:
			return guild.get_member(target)
	return None


@client.command(trigger=cmd_name, aliases=["objinfo", "userinfo"])
async def command(command: str, message: discord.Message):
	parts = command.split(" ")
	if len(parts) == 1:
		# no following argument
		await message.channel.send(f"You ran this command without arguments. The old `{client.default_prefix}info` command has been moved to `{client.default_prefix}about`, and this command is now what `{client.default_prefix}debug` used to be.")
		return
	try:
		try:
			u = await client.fetch_user(__common__.stripMentionsToID(parts[1]))
		except TypeError:
			await message.channel.send("Invalid argument: integer ID or mentions are acceptable")
			return
		except:
			isUser = False
		else:
			isUser = True

		s = client.get_guild(__common__.stripMentionsToID(parts[1]))
		if s is None:
			isServer = False
		else:
			isServer = True

		c = client.get_channel(__common__.stripMentionsToID(parts[1]))
		if c is None:
			isTextChannel = False
			isVoiceChannel = False
		else:
			if isinstance(c, discord.TextChannel):
				isTextChannel = True
				isVoiceChannel = False
			elif isinstance(c, discord.VoiceChannel):
				isTextChannel = False
				isVoiceChannel = True
			else:
				await message.channel.send("Invalid channel type - handling for this is not implemented. Sorry.")
				return

	except ValueError:
		u = message.author
		isUser = True
		s = message.guild
		isServer = True
		c = message.channel
		isTextChannel = True
		isVoiceChannel = False

	if isUser and not "--status" in command:
		user_embed = discord.Embed(title="User Information", description=f"Information about {u.mention}", color=0x3127b3)
		user_embed = user_embed.set_thumbnail(url=u.avatar_url_as(static_format="png", size=1024))
		user_embed = user_embed.add_field(name="Human-Friendly User ID", value=u.name+"#"+u.discriminator)
		user_embed = user_embed.add_field(name="User Avatar URL", value=u.avatar_url_as(static_format="png", size=1024))
		user_embed = user_embed.add_field(name="Raw User ID", value=u.id)
		user_embed = user_embed.add_field(name="Is Bot", value=u.bot)
		user_embed = user_embed.add_field(name="Account Creation Time", value=u.created_at)
		if message.guild.get_member(u.id) is not None:
			m = message.guild.get_member(u.id)
			roles = "\n".join([f"{x.name} ({x.id})" for x in m.roles][::-1])
			user_embed = user_embed.add_field(name="Roles in this server", value=roles, inline=False)
			user_embed = user_embed.add_field(name="User Nickname", value=m.display_name)
			user_embed = user_embed.add_field(name="Joined this server on", value=m.joined_at.__str__())
		if get_any_member(u.id) is not None:
			m = get_any_member(u.id)
			user_embed = user_embed.add_field(name="Current State",
												value=f"Apparent Status: {status_emoji(m.status)}\n"
														f"Desktop: {status_emoji(m.desktop_status)}\n"
														f"Web: {status_emoji(m.web_status)}\n"
														f"Mobile: {status_emoji(m.mobile_status)}\n",
												inline=False)
		user_embed = user_embed.set_footer(text=datetime.datetime.utcnow().__str__())

	if isUser and "--status" in command:
		if get_any_member(u.id) is not None:
			m = get_any_member(u.id)
		else:
			return await message.channel.send("Cannot get status: I do not share any servers with this user (in order to get a user's status I must share a server with them)")
		user_embed = discord.Embed(description=f"Apparent Status: {status_emoji(m.status)}\n"
																	f"Desktop: {status_emoji(m.desktop_status)}\n"
																	f"Web: {status_emoji(m.web_status)}\n"
																	f"Mobile: {status_emoji(m.mobile_status)}\n"
																	f"Is on mobile? {m.is_on_mobile()}",)
		user_embed = user_embed.set_author(icon_url=m.avatar_url_as(format="png", size=128), name=f"{m.name}#{m.discriminator}")
		user_embed = user_embed.set_footer(text=datetime.datetime.utcnow().__str__())

	if isServer:
		server_embed = discord.Embed(title="Server Information", color=0xb368a2)
		server_embed = server_embed.add_field(name="Name", value=s.name)
		server_embed = server_embed.add_field(name="Raw ID", value=s.id)
		icon = s.icon_url_as(format="png", size=1024)
		if not icon:  # Used to be != "" before icon was a discord.Asset, credit to eyyyyyy/0x5c for finding/fixing this
			icon = "[no custom icon]"
			server_embed = server_embed.set_thumbnail(url=s.icon_url)
		server_embed = server_embed.add_field(name="Icon URL", value=icon)
		server_embed = server_embed.add_field(name="Owner", value=f"{s.owner.name}#{s.owner.discriminator}\nID {s.owner.id}")
		server_embed = server_embed.add_field(name="Member Count", value=s.member_count)
		server_embed = server_embed.add_field(name="Role Count", value=len(s.roles))
		server_embed = server_embed.add_field(name="Emoji Count", value=len(s.emojis))
		server_embed = server_embed.add_field(name="Creation Time", value=s.created_at)
		server_embed = server_embed.add_field(name="Region", value=s.region)
		server_embed = server_embed.add_field(name="Is offline?", value=s.unavailable)
		server_embed = server_embed.add_field(name="Admin 2FA required?", value=bool(s.mfa_level))
		server_embed = server_embed.add_field(name="Verification Level", value=s.verification_level)
		server_embed = server_embed.set_footer(text=datetime.datetime.utcnow().__str__())

	if isTextChannel:
		channel_embed = discord.Embed(title="Channel Information", description=f"Information about the text channel {c.mention}", color=0x8f44a2)
		channel_embed = channel_embed.add_field(name="Name", value=c.name)
		channel_embed = channel_embed.add_field(name="ID", value=c.id)
		channel_embed = channel_embed.add_field(name="Server", value=f"{c.guild.name} ({c.guild.id})")
		t = c.topic
		if t == "":
			t = "[none]"
		channel_embed = channel_embed.add_field(name="Topic", value=t, inline=False)
		channel_embed = channel_embed.add_field(name="Creation Time", value=c.created_at)

	if isVoiceChannel:
		channel_embed = discord.Embed(title="Channel Information", description=f"Information about the voice channel {c.name}", color=0x8f44a2)
		channel_embed = channel_embed.add_field(name="Name", value=c.name)
		channel_embed = channel_embed.add_field(name="ID", value=c.id)
		channel_embed = channel_embed.add_field(name="Server", value=f"{c.guild.name} ({c.guild.id})")
		channel_embed = channel_embed.add_field(name="Bitrate", value=c.bitrate)
		channel_embed = channel_embed.add_field(name="User Limit", value=c.user_limit)
		channel_embed = channel_embed.add_field(name="Creation Time", value=c.created_at)
		in_vc = "\n".join([f"{x.display_name} ({x.name}#{x.discriminator} - {x.id})" for x in c.members])
		if in_vc == "":
			in_vc = "[none]"
		channel_embed = channel_embed.add_field(name="Members Currently In Channel", value=in_vc)

	if isUser:
		await message.channel.send(embed=user_embed)
		await asyncio.sleep(0.05)

	if isServer:
		await message.channel.send(embed=server_embed)
		await asyncio.sleep(0.05)

	if isTextChannel or isVoiceChannel:
		channel_embed = channel_embed.set_footer(text=datetime.datetime.utcnow().__str__())
		await message.channel.send(embed=channel_embed)
		await asyncio.sleep(0.05)

	if not (isUser or isServer or (isTextChannel or isVoiceChannel)):  # if not a user, server, or channel:
		await message.channel.send(f"Unknown user, server, or channel with ID {parts[1]}. I might not be able to 'see' that object.")
	return
