import log
from client import client
from key import wa_key

import aiohttp
import discord
import time
import wolframalpha

http_client = aiohttp.ClientSession()
last_run_time = 0
blacklist_users = [
	252597184761954304,
]

# todo: File system caching
# todo: more data in embeds (show everything)?
# todo: help
@client.command("wa", aliases=["wolframalpha", "w|a", "wolfram|alpha"])
async def WolframAlphaQuery(command: str, message: discord.Message):
	global last_run_time
	if message.author.id in blacklist_users:
		await message.channel.send(f"{message.author.mention} Command denied: blacklisted")
		return
	if (time.time()-last_run_time) < 15:
		await message.channel.send(f"{message.author.mention} Rate limited: please wait "
								   f"{15-(time.time()-last_run_time):.1f} seconds")
		return
	if len(command.split(" ")) == 1:
		await message.channel.send("Argument error: Query not provided")
		return

	last_run_time = time.time()
	query = command.split(" ", 1)[1]
	await message.channel.trigger_typing()

	request_params = {
		"appid": wa_key,
		"output": "json",
		"reinterpret": "true",
		"ip": "127.0.0.1",
		"units": "metric",
		"input": query
	}
	async with http_client.get("http://api.wolframalpha.com/v2/query", params=request_params) as _results:
		results = await _results.json(content_type="text/plain")
	results = results['queryresult']

	if results.get("success") and not results.get("error"):
		embed = discord.Embed(colour=0x08ab12, description="Wolfram|Alpha query")
		embed = embed.set_author(name=message.author.display_name, icon_url=message.author.avatar_url)

		try:
			raw_assumptions = results.get("assumptions", None)
			assumptions = []
			if raw_assumptions is not None:
				if isinstance(raw_assumptions, dict):
					raw_assumptions = [raw_assumptions]
				for item in raw_assumptions:
					assumptions.append(f"Assuming {item['values'][0]['desc']} for '{item['word']}'")
				embed = embed.add_field(inline=False, name="Assumptions", value="\n".join(assumptions))
		except Exception as e:
			log.warning(f"Could not find assumptions for query: {query}", include_exception=True)

		try:
			input_pod = discord.utils.find(lambda x: x['id'] == "Input", results['pods'])
			input_interpretation = input_pod['subpods'][0]['plaintext']
			embed = embed.add_field(inline=False, name=input_pod['title'], value=input_interpretation)
		except:
			log.warning(f"Could not find user interpretation from query: {query}", include_exception=True)

		try:
			result_pod = discord.utils.find(lambda x: (x['id'] == 'Result') or
													(x.get("primary", False)),
											results['pods'])
			if result_pod is None:
				result_pod = results['pods'][1]
			answer = result_pod['subpods'][0]['plaintext']
			embed = embed.add_field(inline=False, name=result_pod['title'], value=answer)
		except Exception as e:
			log.warning(f"Cound not find answer from query: {query}", include_exception=True)

		try:
			conversion_pod = discord.utils.find(lambda x: x['id'] == "UnitConversion", results['pods'])
			if conversion_pod is not None:
				conversions = [x['plaintext'] for x in conversion_pod['subpods']]
				embed = embed.add_field(inline=False, name="Unit conversions", value="\n".join(conversions))
		except Exception as e:
			log.warning(f"Could not find conversions from query: {query}")

		if "Invention" in results['datatypes'].split(","):
			summary_pod = discord.utils.find(lambda x: "WikipediaSummary" in x['id'], results['pods'])
			embed = embed.add_field(inline=False,
									name=summary_pod['title'],
									value=summary_pod['subpods'][0]['plaintext'])
			embed = embed.add_field(inline=False,
									name="Full Wikipedia page",
									value=summary_pod['subpods'][0]['infos']['links']['url'])

		embed = embed.set_footer(text="For feature or more info requests, please message ntoskrnl")
		await message.channel.send(embed=embed)

	if not (results['success'] or results['error']):
		embed = discord.Embed(colour=0xa80703, description="Your query was not understood")
		embed = embed.set_author(name=message.author.display_name, icon_url=message.author.avatar_url)
		embed = embed.add_field(name="Some tips for asking W|A", value="Try different phrasings of your query\n"
																	"Enter whole words, not abbreviations or TLAs\n"
																	"Check spelling and use English")
		await message.channel.send(embed=embed)
		return

	if results['error']:
		await message.channel.send("There was an error in Wolfram|Alpha while running your query.")
		return
