from typing import List, Tuple, Union
from functools import lru_cache


# @lru_cache(maxsize=256)
def check_prefix(message: str, prefixes: List[str]) -> Tuple[bool, Union[str, None]]:
	for prefix in prefixes:
		if message.lower().startswith(prefix) and (message.split(" ")[0] == prefix.strip()):
			return True, prefix
	return False, None

