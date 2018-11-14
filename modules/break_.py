from client import client
import discord

client.basic_help(title="break", desc="Breaks the bot.\n*Command requested by KY6G*")

@client.command(trigger="break")
async def bork(command: str, message: discord.Message):
	parts = command.split(" ")
	try:
		parts[1]
	except IndexError:
		await message.channel.send(f"There was an internal error processing your command. More information is shown below:\n\nOOPSIE WOOPSIE!! Uwu We made a fucky wucky!! A wittle fucko boingo! The code monkeys at our headquarters are working VEWY HAWD to fix this!")
	else:
		await message.channel.send(f"There was an internal error processing your command, caused by {parts[1]}. More information is shown below:\n\nOOPSIE WOOPSIE!! Uwu We made a fucky wucky!! A wittle fucko boingo! The code monkeys at our headquarters are working VEWY HAWD to fix this!")
