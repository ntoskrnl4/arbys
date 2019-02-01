from typing import List, Tuple, Union


def check_command_prefix(message: str, prefixes: List[str]) -> Tuple[bool, Union[str, None]]:
	# this function handles specifically command prefixes because the same code to detect regular non-word prefixes in
	# bots will cause a bug in command triggers where "xxx<whatever>" triggers the same command as "xxx". This function
	# is the correct version for commands that also checks by splitting the message.
	for prefix in prefixes:
		if message.lower().startswith(prefix) and (message.split(" ")[0].lower() == prefix.lower().strip()):
			return True, prefix
	return False, None


def check_bot_prefix(message: str, prefixes: List[str]) -> Tuple[bool, Union[str, None]]:
	# This function is similar to the function above in that it also checks for the prefixes on the bot, however is also
	# modified to properly handle character-based prefixes instead of just word-based prefixes.
	for prefix in prefixes:
		if message.lower().startswith(prefix.lower()):
			return True, prefix
	return False, None
