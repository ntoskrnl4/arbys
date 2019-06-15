from client import client
from collections import defaultdict
from datetime import datetime
from exceptions import BaseFrameworkError
from typing import Union, Dict, List

import asyncio
import discord
import json
import key
import log
import os
import random
import socket
import time
import urllib
import youtube_dl


detailed_help = {
	"Usage": f"{client.default_prefix}music <subcommand> [args]",
	"Arguments": "`subcommand` - subcommand to run\n`args` - (optional) arguments specific to the subcommand being run",
	"Description": "This command manages music related functionality within the bot. Music is available to several servers at once.",
	"Subcommands": f"`{client.default_prefix}music join` - Joins a voice channel\n"
					f"`{client.default_prefix}music add <url>` - Adds the specified song to the queue\n"
					f"`{client.default_prefix}music play` - Plays music in the queue\n"
					f"`{client.default_prefix}music pause` - Toggles pause\n"
					f"`{client.default_prefix}music playing` - Shows what is currently playing\n"
					f"`{client.default_prefix}music skip` - Skips the currently playing song\n"
					f"`{client.default_prefix}music queue` - Shows the current music queue\n"
					f"`{client.default_prefix}music info [index]` - Shows song information for the specified song in the queue\n"
					f"`{client.default_prefix}music volume <volume>` - Sets the music volume, on a scale of 0.0-2.0\n"
					f"`{client.default_prefix}music exit` - Exits the channel (also aliased to `stop` and `quit`)\n",
}
client.long_help(cmd="music", mapping=detailed_help)

voice_enable = False
access_lock = asyncio.Lock()
song_info_embed_colour = 0xbf35e3
playlist_dir = "playlists/"

cooldown: Dict[int, datetime] = defaultdict(lambda: datetime(1970, 1, 1, 0, 0, 0, 0))
guild_channel: Dict[int, discord.TextChannel] = {}
guild_queue: Dict[int, List["Song"]] = defaultdict(list)
guild_now_playing_song: Dict[int, "Song"] = {}
guild_volume: Dict[int, float] = defaultdict(lambda: float(1.0))
active_clients: Dict[int, discord.VoiceClient] = {}


class EmptySource(discord.AudioSource):
	used = False

	def is_opus(self):
		return False

	def read(self):
		if not self.used:
			self.used = True
			return b"\x00"*3840
		else:
			return b""


class MusicException(BaseFrameworkError):
	pass


class NotConnectedException(MusicException):
	pass


class TrackingVolumeTransformer(discord.PCMVolumeTransformer):
	def __init__(self, *args, **kwargs):
		self.timer = 0
		self.reads = 0
		super().__init__(*args, **kwargs)

	def read(self):
		self.reads += 1
		if self.reads % 50 is 0:
			self.timer += 1
		return super().read()


class Song:
	def __init__(self, url: str, title: str = None, duration: int = None, requester: str = "<unknown requester>", noload: bool = False):
		self.submitted_url = url

		if not noload:
			with youtube_dl.YoutubeDL({"format": "bestaudio", "noplaylist": True}) as session:
				data = session.extract_info(download=False, url=url)
				# get url from the data dict. if it's a youtube link then you need to check for the best format url too
			if title is None:
				self.title = data.get("title", "<no title>")
			if duration is None:
				self.duration = data.get("duration", 0)
			formats = data.get("formats", None)
			if formats is None:
				log.error("no formats found????")
				self.media_url = ""
			else:
				self.media_url = formats[0].get("url", "")

			if self.submitted_url.endswith(".flac"):
				data = get_flac_data(self.submitted_url)
				self.title = data["title"]
				self.duration = data["duration"]

			self.loaded = True

		if noload:
			self.media_url = ""
			self.title = title if title is not None else "<song data not loaded>"
			self.duration = duration if duration is not None else 0
			self.loaded = False

		self.requester = requester
		self.source = None

	def load(self):
		with youtube_dl.YoutubeDL({"format": "bestaudio", "noplaylist": True}) as session:
			data = session.extract_info(download=False, url=self.submitted_url)
		# get url from the data dict. if it's a youtube link then you need to check for the best format url too
		self.title = data.get("title", "<no title>")
		self.duration = data.get("duration", 0)
		formats = data.get("formats", None)
		if formats is None:
			log.error("no formats found????")
			self.media_url = ""
		else:
			self.media_url = formats[0].get("url", "")
		self.loaded = True

	def get_source(self, guild_id: int):
		"""Get an AudioSource object for the song."""
		if self.source is not None: return self.source
		self.source = TrackingVolumeTransformer(discord.FFmpegPCMAudio(self.media_url), volume=guild_volume[guild_id])
		return self.source

	@property
	def depth(self):
		return getattr(self.source, "timer", 0)


async def confirm(message, fallback: str = None) -> bool:
	try:
		await message.add_reaction("")
	except discord.errors.Forbidden:
		pass
	else:
		return True

	if fallback is None:
		return False
	# now still executing only if the above failed
	try:
		await message.channel.send(fallback)
	except discord.errors.Forbidden:
		return False  # we weren't able to send any feedback to the user at all
	else:
		return True


def get_flac_data(url: str):
	try:
		url = urllib.parse.urlparse(url)
		ip = url.hostname
		port = url.port
		filename = url.path
		try:
			remote = socket.create_connection((ip, port), timeout=1.0)
		except:
			log.warning("Could not connect to retrieve FLAC header")
			return
		req = b"GET filename HTTP/1.1\r\n\r\n"
		req = req.replace(b"filename", filename.encode())
		remote.send(req)
		time.sleep(0.01)
		data_in = remote.recv(256)
		flac_beginning = data_in[data_in.index(b"fLaC"):]

		raw = bytearray(flac_beginning)
		# now we can start bitparsing the header by hand

		# header_length = int((raw[5] << 16) | (raw[6] << 8) | raw[7])
		# min_blocksize = int((raw[8] << 8) | raw[9])
		# max_blocksize = int((raw[10] << 8) | raw[11])
		# min_framesize = int((raw[12] << 16) | (raw[13] << 8) | raw[14])
		# max_framesize = int((raw[15] << 16) | (raw[16] << 8) | raw[17])
		sample_rate = int(bin((raw[18] << 16) | (raw[19] << 8) | raw[20])[2:-4], base=2)
		# num_channels = ((raw[20] & 0b00001110) >> 1) + 1
		# bits_per_sample = ((raw[20]&1) << 4) | (raw[21] >> 4) + 1
		num_samples = (((raw[21] & 0xF) << 32) | (raw[22] << 24) | (raw[23] << 16) | (raw[24] << 8) | raw[25])
		length_sec = num_samples / sample_rate
		return {
			"title": filename[1:].replace(".flac", ""),
			"duration": int(length_sec)
		}
	except:
		return None


def check_if_user_in_channel(channel: discord.VoiceChannel, user: Union[discord.User, int]) -> bool:
	return getattr(user, "id", user) in [x.id for x in channel.members]


def get_song_embed(song, is_next: bool = False, queue_position: int = None, is_paused: bool = False):
	if not song.loaded: song.load()
	if is_next:
		embed = discord.Embed(title="Now Playing", description=discord.Embed.Empty, colour=song_info_embed_colour)
	else:
		position = f"Queue position {queue_position}" if queue_position is not None else discord.Embed.Empty
		embed = discord.Embed(title="Song Info", description=position, colour=song_info_embed_colour)

	duration = "<length unknown>" if song.duration is 0 else f"{song.duration//60}:{'0' if song.duration%60 < 10 else ''}{song.duration%60}"
	through = f"{song.depth//60}:{'0' if song.depth%60 < 10 else ''}{song.depth%60} / {duration} {'paused' if is_paused else ''}"

	embed = embed.add_field(name="Title", value=song.title, inline=True)
	embed = embed.add_field(name="Duration", value=through, inline=True)
	embed = embed.add_field(name="Requester", value=song.requester, inline=True)
	embed = embed.add_field(name="Reference", value=song.submitted_url, inline=False)
	embed = embed.set_footer(text=datetime.utcnow().__str__())
	return embed


def get_target_voice_connection(object: Union[discord.Member, discord.Guild, discord.VoiceChannel, int]) -> Union[discord.VoiceClient, MusicException]:
	target = None

	if isinstance(object, discord.Member):
		target = getattr(object.voice, "channel", None)
	if isinstance(object, discord.Guild):
		target = getattr(discord.utils.find(lambda x: x.guild.id == object.id, client.voice_clients), "channel", None)
	if isinstance(object, discord.VoiceChannel):
		target = object

	if isinstance(object, int):
		# seriously :/
		log.warning("get_target_voice_channel() given a raw integer/ID; this probably should not happen but I'll try my best")

		channel = client.get_channel(object)
		guild = client.get_guild(object)
		if isinstance(guild, discord.Guild):
			target = discord.utils.find(lambda x: x.id == object, client.voice_clients).channel

		elif isinstance(channel, discord.VoiceChannel):
			target = channel

		else:
			target = None

	if not isinstance(target, discord.VoiceChannel):
		return None
	# now we know that target is a VoiceChannel
	if not check_if_user_in_channel(target, client.user.id):
		# if we're not in the channel
		return NotConnectedException("We're not currently connected to this voice channel")
	else:
		return discord.utils.find(lambda x: x.channel.id == target.id, client.voice_clients)


def get_queue_list(queue, length=20):
	info = f"Next {length if len(queue) > length else len(queue)} items in queue:\n"
	i = 1
	for song in queue[:length]:
		duration = "length unknown" if song.duration is 0 else f"{song.duration//60}m{song.duration%60}s"
		info += f"`{'0' if (len(queue) > 9) and (i < 10) else ''}" \
				f"{i}:` " \
				f"{song.title} ({duration}) (requested by {song.requester})\n"
		i += 1
	if len(info) > 2048:
		return get_queue_list(queue=queue, length=length-1)  # crossing fingers we don't get any issues
	else:
		return info


@client.command(trigger="music")
async def command(command: str, message: discord.Message):
	global guild_channel, guild_now_playing_song, guild_queue, guild_volume, active_clients, access_lock

	if message.guild.id == 364480908528451584:
		await message.channel.send(client.unknown_command)
		return

	if not voice_enable:
		await message.channel.send("Sorry, but the internal Opus library required for voice support was not loaded for whatever reason, and music functionality will not work.")
		return

	if message.author.id in key.music_blacklist:
		await message.channel.send("Command refused: You are not permitted to use this command")
		return

	parts = command.split(" ")
	# parts: music subcmd args args args

	# commands:
	# music join [channel_id]
	# music add <reference>
	# music play
	# music skip
	# music pause (toggle)
	# music volume <float>
	# music queue
	# music info [position in queue (else get now playing)]
	# music playing (like above but only for now playing)
	# music exit/quit/stop

	try:
		parts[1] = parts[1].lower()
	except IndexError:
		await message.channel.send("Subcommand not given. See command help for available subcommands.")
		return

	if not parts[1] in ["join", "add", "play", "skip", "pause", "volume", "queue", "info", "playing", "exit", "stop", "quit", "load", "remove"]:
		await message.channel.send("Unknown subcommand (see command help for available subcommands)")
		return

	# start playing music for them
	if parts[1] == "play":
			# todo: if paused, resume instead
			vc = get_target_voice_connection(message.guild)
			if not isinstance(vc, discord.VoiceClient):
				await message.channel.send("Cannot play music: not connected to any voice channel")
				return
			if not check_if_user_in_channel(vc.channel, message.author.id):
				try:
					await message.add_reaction("❌")
				except:
					try:
						await message.channel.send("Command refused: you are not in the target channel")
					except:
						pass
				finally:
					return
			if len(guild_queue[message.guild.id]) is 0:
				await message.channel.send("Queue empty: nothing to play")
				return

			if vc.is_playing():
				# we're already playing something
				vc = get_target_voice_connection(message.guild)
				if not isinstance(vc, discord.VoiceClient):
					await message.channel.send("Cannot unpause music: not currently connected to any voice channel")
					return
				if not check_if_user_in_channel(vc.channel, message.author.id):
					await message.channel.send("Command refused: you are not in the target voice channel")
					return
				vc.resume()

			while True:
				try:
					next_up = guild_queue[message.guild.id].pop(0)
					guild_now_playing_song[message.guild.id] = next_up
					await message.channel.send(embed=get_song_embed(next_up, is_next=True))
					vc.play(next_up.get_source(message.guild.id))
				except IndexError:
					if isinstance(get_target_voice_connection(message.guild), discord.VoiceClient):
						await message.channel.send("Queue exhausted: stopping music playback")
					return
				except Exception as e:
					if isinstance(e, IndexError): return
					log.error("Unexpected error during music playback", include_exception=True)
					await message.channel.send("Sorry, there was an unexpected error while playing music.")
					await vc.disconnect(force=True)
					del guild_now_playing_song[message.guild.id]
				else:
					while vc.is_playing() or vc.is_paused():
						try:
							await asyncio.sleep(1)
						except:
							pass

	async with access_lock:
		# join their voice channel
		if parts[1] == "join":
			connection = get_target_voice_connection(message.author)
			if connection is None:
				# user's not in a channel
				connection = get_target_voice_connection(message.guild)
				if connection is None:
					# we're not in a channel either
					# cool, we have no idea what channel they want us to join to
					await message.channel.send("Cannot join channel: Ambiguous/unknown target channel - please join the target voice channel")
					return
				else:
					# user's not in a channel but we are already in a channel
					await message.channel.send("Cannot join channel: Already in a channel (also, next time please join the channel you are referring to first)")
					return
			if isinstance(connection, MusicException):
				# user is in there but we're not
				if isinstance(get_target_voice_connection(message.guild), discord.VoiceClient):
					await message.channel.send("Cannot join channel: already in another channel in this server")
					return

				user_state = message.author.voice
				if user_state is None:
					await message.channel.send("error: user voice status changed between two subsequent calls to retrieve user's channel")
					return

				channel_perms = user_state.channel.permissions_for(message.guild.me)
				if not channel_perms.connect:
					await message.channel.send("Cannot join channel: insufficient permissions to connect to the channel")
					return
				if channel_perms.connect and not channel_perms.speak:
					await message.channel.send("Refusing to join channel: insufficient permissions to send voice data in target channel")
					return

				try:
					new_connection = await message.author.voice.channel.connect(timeout=5.0)
				except discord.errors.ClientException:
					# d.py said we weren't in a channel but we were >:( damn liar
					await asyncio.sleep(0.1)
					try:
						new_connection = await message.author.voice.channel.connect(timeout=5.0)
					except discord.errors.ClientException:
						# ahhh, just give up
						await message.channel.send("Cannot join channel: Unknown internal error (sorry...)")
						return

				active_clients[message.guild.id] = new_connection
				new_connection.play(EmptySource())  # Attempt to clear transmitting on join bug
				new_connection.stop()
				await confirm(message, "Joined the channel")
				return
			if isinstance(connection, discord.VoiceClient):
				# we're in the channel with them
				await message.channel.send("Already in this channel with you")
				return

		# add a new song to the queue
		if parts[1] == "add":
			try:
				parts[2]
			except IndexError:
				await message.channel.send("Cannot add song to queue: no song given to add")

			url = command.replace("music add ", "", 1)

			try:
				song = Song(url=url, requester=message.author.mention)
			except Exception:
				await message.channel.send("Error getting song information: song not added to queue")
				# log.warning("Unable to add song", include_exception=True)  disabled because it kinda spams the log a bit
				return

			# todo: add warning for sending links with playlists, that they will not get added

			guild_queue[message.guild.id].append(song)
			await message.channel.send("Song added to end of queue:", embed=get_song_embed(song, queue_position=len(guild_queue[message.guild.id])))
			return

		# skip the current song
		if parts[1] == "skip":
			vc = get_target_voice_connection(message.guild)
			if not isinstance(vc, discord.VoiceClient):
				await message.channel.send("Cannot skip song: not currently connected to any voice channel")
				return
			if not check_if_user_in_channel(vc.channel, message.author.id):
				await message.channel.send("Command refused: you are not in the target channel")
				return
			vc.stop()
			await confirm(message)

		# pause the current song (toggle)
		if parts[1] == "pause":
			vc = get_target_voice_connection(message.guild)
			if not isinstance(vc, discord.VoiceClient):
				await message.channel.send("Cannot pause music: not currently connected to any voice channel")
				return
			if not check_if_user_in_channel(vc.channel, message.author.id):
				await message.channel.send("Command refused: you are not in the target voice channel")
				return
			if vc.is_paused():
				vc.resume()
				await message.channel.send("Paused music playback", delete_after=15)
			else:
				vc.pause()
				await message.channel.send("Resumed music playback", delete_after=15)

		# change the volume
		if parts[1] == "volume":
			try:
				new_vol = float(parts[2])
				if message.author.id == 389415987402899459 and new_vol > 0.4:
					await message.channel.send("not happening")
					return
			except ValueError:
				await message.channel.send(f"That's not a float. (got: {parts[2]})")
				return
			except IndexError:
				await message.channel.send("New volume not supplied. See command help for help.")
				return

			vc = get_target_voice_connection(message.guild)
			if vc is not None:
				if not check_if_user_in_channel(vc.channel, message.author):
					await message.channel.send("Command refused: you are not in the target voice channel")
					await message.add_reaction("❌")
					return
			try:
				vc.source.volume = new_vol
			except:
				pass
			finally:
				guild_volume[message.guild.id] = new_vol
				await confirm(message, f"Successfully changed the volume to {new_vol}")

		# see the queue
		if parts[1] == "queue":
			try:
				if parts[2] == "--clear":
					guild_queue[message.guild.id] = []
					return
			except IndexError:
				pass
			embed = discord.Embed(title="Upcoming Music Queue", description=get_queue_list(guild_queue.get(message.guild.id, [])), colour=discord.Embed.Empty)
			currently_playing = guild_now_playing_song.get(message.guild.id, None)
			if currently_playing is not None:
				embed = embed.add_field(name="Currently Playing", value=currently_playing.title)
			embed = embed.set_footer(text=datetime.utcnow().__str__())
			await message.channel.send(embed=embed)
			return

		# see information about a song in the queue
		if parts[1] == "info":
			if not isinstance(get_target_voice_connection(message.guild), discord.VoiceClient):
				await message.channel.send("Not currently connected to voice chat")
				return
			try:
				parts[2]
			except IndexError:
				target_song = guild_now_playing_song.get(message.guild.id, None)
				if target_song is None:
					await message.channel.send("Cannot get song information: no song is currently playing and no queue index specified")
					return
				else:
					await message.channel.send(embed=get_song_embed(target_song, is_next=True, is_paused=get_target_voice_connection(message.guild).is_paused()))
					return

			try:
				index = int(parts[2])
			except ValueError:
				await message.channel.send(f"Cannot get song info: noninteger queue index (got: {parts[2]})")
				return

			try:
				target_song = guild_queue.get(message.guild.id, [])[index-1]
			except IndexError:
				await message.channel.send(f"Cannot get song info: invalid queue index (queue is shorter than index provided?)")
				return

			await message.channel.send(embed=get_song_embed(target_song, queue_position=index))

		# see information about what is currently playing
		if parts[1] == "playing":
			if not isinstance(get_target_voice_connection(message.guild), discord.VoiceClient):
				await message.channel.send("Not currently connected to voice chat")
				return
			target_song = guild_now_playing_song.get(message.guild.id, None)
			if target_song is None:
				await message.channel.send("Not currently playing any song")
				return
			else:
				await message.channel.send(embed=get_song_embed(target_song, is_next=True, is_paused=get_target_voice_connection(message.guild).is_paused()))
				return

		# bye
		if parts[1] in ["exit", "stop", "quit"]:
			try:
				all = (parts[2] == "--force-all")
			except IndexError:
				all = False
			vc = get_target_voice_connection(message.guild)
			if not isinstance(vc, discord.VoiceClient):
				await message.channel.send("Cannot disconnect from voice channel: not connected to any voice channel in this server")
				return
			if vc.channel.members != [vc.guild.me]:
				if not check_if_user_in_channel(vc.channel, message.author.id):
					await message.channel.send("Command refused: you are not in the target voice channel")
					return
			if not all:
				await vc.disconnect(force=True)
				try:
					del guild_now_playing_song[message.guild.id]
				except KeyError:
					# no song was ever actually played while in VC. lmao ok
					pass
			if all:
				for vc in client.voice_clients:
					if vc.guild.id == message.guild.id:
						await vc.disconnect(force=True)
			try:
				parts[2]
			except IndexError:
				clear_queue = True
			else:
				clear_queue = parts[2] not in ["--no-clear-queue", "-n"]
			if clear_queue:
				guild_queue[message.guild.id] = []

		# load a queue from a json file
		if parts[1] == "load":
			force_randomize = "--force-randomize" in command
			no_force_randomize = "--no-force-randomize" in command
			if force_randomize and no_force_randomize:
				await message.channel.send("Argument error: both --force-randomize and --no-force-randomize passed as arguments")
				return

			command = command.replace(" --force-randomize", "")
			command = command.replace(" --no-force-randomize", "")

			parts = command.split(" ")

			try:
				parts[2]
			except IndexError:
				await message.channel.send("Cannot load playlist: no playlist specified. See command help or source code for help.")
				return

			target_filename = f"{parts[2]}.json"
			if target_filename not in os.listdir(playlist_dir):
				await message.channel.send("Cannot load playlist: no such playlist exists")
				return

			try:
				data = json.load(open(playlist_dir+target_filename, "r"))
			except Exception as e:
				log.error("Error loading playlist:", include_exception=True)
				await message.channel.send(f"Cannot load playlist: unexpected exception loading playlist: {e.__class__.__name__}: {''.join(e.args)}\n\nThis exception has been logged.")
				return

			loaded_playlist = data['playlist']
			if "--no-extend" not in command:
				for i in range(data['exponential_extend_iter']):
					loaded_playlist.extend(loaded_playlist)
			if (data['randomize'] or force_randomize) and not no_force_randomize:
				random.shuffle(loaded_playlist)

			playlist_objects = []
			errored = False
			i = 0
			for song in loaded_playlist:
				playlist_objects.append(Song(url=song,
											requester=f"{message.author.mention} from playlist \"{parts[2]}.json\"",
											noload=False if i < 3 else True))
				i += 1

			current_queue = guild_queue[message.guild.id]
			if current_queue is None:
				guild_queue[message.guild.id] = []
			guild_queue[message.guild.id].extend(playlist_objects)
			await message.channel.send(f"Loaded {len(playlist_objects)} from playlist `{parts[2]}.json`")

		# purge queue
		if parts[1] == "clear":
			guild_queue[message.guild.id] = []
			return

		# remove (element) from queue or clear queue
		if parts[1] == "remove":
			vc = get_target_voice_connection(message.guild)
			if vc is not None:
				# we're in a channel
				if not check_if_user_in_channel(vc.channel, message.author.id):
					await message.channel.send("Command refused: you are not in the target voice channel")
					return
			try:
				parts[2]
			except IndexError:
				await message.channel.send("Argument error: no queue index to remove")
				return

			clear_all = parts[2] in ["-c", "--clear", "--clear-all"]
			if clear_all:
				guild_queue[message.guild.id] = []
				return

			try:
				index = int(parts[2])
			except ValueError:
				await message.channel.send(f"Cannot remove song from queue: invalid integer index (got: {parts[2]})")
				return

			guild_queue[message.guild.id].pop(index-1)

@client.ready
async def music_capable_check():
	global voice_enable
	if discord.opus.is_loaded():
		voice_enable = True
	else:
		voice_enable = False
		log.warning("Voice library not loaded for some unknown reason. Music functionality will not work.")


@client.shutdown
async def exit_all_vcs():
	for vc in client.voice_clients:
		await vc.disconnect()
