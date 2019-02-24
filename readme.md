# ntoskrnl-bot
A simplified framework for creating modular Discord bots

---
### Features
* Fully modular design - all user code goes into modules in the `modules/` directory
* No defined arguments or names for commands - unlike discord.py's Bot extension, functions' names have no relation to what triggers them
* Not limited to commands
	* Currently supports user code for the following Discord events:
		* `@client.command()` (command is run)
		* `@client.message()` (message is sent)
		* `@client.member_join` (user joins a server)
		* `@client.member_remove` (user leaves a server)
		* `@client.reaction_add` (reaction is added to a message)
		* `@client.reaction_remove` (reaction is removed from a message)
		* `@client.ready` (bot connects to Discord)
		* `@client.shutdown` (bot starts shutting down)
* Built-in customizable help system
	* Supports basic one-line help for the entire bot or detailed help for a specific command
	* Commands are not forced to have either help entry, or both, allowing commands to be hidden or to only have a detailed help entry
* Permits any number of prefixes of any kind, including word-based prefixes and character-based prefixes
* Fast: Less than 30ms (typical) between message received and command triggered 
* Custom logging designed to be fast, with low overhead

###Setup
Before writing code for the bot you must consider what system it will run on. For 24/7 use a decently powerful computer
should be used with a stable Internet connection is recommended, ideally running Linux as well. A Raspberry Pi is
perfect for this as it uses Linux, is low cost, and can be left alone.

1. If you haven't already, install the following:
	* Python 3.6+
	* discord.py rewrite
		* To do this install via pip: `pip install -U https://github.com/Rapptz/discord.py/archive/rewrite.zip#egg=discord.py[voice]` 
			* `[voice]` at the end of that line is only necessary if voice functionality is desired.
2. Clone the repository to the server.
3. Create a file named `key.py` in the main directory. Within, add the line `token = ""` and fill in your bot's token.
4. Change `config.py` to your desired settings.
5. `modules/` contains all of your code, along with three pre-supplied modules: a help command, a ping command, and a
message logging command.

######Warning
Before enabling the message logging module, it is *very highly recommended* that you __thoroughly__ read through Discord's
bot development terms of service, as there are precautions and terms that must be taken when logging user messages.
[Link](https://discordapp.com/developers/docs/legal)
 
###Writing modules
The main flexibility of the bot comes with respect to its modules. Modules are added by creating a new file in the
`modules/` directory with a name of your choice and adding relevant code to the file.

```
Note: It is highly recommended that the user become familiar with the discord.py primary API page, as it is useful when 
developing modules:
https://discordpy.readthedocs.io/en/rewrite/api.html
```

Every module in order to work with the bot must import it into the file: `from client import client`  
Importing the `discord` module is also highly recommended as it allows you to use typing and embeds and other features
of discord.py.

Imports are recommended to be sorted by type and then by alphabetical order, for example:
```
from client import client
from datetime import datetime
from time import sleep

import asyncio
import discord
import json
import os
import sys
```

####Help
The framework includes two kinds of help; a "basic help" displayed as the bot's primary help, and a "detailed help" that
shows in depth information for a command. Modules can add as many or as few objects to these help commands as they want.

#####Basic help
An entry for basic help can be added to the bot by running the function `client.basic_help(title, description)`:
* `title: str` is the title of the command. Should typically just be the trigger for the command, eg. `ping`
* `description: str` is the description for the command. This should be one sentence that describes briefly what the
command does. Don't include a command's aliases or arguments in here as those are in a command's detailed help.
* `include_prefix: bool = True` (optional) automatically adds in the bot's prefix to the title.

#####Detailed help
Modules can add detailed help by running the `client.long_help(cmd, mapping)` command:
* `cmd: str` - command to bind help to.
* `mapping: Dict[str, str]` - A direct mapping of title -> content that will be shown in the command's help embed.
Aliases do not need to be added in here as they will be added for you, if applicable. Recommended fields are as follows:
	* `Usage` - a direct show of the command and its arguments.
	* `Arguments` - explanation of any and all arguments in the command
	* `Description` - a written English explanation of what the command does

#####Example
```python
client.basic_help("ping", "Returns the bot's latency to its connected API endpoint.")

detailed_help = {
	"Usage": f"`{client.default_prefix}ping`",
	"Description": "This command returns the bot's latency to the Discord API endpoint it is connected to."
}
client.long_help("ping", detailed_help)

``` 

####Adding a command
In order to add a command, a coroutine must be created with the arguments `command` and `message`, and the function
must use the decorator `@client.command()`. Arguments for the decorator include `trigger=""` which defines what command
will trigger your function, and an optional argument `aliases=[]`, a list of `str`s that also trigger the command.
For example:
```python
@client.command(trigger="time")
async def show_time(command: str, message: discord.Message):
	# your code here...
```
Notice that the function's arguments include types in them, which is highly recommended to remind you what the variables
are, and to tell your IDE what the variables are if you run the code in an IDE.  

####Responding to a non-command message (Adding a message handler)
The framework allows modules to also parse every message running through the bot as well. These message handlers include
messages that trigger commands, and are run before commands are. To add a message handler a coroutine must be created 
with a single argument `message` (type `discord.Message`), and the function must be decorated with `@client.message()`. 
The decorator takes one argument `receive_self` (type `bool`) that defines whether this function will be activated for 
the bot's own messages, and it defaults to `True`.

For example:
```python
@client.message()  # receive_self argument omitted; defaults to True
async def react(message: discord.Message):
	# your code here...
```

####Reacting to a member_join or member_leave event
Modules can have a reaction to a member join or leave event, by creating a coroutine with the argument `member`
(type `discord.Member`) with the decorators `@client.member_join` or `@client.member_remove`. This can be used for example 
to post information about the user in a moderator-only channel when a new user joins the server, or to post information 
about a user when they leave the server.

For example:
```python
@client.member_join
async def hello(member: discord.Member):
	await channel.send(f"Hello, {member.name}!")

@client.member_remove
async def goodbye(member: discord.Member):
	await channel.send(f"Goodbye, {member.display_name}.")
```

####Reacting to...reactions
A function can be triggered by the addition or removal of a reaction from a message with the decorators
`@client.reaction_add` or `@client.reaction_remove`. As with other functions they must be coroutines. Arguments for these
handlers are `reaction` (type `discord.Reaction`) and `source` (type `discord.Member`). Info about these arguments can
be found [here](https://discordpy.readthedocs.io/en/rewrite/api.html#discord.on_reaction_add). Note that the message 
must be in the cache for these events to be run; the size of the cache can be increased with the `message_cache_size` 
variable in `config.py` at the cost of more memory.

####Running a startup or shutdown function
Some modules may desire for a function to be run once when the bot starts up and connects to Discord; this can be done
by creating a coroutine with the decorator `@client.ready`. This can be useful for loading persistent-state information
into a module for later use with a command, as an example. These ready functions are only run once when the bot 
initially starts up, and won't be run if discord.py disconnects and must reconnect to Discord.

Likewise, a coroutine can also be run when the bot is exited through a command. This can be useful for saving persistent-state
information to a file, though it means modules that rely on this must then exit the bot through the shutdown procedure
(by calling `client.on_shutdown()`).

For example:
```python
@client.ready
async def load_data():
	data = json.load(file)
	# your code here...

@client.shutdown
async def save_data():
	json.dump(data, file)
	# your code here...
```

####Running a background task
A background task independent of any trigger may be desired. In that case, the decorator `@client.background()` can  
provide this functionality for you, including waiting until the bot is online, only running while the bot is active, and
automatic handling of periodic tasks.

To use the decorator, create a coroutine with the code that you want to be run periodically. No loop code or 
`wait_until_ready()` should be included as this will be done automatically. To add the coroutine as a periodic 
background task, add the decorator `@client.background()`:
* `period: int` - Period of which the function should be run, in seconds.

For example:
```python
@client.background(period=60)
async def background_task():
	log.debug("Background task is running")
	# your code here...
```
This will run `background_task()` every 60 seconds, until the bot is shut down.

####Other events
What's listed above curently covers all the events implemented in the current version of this framework, however as time
goes by the rest of the events will be added as well. If you desire an event for something that's not here, please feel
free to send a PR or an issue with your request. 

###Sample
An active, in-use sample of this framework can be found at 
[young-amateurs-rc/arbys](https://github.com/young-amateurs-rc/arbys), 
my Discord bot for the Young Hams community.