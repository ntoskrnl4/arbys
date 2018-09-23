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
