from typing import Union
import discord
import key


def strip_to_id(raw: str, ignore_escaped: bool = False) -> int:
	if ignore_escaped and (raw[0] == "\\"):
		raise TypeError("not an actual mention (likely escaped)")
	s = raw.replace(">", "")
	s = s.replace("<@!", "")
	s = s.replace("<@&", "")
	s = s.replace("<@", "")
	s = s.replace("<#", "")
	try:
		ret = int(s)
	except ValueError:
		raise TypeError("could not be converted to numerical id form (probably not an actual mention)")
	else:
		return ret


def check_permission(user: Union[discord.Member, discord.User]) -> bool:
	return any([x.id in key.admin_users for x in user.roles]) or (user.id in key.admin_users)


async def confirm(message: discord.Message, fallback: str = None) -> bool:
	"""
	Helper function to send a checkmark reaction on a message. This would be
	used for responding to a user that an action completed successfully, 
	without sending a whole other message. If a checkmark reaction cannot
	be added, the optional `fallback` message will be sent instead. 
	
	:param discord.Message message: The message to add the reaction to.
	:param str fallback: The fallback message to be sent to the channel, if the reaction could not be added.
	:return: Whether confirming the message succeeded.
	"""
	try:
		await message.add_reaction("☑")
	except:
		pass
	else:
		return True
	
	if fallback is None:
		return False
	# now still executing only if the above failed
	try:
		await message.channel.send(fallback)
	except:
		return False  # we weren't able to send any feedback to the user at all
	else:
		return True
	
	
async def failure(message: discord.Message, fallback: str = None) -> bool:
	"""
	Helper function to send a X (failed) reaction on a message. This would be
	used for responding to a user that an action was denied, without sending a
	whole other message. If the reaction cannot be added, the optional
	`fallback` message will be sent instead.
	
	:param discord.Message message: The message to add the reaction to.
	:param str fallback: The fallback message to be sent to the channel, if the reaction could not be added.
	:return: Whether confirming the message succeeded.
	"""
	try:
		await message.add_reaction("❌")
	except:
		pass
	else:
		return True
	
	if fallback is None:
		return False
	# now still executing only if the above failed
	try:
		await message.channel.send(fallback)
	except:
		return False  # we weren't able to send any feedback to the user at all
	else:
		return True
