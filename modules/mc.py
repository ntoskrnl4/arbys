# mc.py a command for fetching details about a minecraft server

from client import client

import asyncio
import base64
import datetime
import discord
import io
import json
import log
import random
import socket
import struct


SERVER_URL = "mc.usu.xyz"  # Port is default 25565
COMMAND_TRIGGER = "mc"  # "mc" default

# Following classes are forked/edited from Dinnerbone/mcstatus


class Connection:
    def __init__(self):
        self.sent = bytearray()
        self.received = bytearray()

    def read(self, length):
        result = self.received[:length]
        self.received = self.received[length:]
        return result

    def write(self, data):
        if isinstance(data, Connection):
            data = bytearray(data.flush())
        if isinstance(data, str):
            data = bytearray(data)
        self.sent.extend(data)

    def receive(self, data):
        if not isinstance(data, bytearray):
            data = bytearray(data)
        self.received.extend(data)

    def remaining(self):
        return len(self.received)

    def flush(self):
        result = self.sent
        self.sent = ""
        return result

    def _unpack(self, format, data):
        return struct.unpack(">" + format, bytes(data))[0]

    def _pack(self, format, data):
        return struct.pack(">" + format, data)

    def read_varint(self):
        result = 0
        for i in range(5):
            part = ord(self.read(1))
            result |= (part & 0x7F) << 7 * i
            if not part & 0x80:
                return result
        raise IOError("Server sent a varint that was too big!")

    def write_varint(self, value):
        remaining = value
        for i in range(5):
            if remaining & ~0x7F == 0:
                self.write(struct.pack("!B", remaining))
                return
            self.write(struct.pack("!B", remaining & 0x7F | 0x80))
            remaining >>= 7
        raise ValueError("The value %d is too big to send in a varint" % value)

    def read_utf(self):
        length = self.read_varint()
        return self.read(length).decode('utf8')

    def write_utf(self, value):
        self.write_varint(len(value))
        self.write(bytearray(value, 'utf8'))

    def read_ascii(self):
        result = bytearray()
        while len(result) == 0 or result[-1] != 0:
            result.extend(self.read(1))
        return result[:-1].decode("ISO-8859-1")

    def write_ascii(self, value):
        self.write(bytearray(value, 'ISO-8859-1'))
        self.write(bytearray.fromhex("00"))

    def read_short(self):
        return self._unpack("h", self.read(2))

    def write_short(self, value):
        self.write(self._pack("h", value))

    def read_ushort(self):
        return self._unpack("H", self.read(2))

    def write_ushort(self, value):
        self.write(self._pack("H", value))

    def read_int(self):
        return self._unpack("i", self.read(4))

    def write_int(self, value):
        self.write(self._pack("i", value))

    def read_uint(self):
        return self._unpack("I", self.read(4))

    def write_uint(self, value):
        self.write(self._pack("I", value))

    def read_long(self):
        return self._unpack("q", self.read(8))

    def write_long(self, value):
        self.write(self._pack("q", value))

    def read_ulong(self):
        return self._unpack("Q", self.read(8))

    def write_ulong(self, value):
        self.write(self._pack("Q", value))

    def read_buffer(self):
        length = self.read_varint()
        result = Connection()
        result.receive(self.read(length))
        return result

    def write_buffer(self, buffer):
        data = buffer.flush()
        self.write_varint(len(data))
        self.write(data)


class TCPSocketConnection(Connection):
    def __init__(self, addr, timeout=3):
        Connection.__init__(self)
        self.socket = socket.create_connection(addr, timeout=timeout)

    def flush(self):
        raise TypeError("TCPSocketConnection does not support flush()")

    def receive(self, data):
        raise TypeError("TCPSocketConnection does not support receive()")

    def remaining(self):
        raise TypeError("TCPSocketConnection does not support remaining()")

    def read(self, length):
        result = bytearray()
        while len(result) < length:
            new = self.socket.recv(length - len(result))
            if len(new) == 0:
                raise IOError("Server did not respond with any information!")
            result.extend(new)
        return result

    def write(self, data):
        self.socket.send(data)

    def __del__(self):
        try:
            self.socket.close()
        except:
            log.warning("Could not close socket for unknown reason", include_exception=True)
            pass


class UDPSocketConnection(Connection):
    def __init__(self, addr, timeout=3):
        Connection.__init__(self)
        self.addr = addr
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.settimeout(timeout)

    def flush(self):
        raise TypeError("UDPSocketConnection does not support flush()")

    def receive(self, data):
        raise TypeError("UDPSocketConnection does not support receive()")

    def remaining(self):
        return 65535

    def read(self, length):
        result = bytearray()
        while len(result) == 0:
            result.extend(self.socket.recvfrom(self.remaining())[0])
        return result

    def write(self, data):
        if isinstance(data, Connection):
            data = bytearray(data.flush())
        self.socket.sendto(data, self.addr)

    def __del__(self):
        try:
            self.socket.close()
        except:
            log.warning("Could not close socket for unknown reason", include_exception=True)
            pass


class ServerPinger:
    def __init__(self, connection, host="", port=0, version=47, ping_token=None):
        if ping_token is None:
            ping_token = random.randint(0, (1 << 63) - 1)
        self.version = version
        self.connection = connection
        self.host = host
        self.port = port
        self.ping_token = ping_token

    def handshake(self):
        packet = Connection()
        packet.write_varint(0)
        packet.write_varint(self.version)
        packet.write_utf(self.host)
        packet.write_ushort(self.port)
        packet.write_varint(1)  # Intention to query status

        self.connection.write_buffer(packet)

    def read_status(self):
        request = Connection()
        request.write_varint(0)  # Request status
        self.connection.write_buffer(request)

        response = self.connection.read_buffer()
        if response.read_varint() != 0:
            raise IOError("Received invalid status response packet.")
        try:
            raw = json.loads(response.read_utf())
        except ValueError:
            raise IOError("Received invalid JSON")
        try:
            return PingResponse(raw)
        except ValueError as e:
            raise IOError("Received invalid status response: %s" % e)

    def test_ping(self):
        request = Connection()
        request.write_varint(1)  # Test ping
        request.write_long(self.ping_token)
        sent = datetime.datetime.now()
        self.connection.write_buffer(request)

        response = self.connection.read_buffer()
        received = datetime.datetime.now()
        if response.read_varint() != 1:
            raise IOError("Received invalid ping response packet.")
        received_token = response.read_long()
        if received_token != self.ping_token:
            raise IOError("Received mangled ping response packet (expected token %d, received %d)" % (
                self.ping_token, received_token))

        delta = (received - sent)

        return (delta.total_seconds() * 1000)


class PingResponse:
    class Players:
        class Player:
            def __init__(self, raw):
                if type(raw) is not dict:
                    raise ValueError("Invalid player object (expected dict, found %s" % type(raw))

                if "name" not in raw:
                    raise ValueError("Invalid player object (no 'name' value)")
                if not isinstance(raw["name"], str):
                    raise ValueError("Invalid player object (expected 'name' to be str, was %s)" % type(raw["name"]))
                self.name = raw["name"]

                if "id" not in raw:
                    raise ValueError("Invalid player object (no 'id' value)")
                if not isinstance(raw["id"], str):
                    raise ValueError("Invalid player object (expected 'id' to be str, was %s)" % type(raw["id"]))
                self.id = raw["id"]

        def __init__(self, raw):
            if type(raw) is not dict:
                raise ValueError("Invalid players object (expected dict, found %s" % type(raw))

            if "online" not in raw:
                raise ValueError("Invalid players object (no 'online' value)")
            if type(raw["online"]) is not int:
                raise ValueError("Invalid players object (expected 'online' to be int, was %s)" % type(raw["online"]))
            self.online = raw["online"]

            if "max" not in raw:
                raise ValueError("Invalid players object (no 'max' value)")
            if type(raw["max"]) is not int:
                raise ValueError("Invalid players object (expected 'max' to be int, was %s)" % type(raw["max"]))
            self.max = raw["max"]

            if "sample" in raw:
                if type(raw["sample"]) is not list:
                    raise ValueError("Invalid players object (expected 'sample' to be list, was %s)" % type(raw["max"]))
                self.sample = [self.Player(p) for p in raw["sample"]]
            else:
                self.sample = None

    class Version:
        def __init__(self, raw):
            if type(raw) is not dict:
                raise ValueError("Invalid version object (expected dict, found %s" % type(raw))

            if "name" not in raw:
                raise ValueError("Invalid version object (no 'name' value)")
            if not isinstance(raw["name"], str):
                raise ValueError("Invalid version object (expected 'name' to be str, was %s)" % type(raw["name"]))
            self.name = raw["name"]

            if "protocol" not in raw:
                raise ValueError("Invalid version object (no 'protocol' value)")
            if type(raw["protocol"]) is not int:
                raise ValueError("Invalid version object (expected 'protocol' to be int, was %s)" % type(raw["protocol"]))
            self.protocol = raw["protocol"]

    def __init__(self, raw):
        self.raw = raw

        if "players" not in raw:
            raise ValueError("Invalid status object (no 'players' value)")
        self.players = self.Players(raw["players"])

        if "version" not in raw:
            raise ValueError("Invalid status object (no 'version' value)")
        self.version = self.Version(raw["version"])

        if "description" not in raw:
            raise ValueError("Invalid status object (no 'description' value)")
        self.description = raw["description"]

        if "favicon" in raw:
            self.favicon = raw["favicon"]
        else:
            self.favicon = None

        self.latency = None


class MinecraftServer:
    def __init__(self, host, port=25565):
        self.host = host
        self.port = port

    @staticmethod
    def lookup(address):
        host = address
        port = None
        if ":" in address:
            parts = address.split(":")
            if len(parts) > 2:
                raise ValueError("Invalid address '%s'" % address)
            host = parts[0]
            port = int(parts[1])
        if port is None:
            port = 25565

        return MinecraftServer(host, port)

    def status(self, retries=3, **kwargs):
        connection = TCPSocketConnection((self.host, self.port))
        exception = None
        for attempt in range(retries):
            try:
                pinger = ServerPinger(connection, host=self.host, port=self.port, **kwargs)
                pinger.handshake()
                result = pinger.read_status()
                result.latency = pinger.test_ping()
                return result
            except Exception as e:
                exception = e
            finally:
                asyncio.sleep(2)  # Sleep between tries since the attempt blocks for 3 seconds
        else:
            raise exception

@client.command(trigger=COMMAND_TRIGGER)
async def mc(ctx, message: discord.Message):
    async with message.channel.typing():
        server = MinecraftServer.lookup(SERVER_URL) # Instantiate MinecraftServer class from SERVER_URL
        status = server.status() # Get status, including icon, user count, usernames, etc

        players = [] # Players on the server

        latency = int(status.latency)
        version = status.raw["version"]["name"]
        onlineplayercount = status.raw["players"]["online"]
        maxplayercount =  status.raw["players"]["max"]

        description = f"\n**Latency:** {latency}ms\n**Version:** {version}\n**Players:** {onlineplayercount}/{maxplayercount}"

        buffer = io.BytesIO(base64.b64decode(status.favicon.split(",")[1])) # Decode base64 icon and turn the data into a BytesIO

        servertitle = status.description["text"]
        serverurl = SERVER_URL

        embed = discord.Embed(color=0x3D69DE, title=f"**{servertitle}**\n{serverurl}", description=description) # Create embed
        embed.set_thumbnail(url="attachment://icon.png")

        if status.raw["players"]["online"] > 0: # If players are online create players field
            for player in status.raw["players"]["sample"]:
                players.append(player["name"])
            embed.add_field(name="Players", value="\n".join(players))
        
        file = discord.File(fp=buffer, filename="icon.png")
    await message.channel.send(file=file, embed=embed) # Send embed
