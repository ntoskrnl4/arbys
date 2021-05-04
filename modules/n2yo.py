from client import client
from modules import __common__
from typing import List

import aiohttp
import datetime
import discord
import key


client.basic_help(title="n2yo", desc="Shows information about satellites currently in space. Run with no arguments "
                                     "for an explanation of functionality and some selected satellites.")

cmd_help = {
    "Usage": "`n2yo <action> [args] [--debug] [--apicount]`",
    "Arguments": "`action` - what you want to do\n`--debug` - shows extra information about the command while running\n`--apicount` - shows api usage in past hour",
    "Further help": "For detailed help about the functionality of this command, run `n2yo` without any arguments."
}
client.long_help(cmd="n2yo", mapping=cmd_help)

cmd_desc = "This command uses the N2YO.com API to show information about various satellites that are in the sky at " \
           "your location. \nSatellites are referred to by their NORAD catalogue number. To get a list of satellite " \
           "numbers run the command with the singular argument \"sats\". If you know the NORAD ID of another " \
           "satellite you can use its ID as well.\n"
get_sat_pos = "Usage: `n2yo pos <sat_id> <grid> ['--alt' your_altitude] `\n\nGets the current position of a satellite in your " \
              "sky given the satellite ID and your Maidenhead grid square. An altitude of 100m is used by default, " \
              "altitude in meters can be provided as an optional third argument and can help increase accuracy."
get_passes = "Usage: `n2yo passes <sat_id> <grid> <min_elevation> ['--alt' your_altitude]`\n\n`min_elevation` - " \
             "minimum maximum elevation of the pass\n`--alt [x]` - specifies your altitude in meters for better " \
             "accuracy (recommended)"
sat_norad_ids = """```
25544: Space Station
40967: Fox-1A / AO-85
43017: Fox-1B / AO-91
43774: Fox-1C / AO-95
43137: Fox-1D / AO-92
```
"""

api_key = f"&apiKey={key.n2yo_key}"
base = "https://www.n2yo.com/rest/v1/satellite"
last_pass_req = []

# cooldown timers:
# max 600 req/1 hour
# max 100 req/5 min

req_history: List[datetime.datetime] = []

fast_cooldown_max = 100  # This many requests in fast_cooldown_window amount of time will trigger the cooldown
fast_cooldown_window = datetime.timedelta(minutes=5)

slow_cooldown_max = 600  # N2YO.com specifies 1000/hr max but we'll say 600 to be safe
slow_cooldown_window = datetime.timedelta(hours=1)

sat_id_embed = discord.Embed(title="Common satellite NORAD IDs",
                             description="This command requires satellites to be identified by their NORAD ID. Any ID "
                                         f"can be used but here are some common ones.\n{sat_norad_ids}")


def check_cooldowns():
    """Return true if cooldowns check out."""
    global req_history
    now = datetime.datetime.utcnow()
    if not len([x for x in req_history if now-x < datetime.timedelta(seconds=3)]) < 5:  # instantaneous cooldown
        return False
    if not len([x for x in req_history if now-x < fast_cooldown_window]) < fast_cooldown_max:
        return False
    if not len([x for x in req_history if now-x < slow_cooldown_window]) < slow_cooldown_max:
        return False
    req_history.append(now)
    return True


def deg2hms(degrees):
    hours = int((degrees/360)*24)
    hours_part = ((degrees/360)*24) - hours
    minutes = int(hours_part*60)
    minutes_part = (hours_part*60) - minutes
    seconds = minutes_part*60
    return hours, minutes, seconds


def get_lat_long(square: str):
    lon = ((ord(square[0].upper()) - ord('A')) * 20) - 180
    lat = ((ord(square[1].upper()) - ord('A')) * 10) - 90
    
    lon += ((ord(square[2]) - ord('0')) * 2)
    lat += ((ord(square[3]) - ord('0')) * 1)
    
    lon += ((ord(square[4].upper())) - ord('A')) * (5 / 60)
    lat += ((ord(square[5].upper())) - ord('A')) * (2.5 / 60)
    
    lon += (2.5 / 60)
    lat += (1.25 / 60)
    
    return lat, lon


def parse_pass_info(item, iter):
    start_azimuth = item["startAz"]
    start_time = datetime.datetime.utcfromtimestamp(item["startUTC"])
    peak_azimuth = item["maxAz"]
    peak_elevation = item["maxEl"]
    peak_time = datetime.datetime.utcfromtimestamp(item["maxUTC"])
    end_azimuth = item["endAz"]
    end_time = datetime.datetime.utcfromtimestamp(item["endUTC"])
    runtime = (end_time-start_time).seconds
    return f"`{iter}: {start_time.__str__()} UTC lasting {runtime//60}m{runtime%60}s @ peak el. {int(peak_elevation)}°`"


def passinfo(count: int, passes: list):
    out = ""
    i = 0
    for _pass in passes:
        if i == count: break
        out += parse_pass_info(_pass, i)+"\n"
        i += 1
    if len(out) > 2000:
        return passinfo(count-1, passes)
    else:
        return out


@client.command(trigger="n2yo", aliases=["sat"])
async def process_command(command: str, message: discord.Message):
    global last_pass_req
    
    parts = command.split(" ")
    
    try:
        parts, args = __common__.parse_arguments(parts, {
            "debug": False,
            "apicount": False,
            "alt": 100.0,
            "dx": False,
            "days": 3,
        })
    except RuntimeError as e:
        pass
        return
    
    if args["debug"]: await message.channel.send(f"debug: running command with arguments `{parts}`")
    
    if len(parts) is 1:
        # no arguments, print help
        embed = discord.Embed(title="Command usage", description=cmd_desc, colour=0x42bf92)
        embed = embed.add_field(name="Get current satellite position", value=get_sat_pos)
        embed = embed.add_field(name="Get upcoming passes", value=get_passes)
        embed = embed.set_footer(text=__common__.get_timestamp())
        await message.channel.send(embed=embed)
        return
    
    if parts[1] == "sats":
        if args["debug"]: await message.channel.send("debug: returning satellite info embed")
        await message.channel.send(embed=sat_id_embed)
        return
    
    if parts[1] in ["passinfo"]:
        if not last_pass_req:
            await message.channel.send("State error: `passes` command has not been run; no passes available to get details on")
            return
        try:
            num = int(parts[2])
        except ValueError:
            await message.channel.send(f"Argument error: Invalid integer provided (got: {parts[2]})")
            return
        except IndexError:
            # no second number
            await message.channel.send("Argument error: No pass specified")
            return
        
        try:
            target_pass = last_pass_req["passes"][num]
        except IndexError:
            await message.channel.send("State error: Index out of bounds")
            return
        
        embed = discord.Embed(title="Satellite pass details", description=f"Information about satellite pass of {last_pass_req['info']['satname']} (id {last_pass_req['info']['satid']})")
        embed = embed.add_field(name="Pass Start",
                                value=f"`Timestamp: {datetime.datetime.utcfromtimestamp(target_pass['startUTC']).__str__()} UTC`\n"
                                      f"`Azimuth: {target_pass['startAz']} degrees`\n",
                                inline=False)
        embed = embed.add_field(name="Pass Climax",
                                value=f"`Timestamp: {datetime.datetime.utcfromtimestamp(target_pass['maxUTC']).__str__()} UTC`\n"
                                      f"`Azimuth: {target_pass['maxAz']} degrees`\n"
                                      f"`Elevation: {target_pass['maxEl']} degrees`\n",
                                inline=False)
        embed = embed.add_field(name="Pass End",
                                value=f"`Timestamp: {datetime.datetime.utcfromtimestamp(target_pass['endUTC']).__str__()} UTC`\n"
                                      f"`Azimuth: {target_pass['endAz']} degrees`\n",
                                inline=False)
        await message.channel.send(embed=embed)
        return
    
    if not check_cooldowns():
        await message.channel.send("Sorry, but the API limit has been reached. Please try again later, or go to the n2yo.com website.")
        return
    
    if parts[1] in ["get_pos", "pos", "position"]:
        if len(parts) < 4:
            await message.channel.send("Argument error: Not enough arguments provided for specified operation. Run `n2yo` without arguments for command help.")
            return
        
        # get our targeted satellite
        target_sat = parts[2]
        try: target_sat = int(target_sat)  # Literally only doing this so the folded code will look neat in PyCharm (it doesn't fold single lines >:( )
        except ValueError:
            await message.channel.send(f"Argument error: Target satellite could not be converted to integer. Run `n2yo` without arguments for command help. (got: {target_sat})")
            return
        
        # get our targeted grid
        target_grid = parts[3]
        if len(target_grid) is not 6:
            await message.channel.send(f"Argument error: Provided grid not 6 characters long. Please use your 6 digit Maidenhead grid locator only. Run `n2yo` without arguments for command help. (got: {target_grid})")
            return
        if not (target_grid[:2].isalpha() and target_grid[2:4].isdigit() and target_grid[4:6].isalpha()):
            await message.channel.send(f"Argument error: Provided grid not formatted correctly. Format must be 6 digit Maidenhead grid locator. (got: {target_grid})")
            return
        target_lat, target_long = get_lat_long(target_grid)
        if args["debug"]: await message.channel.send(f"debug: target coordinates {target_lat} {target_long}")
        
        async with message.channel.typing():
            async with aiohttp.ClientSession() as connection:
                
                target_url = f"{base}/positions/{target_sat}/{target_lat}/{target_long}/{args['alt']}/{2 if args['dx'] else 1}/"
                if args["debug"]: await message.channel.send(f"debug: calling api url `{target_url}`")
                async with connection.get(target_url+api_key) as response:
                    info = await response.json()
            
            satname = info['info']['satname']
            satid = info['info']['satid']
            ts = datetime.datetime.utcfromtimestamp(info['positions'][0]['timestamp'])
            gr_lat = info['positions'][0]['satlatitude']
            gr_lon = info['positions'][0]['satlongitude']
            sat_alt = info['positions'][0]['sataltitude']
            azimuth = info['positions'][0]['azimuth']
            elevation = info['positions'][0]['elevation']
            ra = info['positions'][0]['ra']
            dec = info['positions'][0]['dec']
            ra_h, ra_m, ra_s = deg2hms(ra)
            
            gr_loc = f"`Latitude: {str(gr_lat)[:8]}°`\n`Longitude: {str(gr_lon)[:7]}°`\n`Altitude: {sat_alt:.2f} km`"
            sky_loc = f"`Azimuth: {azimuth}°`\n`Elevation: {elevation}°`"
            cel_loc = f"`RA: {ra_h}h {ra_m}m {ra_s:.3f}s`\n`Dec: {dec:.2f} degrees`"
            
            if args["dx"]:
                d_gr_lat = info['positions'][1]['satlatitude'] - gr_lat
                d_gr_lon = info['positions'][1]['satlongitude'] - gr_lon
                d_sat_alt = info['positions'][1]['sataltitude'] - sat_alt
                d_azimuth = info['positions'][1]['azimuth'] - azimuth
                d_elevation = info['positions'][1]['elevation'] - elevation
                d_ra = info['positions'][1]['ra'] - ra
                d_dec = info['positions'][1]['dec'] - dec
                d_ra_h, d_ra_m, d_ra_s = deg2hms(d_ra)
                
                d_gr_loc = f"`Latitude: {d_gr_lat:.2f}°/sec`\n`Longitude: {d_gr_lon:.2f}°/sec`\n`Altitude: {d_sat_alt:.2f} km/s`"
                d_sky_loc = f"`Azimuth: {d_azimuth:.2f}°/sec`\n`Elevation: {d_elevation:.2f}°/sec`"
                d_cel_loc = f"`RA: {d_ra_s+(d_ra_m*60)+(d_ra_h*3600):.2f}s /second`\n`Dec: {d_dec:.4f} degrees/sec`"
            
            embed = discord.Embed(title=f"Current satellite position for \"{satname}\" (ID {satid})",
                                  description=f"This information calculated for {ts.__str__()} UTC")
            embed = embed.add_field(name="Ground Location", value=gr_loc)
            embed = embed.add_field(name="Sky Location", value=sky_loc)
            embed = embed.add_field(name="Celestial Sphere Location", value=cel_loc)
            
            if args["dx"]:
                embed = embed.add_field(name="Ground Movement", value=d_gr_loc)
                embed = embed.add_field(name="Sky Movement", value=d_sky_loc)
                embed = embed.add_field(name="Celestial Sphere Movement", value=d_cel_loc)
            
            if '--apicount' in parts:
                embed = embed.set_footer(text=f"Information provided thanks to the N2YO.com API - API Usage for past hour: {info['info']['transactionscount']}")
            else:
                embed = embed.set_footer(text=f"Information provided thanks to the N2YO.com API")
        
        await message.channel.send(embed=embed)
        return
    
    if parts[1] in ["passes"]:
        # params: n2yo passes satid grid min_elevation --alt val --days x --apicount --debug
        if len(parts) < 4:
            await message.channel.send("Argument error: Not enough arguments provided for specified operation. Run `n2yo` without arguments for command help.")
            return
        
        target_sat = parts[2]
        try:
            target_sat = int(target_sat)
        except ValueError:
            await message.channel.send(f"Argument error: Target satellite could not be converted to integer. Run `n2yo` without arguments for command help. (got: {target_sat})")
            return
        
        target_grid = parts[3]
        if len(target_grid) is not 6:
            await message.channel.send(f"Argument error: Provided grid not 6 characters long. Please use your 6 digit Maidenhead grid locator only. Run `n2yo` without arguments for command help. (got: {target_grid})")
            return
        if not target_grid[:2].isalpha() or not target_grid[2:4].isdigit() or not target_grid[4:6].isalpha():
            await message.channel.send(f"Argument error: Provided grid not formatted correctly. Format must be 6 digit Maidenhead grid locator. (got: {target_grid})")
            return
        target_lat, target_long = get_lat_long(target_grid)
        
        if args["debug"]: await message.channel.send(f"debug: successfully got target coordinates {target_lat} {target_long}")
        
        target_elevation = parts[4]
        try:
            target_elevation = int(target_elevation)
        except ValueError:
            await message.channel.send(f"Argument error: Target elevation could not be converted to integer. Run `n2yo` without arguments for command help. (got: {target_elevation})")
            return
            
        async with message.channel.typing():
            async with aiohttp.ClientSession() as connection:
                
                target_url = f"{base}/radiopasses/{target_sat}/{target_lat}/{target_long}/{args['alt']}/{args['days']}/{target_elevation}/"
                if args["debug"]: await message.channel.send(f"debug: calling api url `{target_url}`")
                async with connection.get(target_url+api_key) as response:
                    info = await response.json()
            
            satname = info["info"]["satname"]
            satid = info["info"]["satid"]
            passcount = info["info"]["passescount"]
            
            last_pass_req = info
            
            embed = discord.Embed(title=f"Upcoming passes of satellite {satname} (id {satid})",
                                  description=passinfo(40, info["passes"]))
            embed = embed.add_field(name="To see more details about a specific pass run the following command:",
                                    value="`n2yo passinfo <number>`")
            if args['apicount']:
                embed = embed.set_footer(text=f"Information provided thanks to the N2YO.com API - API Usage for past hour: {info['info']['transactionscount']}")
            else:
                embed = embed.set_footer(text=f"Information provided thanks to the N2YO.com API")
        
        await message.channel.send(embed=embed)
