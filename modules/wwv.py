from client import client

import datetime
import discord

text = "National Institute of Standards and Technology Time, This is Radio Station WWV, Fort Collins, Colorado, " \
		"broadcasting on internationally allocated standard carrier frequencies of 2.5, 5, 10, 15, and 20 Megahertz, " \
		"providing time of day, standard time intervals, and other related information. Inquiries regarding these " \
		"transmissions may be directed to the National Institute of Standards and Technology, Radio Station WWV, 2000 " \
		"East County Road 58, Fort Collins, Colorado, 80524.\n"

text_h = "National Institute of Standards and Technology Time, This is radio station WWVH, Kauai, Hawaii, broadcasting"\
		" on internationally allocated standard carrier frequencies of 2.5, 5, 10 and 15 Megahertz, providing time of" \
		" day, standard time intervals, and other related information. Inquiries regarding these transmissions may be " \
		"directed to the National Institute of Standards and Technology, Radio Station WWVH, Post Office Box 417, " \
		"Kekaha, Hawaii 96752. Aloha.\n"

new_minute = "At the tone, HHHH hours, MMMM minutes, coordinated universal time. DOTS BEEEEP"

time_lookup = {
	0: "zero",
	1: "one",
	2: "two",
	3: "three",
	4: "four",
	5: "five",
	6: "six",
	7: "seven",
	8: "eight",
	9: "nine",
	10: "ten",
	11: "eleven",
	12: "twelve",
	13: "thirteen",
	14: "fourteen",
	15: "fifteen",
	16: "sixteen",
	17: "seventeen",
	18: "eighteen",
	19: "nineteen",
	20: "twenty",
	21: "twenty-one",
	22: "twenty-two",
	23: "twenty-three",
	24: "twenty-four",
	25: "twenty-five",
	26: "twenty-six",
	27: "twenty-seven",
	28: "twenty-eight",
	29: "twenty-nine",
	30: "thirty",
	31: "thirty-one",
	32: "thirty-two",
	33: "thirty-three",
	34: "thirty-four",
	35: "thirty-five",
	36: "thirty-six",
	37: "thirty-seven",
	38: "thirty-eight",
	39: "thirty-nine",
	40: "fourty",
	41: "fourty-one",
	42: "fourty-two",
	43: "fourty-three",
	44: "fourty-four",
	45: "fourty-five",
	46: "fourty-six",
	47: "fourty-seven",
	48: "fourty-eight",
	49: "fourty-nine",
	50: "fifty",
	51: "fifty-one",
	52: "fifty-two",
	53: "fifty-three",
	54: "fifty-four",
	55: "fifty-five",
	56: "fifty-six",
	57: "fifty-seven",
	58: "fifty-eight",
	59: "fifty-nine",
}


@client.command(trigger="wwv", aliases=["time"])
async def At_the_tone__six_hours_and_twenty_one_minutes__coordinated_universal_time___BEEEEP(command: str, message: discord.Message):
	time = datetime.datetime.utcnow() + datetime.timedelta(minutes=1)
	d_sec = 60-time.second
	if (("--id" in command) or
			(time.minute == 29) or
			(time.minute == 30) or
			(time.minute == 59) or
			(time.minute == 00)):

		say = f"```\n{text}\n{new_minute}\n```"
	else:
		say = f"```{new_minute}```"

	say = say.replace("HHHH", time_lookup[time.hour])
	say = say.replace("MMMM", time_lookup[time.minute])
	say = say.replace("DOTS", "."*d_sec)
	if time.hour == 1:
		say = say.replace("hours", "hour")
	if time.minute == 1:
		say = say.replace("minutes", "minute")

	await message.channel.send(say)


@client.command(trigger="wwvh")
async def WWVH_transmissions(command: str, message: discord.Message):
	time = datetime.datetime.utcnow() + datetime.timedelta(minutes=1)
	d_sec = 60-time.second
	if (("--id" in command) or
			(time.minute == 29) or
			(time.minute == 30) or
			(time.minute == 59) or
			(time.minute == 00)):

		say = f"```\n{text_h}\n{new_minute}\n```"
	else:
		say = f"```{new_minute}```"

	say = say.replace("HHHH", time_lookup[time.hour])
	say = say.replace("MMMM", time_lookup[time.minute])
	say = say.replace("DOTS", "."*d_sec)
	if time.hour == 1:
		say = say.replace("hours", "hour")
	if time.minute == 1:
		say = say.replace("minutes", "minute")

	await message.channel.send(say)
