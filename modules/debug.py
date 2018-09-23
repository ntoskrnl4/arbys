from client import client
from modules import __common__
import discord
import asyncio


cmd_name = "debug"

client.basic_help(title=cmd_name, desc="Shows information about a specified object.")

detailed_help = {
	"Usage": f"{client.default_prefix}{cmd_name} <object>",
	"Arguments": "`<object>` - a mention or ID to get information about",
	"Description": "This command shows various debugging information about the user, the server used in, and the channel. The ID of a user, server, or channel can be passed in as well.",
}
client.long_help(cmd=cmd_name, mapping=detailed_help)


@client.command(trigger=cmd_name, aliases=["objinfo", "userinfo"])
async def command(command: str, message: discord.Message):
	try:
		try:
			u = await client.get_user_info(__common__.stripMentionsToID(command[6:]))
		except:
			isUser = False
		else:
			isUser = True

		s = client.get_guild(__common__.stripMentionsToID(command[6:]))
		if s is None:
			isServer = False
		else:
			isServer = True

		c = client.get_channel(__common__.stripMentionsToID(command[6:]))
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

	if isUser:
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

	if isServer:
		server_embed = discord.Embed(title="Server Information", description=f"Information about the server {s.name}", color=0xb368a2)
		server_embed = server_embed.set_thumbnail(url=s.icon_url)
		server_embed = server_embed.add_field(name="Name", value=s.name)
		server_embed = server_embed.add_field(name="Raw ID", value=s.id)
		icon = s.icon_url_as(format="png", size=1024)
		if icon == "":
			icon = "[no custom icon]"
		server_embed = server_embed.add_field(name="Icon URL", value=icon)
		server_embed = server_embed.add_field(name="Owner", value=f"{s.owner.name}#{s.owner.discriminator} ({s.owner.id})")
		server_embed = server_embed.add_field(name="Creation Time", value=s.created_at)
		server_embed = server_embed.add_field(name="Member Count", value=s.member_count)
		server_embed = server_embed.add_field(name="Role Count", value=len(s.roles))
		server_embed = server_embed.add_field(name="Emoji Count", value=len(s.emojis))
		server_embed = server_embed.add_field(name="Region", value=s.region)
		server_embed = server_embed.add_field(name="Is offline?", value=s.unavailable)
		server_embed = server_embed.add_field(name="Admin 2FA required?", value=s.mfa_level)
		server_embed = server_embed.add_field(name="Verification Level", value=s.verification_level)

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
		await asyncio.sleep(0.05)  # slight delay because we want the information in order and because that's a shitload of info

	if isServer:
		await message.channel.send(embed=server_embed)
		await asyncio.sleep(0.05)

	if isTextChannel or isVoiceChannel:
		await message.channel.send(embed=channel_embed)
		await asyncio.sleep(0.05)

	if not (isUser or isServer or (isTextChannel or isVoiceChannel)):  # if not a user, server, or channel:
		await message.channel.send(f"Unknown user, server, or channel with ID {command[6:]}. I might not be able to 'see' that object.")
	return

	return
