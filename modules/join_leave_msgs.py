from datetime import datetime
from client import client
import discord

from modules import __common__


@client.member_join
async def join_notification(member: discord.Member):
    if member.guild.id == 675545015375888393:
        with open("logs/members.log", "a") as lf:
            lf.write(f"{__common__.get_timestamp(member.joined_at)}+{member.guild.member_count}\n")
        embed = discord.Embed(title="Member has joined the server", description=discord.Embed.Empty, colour=0x15a216)
        embed = embed.set_thumbnail(url=member.avatar_url_as(static_format="png", size=1024))
        embed = embed.add_field(name="Tag", value=f"{member.name}#{member.discriminator}")
        embed = embed.add_field(name="ID", value=member.id)
        embed = embed.add_field(name="Mention", value=member.mention)
        embed = embed.add_field(name="New Member Count", value=member.guild.member_count)
        created_ts = (await client.fetch_user(member.id)).created_at
        embed = embed.add_field(name="Account Created At", value=f"{__common__.get_timestamp(created_ts)}\n"
                                                                 f"{str(datetime.utcnow()-created_ts)}")
        embed = embed.set_footer(text=member.joined_at)
        await client.get_channel(675570198392209428).send(embed=embed)


@client.member_remove
async def leave_notification(member: discord.Member):
    if member.guild.id == 675545015375888393:
        with open("logs/members.log", "a") as lf:
            lf.write(f"{__common__.get_timestamp()}-{member.guild.member_count}\n")
        now = datetime.utcnow()
        embed = discord.Embed(title="Member has left the server", description=discord.Embed.Empty, colour=0xcd5312)
        embed = embed.set_thumbnail(url=member.avatar_url_as(static_format="png", size=1024))
        embed = embed.add_field(name="Tag", value=f"{member.name}#{member.discriminator}")
        embed = embed.add_field(name="ID", value=member.id)
        embed = embed.add_field(name="Nickname", value=member.display_name)
        embed = embed.add_field(name="Mention", value=member.mention)
        embed = embed.add_field(name="New Member Count", value=member.guild.member_count)
        embed = embed.add_field(name="Member since", value=f"{__common__.get_timestamp(member.joined_at)} UTC "
                                                           f"({now-member.joined_at})")
        embed = embed.set_footer(text=str(now))
        await client.get_channel(675570198392209428).send(embed=embed)
