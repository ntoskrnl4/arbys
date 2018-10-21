from typing import Union
import discord
import key


def stripMentionsToID(raw: str, ignore_escaped: bool = False) -> int:
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
