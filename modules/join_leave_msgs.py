from datetime import datetime
from client import client
import discord
import log


@client.member_join
async def join_notification(member: discord.Member):
	if "discord.gg" in member.name and member.guild.id == 364480908528451584:
		try:
			await member.ban()
		except:
			log.warning("Could not autoban member (no permission?)")
		else:
			await client.get_channel(473570993072504832).send(f"Notice: Autobanned member for \"discord.gg\" in username: {member.mention} ({member.name}#{member.discriminator}) ({member.id})")
	if member.guild.id == 364480908528451584:
		await client.get_channel(473570993072504832).send(f"New member joined the server! Member {len(member.guild.members)}: {member.mention} {member.name}#{member.discriminator} (ID {member.id})")
		with open("logs/members.log", "a") as lf:
			lf.write(f"{member.joined_at.__str__()}+{member.guild.member_count}")


@client.member_remove
async def leave_notification(member: discord.Member):
	if member.guild.id == 364480908528451584:
		await client.get_channel(473570993072504832).send(f"Member has left the server: {member.name}#{member.discriminator} ({member.display_name}) ({member.id})\nNew member count: {len(member.guild.members)}")
		with open("logs/members.log", "a") as lf:
			lf.write(f"{datetime.utcnow().__str__()}-{member.guild.member_count}")
