from datetime import datetime
from typing import Any, Dict, List, Tuple, Union

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


def parse_arguments(parts: List[str], args: Dict[str, Any]) -> Tuple[List[str], Dict[str, Any]]:
    """
    Parses out optional arguments from a command and returns the command and given arguments. Acceptable arguments
    are given to `args` in the format of {"name": default}, eg. {"debug": false, "count": 10}. Unknown or unparseable
    arguments return an exception. Switch options will return their default if not given, or !default if given.
    
    :param parts: Split up command to parse.
    :param args: Acceptable arguments to parse.
    :return: Parsed out parts, with any arguments that were found.
    """
    parsed = {}
    for name, default in args.items():
        if isinstance(default, bool):
            # the currently parsed argument is a switch
            if f"--{name}" in parts:
                parsed[name] = not default
                parts.pop(parts.index(f"--{name}"))
            else:
                parsed[name] = default
            continue
        # type(X) returns the class of X, which we can then use to convert to str/int/float/etc
        argtype = type(default)
        if f"--{name}" in parts:
            try:
                popped = parts.pop(parts.index(f"--{name}") + 1)
            except IndexError:
                raise RuntimeError(f"Argument error: No value given for argument --{name}") from None
            parts.pop(parts.index(f"--{name}"))
            try:
                # check for floats given on an int argument
                if isinstance(default, int):
                    if int(popped) != float(popped):
                        raise ValueError("not an integer")
                popped = argtype(popped)
            except ValueError as e:
                raise RuntimeError(f"Argument error: --{name} argument takes a {argtype.__name__} value "
                                   f"(got: {popped})") from None
            parsed[name] = popped
        else:
            parsed[name] = default
    # all arguments should be parsed now
    for item in parts:
        if item.startswith("--"):
            raise RuntimeError(f"Argument error: Unknown argument {item}")
    return parts, parsed


def get_timestamp(dt: datetime = None):
    if dt is None:
        dt = datetime.utcnow()
    return str(datetime.replace(dt, microsecond=0))
