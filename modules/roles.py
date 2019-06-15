from client import client

import discord
import log

@client.command(trigger="net")
async def toggle_net_role(command: str, message: discord.Message):
	if message.guild.id != 364480908528451584:
		await message.channel.send(client.unknown_command)
		return
	if 586730973715234827 not in [x.id for x in message.author.roles]:
		# need to add the role
		role = message.guild.get_role(586730973715234827)
		try:
			await message.author.add_roles(role)
		except discord.HTTPException:
			await message.channel.send(f"{message.author.mention} There was an error while trying to add the role. Message a mod for assistance.")
			log.warning("Failed to add net role to user", include_exception=True)
		else:
			await message.channel.send(f"{message.author.mention} You were added to the Net Reminders role. To remove yourself from this role at any time, just run this command again.")
		finally:
			return

	if 586730973715234827 in [x.id for x in message.author.roles]:
		# need to remove the role
		role = message.guild.get_role(586730973715234827)
		try:
			await message.author.remove_roles(role)
		except discord.HTTPException:
			await message.channel.send(f"{message.author.mention} There was an error while trying to remove the role. Message a mod for assistance.")
			log.warning("Failed to remove net role from user", include_exception=True)
		else:
			await message.channel.send(f"{message.author.mention} You were removed from the Net Reminders role. To add yourself back to this role at any time, just run this command again.")
		finally:
			return

@client.command(trigger="qso")
async def toggle_qso_role(command:str, message: discord.Message):
	if message.guild.id != 364480908528451584:
		await message.channel.send(client.unknown_command)
		return
	if 586731151515975680 not in [x.id for x in message.author.roles]:
		# need to add the role
		role = message.guild.get_role(586731151515975680)
		try:
			await message.author.add_roles(role)
		except discord.HTTPException:
			await message.channel.send(f"{message.author.mention} There was an error while trying to add the role. Message a mod for assistance.")
			log.warning("Failed to add qso role to user", include_exception=True)
		else:
			await message.channel.send(f"{message.author.mention} You were added to the QSO Request role. To remove yourself from this role at any time, just run this command again.")
		finally:
			return

	if 586731151515975680 in [x.id for x in message.author.roles]:
		# need to remove the role
		role = message.guild.get_role(586731151515975680)
		try:
			await message.author.remove_roles(role)
		except discord.HTTPException:
			await message.channel.send(f"{message.author.mention} There was an error while trying to remove the role. Message a mod for assistance.")
			log.warning("Failed to remove qso role from user", include_exception=True)
		else:
			await message.channel.send(f"{message.author.mention} You were removed from the QSO Request role. To add yourself back to this role at any time, just run this command again.")
		finally:
			return