from client import client
import discord


cmd_name = "unmorse"

client.basic_help(title=cmd_name, desc="reverses a Morse Code message back into text")

detailed_help = {
	"Usage": f"{client.default_prefix}{cmd_name}",
	"Description": "This command takes a given Morse Code string and reverts it back to text. Spaces denote separate letters and spaces with slashes denote separate words.",
}
client.long_help(cmd=cmd_name, mapping=detailed_help)

morse_lookup = {
	"A": ".-",
	"B": "-...",
	"C": "-.-.",
	"D": "-..",
	"E": ".",
	"F": "..-.",
	"G": "--.",
	"H": "....",
	"I": "..",
	"J": ".---",
	"K": "-.-",
	"L": ".-..",
	"M": "--",
	"N": "-.",
	"O": "---",
	"P": ".--.",
	"Q": "--.-",
	"R": ".-.",
	"S": "...",
	"T": "-",
	"U": "..-",
	"V": "...-",
	"W": ".--",
	"X": "-..-",
	"Y": "-.--",
	"Z": "--..",
	"0": "-----",
	"1": ".----",
	"2": "..---",
	"3": "...--",
	"4": "....-",
	"5": ".....",
	"6": "-....",
	"7": "--...",
	"8": "---..",
	"9": "----.",
	",": "--..--",
	".": ".-.-.-",
	"?": "..--..",
	";": "-.-.-",
	":": "---...",
	"/": "-..-.",
	"+": ".-.-.",
	"-": "-....-",
	"=": "-...-",
	"(": "-.--.",
	")": "-.--.-",
	" ": "/",
}

unmorse_lookup = {y: x for x, y in morse_lookup.items()}


@client.command(trigger=cmd_name, aliases=[])  # aliases is a list of strs of other triggers for the command
async def handler(command: str, message: discord.Message):
	msg = command[8:]
	result = ''
	msg = msg.split('/')
	msg = [m.split() for m in msg]
	for word in msg:
		for char in word:
			try:
				result += unmorse_lookup[char]
			except:
				result += '<?>'
		result += " "


	result += ' '
	await message.channel.send(result)
	return
