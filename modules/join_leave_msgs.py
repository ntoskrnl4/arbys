from datetime import datetime
from client import client
import discord


@client.member_join
async def join_notification(member: discord.Member):
	if "discord.gg" in member.name and member.guild.id == 364480908528451584:
		try:
			await member.ban()
		except:
			await client.get_channel(473570993072504832).send("Attempted to autoban user below for \"discord.gg\" in username but failed!")
		else:
			await client.get_channel(473570993072504832).send("Successfully autobanned below user for \"discord.gg\" in username.")
	if member.guild.id == 364480908528451584:
		# await client.get_channel(473570993072504832).send(f"New member joined the server! Member {len(member.guild.members)}: {member.mention} {member.name}#{member.discriminator} (ID {member.id})")
		# with open("logs/members.log", "a") as lf:
		# 	lf.write(f"{member.joined_at.__str__()}+{member.guild.member_count}")
		embed = discord.Embed(title="Member has joined the server", description=discord.Embed.Empty, colour=0x15a216)
		embed = embed.set_thumbnail(url=member.avatar_url_as(static_format="png", size=1024))
		embed = embed.add_field(name="Tag", value=f"{member.name}#{member.discriminator}")
		embed = embed.add_field(name="ID", value=member.id)
		embed = embed.add_field(name="Mention", value=member.mention)
		embed = embed.add_field(name="New Member Count", value=member.guild.member_count)
		embed = embed.set_footer(text=member.joined_at)
		await client.get_channel(473570993072504832).send(embed=embed)


@client.member_remove
async def leave_notification(member: discord.Member):
	if member.guild.id == 364480908528451584:
		# await client.get_channel(473570993072504832).send(f"Member has left the server: {member.name}#{member.discriminator} ({member.display_name}) ({member.id})\nNew member count: {len(member.guild.members)}")
		# with open("logs/members.log", "a") as lf:
		# 	lf.write(f"{datetime.utcnow().__str__()}-{member.guild.member_count}")
		now = datetime.utcnow()
		embed = discord.Embed(title="Member has left the server", description=discord.Embed.Empty, colour=0xcd5312)
		embed = embed.set_thumbnail(url=member.avatar_url_as(static_format="png", size=1024))
		embed = embed.add_field(name="Tag", value=f"{member.name}#{member.discriminator}")
		embed = embed.add_field(name="ID", value=member.id)
		embed = embed.add_field(name="Nickname", value=member.display_name)
		embed = embed.add_field(name="Mention", value=member.mention)
		embed = embed.add_field(name="New Member Count", value=member.guild.member_count)
		embed = embed.set_footer(text=str(now))
		await client.get_channel(473570993072504832).send(embed=embed)

