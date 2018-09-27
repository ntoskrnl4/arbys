from client import client
import discord


cmd_name = "morse"

client.basic_help(title=cmd_name, desc="converts a given string to morse code")

detailed_help = {
	"Usage": f"{client.default_prefix}{cmd_name} <string>",
	"Arguments": "`<string>` - the string to convert to morse code",
	"Description": "This command converts a given string into morse code. Works with letters, numbers, and some punctuation.",
	# NO Aliases field, this will be added automatically!
}
client.long_help(cmd=cmd_name, mapping=detailed_help)

morse_lookup = {
	"A": "  .-",
	"B": "  -...",
	"C": "  -.-.",
	"D": "  -..",
	"E": "  .",
	"F": "  ..-.",
	"G": "  --.",
	"H": "  ....",
	"I": "  ..",
	"J": "  .---",
	"K": "  -.-",
	"L": "  .-..",
	"M": "  --",
	"N": "  -.",
	"O": "  ---",
	"P": "  .--.",
	"Q": "  --.-",
	"R": "  .-.",
	"S": "  ...",
	"T": "  -",
	"U": "  ..-",
	"V": "  ...-",
	"W": "  .--",
	"X": "  -..-",
	"Y": "  -.--",
	"Z": "  --..",
	"0": "  -----",
	"1": "  .----",
	"2": "  ..---",
	"3": "  ...--",
	"4": "  ....-",
	"5": "  .....",
	"6": "  -....",
	"7": "  --...",
	"8": "  ---..",
	"9": "  ----.",
	",": "  --..--",
	".": "  .-.-.-",
	"?": "  ..--..",
	";": "  -.-.-",
	":": "  ---...",
	"/": "  -..-.",
	"+": "  .-.-.",
	"-": "  -....-",
	"=": "  -...-",
	"(": "  -.--.",
	")": "  -.--.-",
	" ": "  /",
}


@client.command(trigger=cmd_name)
async def command(command: str, message: discord.Message):
	string = command[6:]
	new_str = "".join([morse_lookup.get(x, "  <?>") for x in string.upper()])
	await message.channel.send(new_str)
	return