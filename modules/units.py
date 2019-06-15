from client import client

import asyncio
import discord
import subprocess

client.basic_help(title="unit", desc="Converts units with the `units` Unix command.")
help_dict = {
	"Usage": f"`{client.default_prefix}unit <src units> [dst units]`",
	"Arguments": "`src units` - Source units to convert from. Supports any units the Unix `units` command supports (a *lot*!).\n`dst units` - (optional) Destination units to convert to.",
	"Description": "This units transforms one unit into another unit. The command uses the underlying `units` Unix command, and supports over 3000 different units.\nIf destination units are not provided, the source units will be converted into standard SI units.",
	"One argument usage": "`units 0.04128mi`\n`units 12d`\nWhen passing only one argument, the bot will convert the given measurement into standard SI units.",
	"Two argument usage": "`units 41.28mi km`\n`units 12um 0.02mm`\nWhen passing two arguments, the format is `units <src> <dst>`. This will convert the given measurement into the destination unit, if possible. If two numerical measurements are provided, this performs a ratio comparison instead (see below). Note that providing one measurement but with a space is interpreted as attempting to convert a dimensionless number into a measurement, and will throw a conformability error.",
	"Three argument usage": "`units 1.3 lightseconds m`\nWhen passing three arguments, the first two are interpreted as the source measurement, which will be converted into the destination measurement given by the third argument.",
	"Four argument usage": "`units 0.128 us 0.000000319 sec`\nWhen passing four arguments, the first two and the last two are interpreted to be the source and destination measurements. With numerical values provided for both, this will perform a ratio comparison (see below).",
	"Using temperature": "If it is desired to use temperatures, the temperature functions must be used: `tempC(1700)`, `tempK(273.15)`, `tempF`, or `tempR`.",
	"SI conversion": "If a single unit is passed without a destination unit or measurement to convert or compare to, then the provided measurement will be converted into standard SI/physics unit dimensions of length (meters), mass (kilograms), and time (seconds).",
	"Comparing measurements": "It is possible to pass in two whole measurements in order to compare the two, assuming they are of the same dimensions (ie. they are both mass, or velocity, or whatever). The resulting scalar value is the ratio of how greater the first value is to the second (eg. `units 5km 2.5km` returns 2.0, because 5km is twice as large as 2.5km). Using units that cannot be compared results in a conformability error.",
	"Conformability errors": "When it is impossible to convert or compare the measurements given (eg. minutes into kilometers), a *conformability error* will result. The two resulting values given are the base SI units for both given measurements, as if you had performed the one argument usage using it.",
	"Performing math": "The units command can perform rather complex math, by entering an expression to calculate in the form of one argument usage. Trig functions are done in radians (as they rightfully should), and proper evaulation order is followed.\nExample: `units 12+3/(2sin(pi/2))",
}
client.long_help(cmd="units", mapping=help_dict)


@client.command(trigger="units", aliases=["unit", "convert", "u"])
async def convert_units(command: str, message: discord.Message):
	parts = command.split(" ")

	if len(parts) == 1:
		# no args
		await message.channel.send(f"Need more arguments to run command. See command help for help.")
		return
	if len(parts) == 2:
		proc = subprocess.Popen(["units", "-t", parts[1]], stdout=subprocess.PIPE)
	if len(parts) == 3:
		proc = subprocess.Popen(["units", "-t", parts[1], parts[2]], stdout=subprocess.PIPE)
	if len(parts) == 4:
		proc = subprocess.Popen(["units", "-t", parts[1]+parts[2], parts[3]], stdout=subprocess.PIPE)
	if len(parts) == 5:
		proc = subprocess.Popen(["units", "-t", parts[1]+parts[2], parts[3]+parts[4]], stdout=subprocess.PIPE)


	await asyncio.sleep(1)
	stdout, stderr = proc.communicate(timeout=0.01)
	await message.channel.send(stdout.decode())
	return
