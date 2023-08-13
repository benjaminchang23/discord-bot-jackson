# Bot.py
import asyncio
import datetime
import os

from dotenv import load_dotenv

from discord import Intents
from discord import utils
from discord.ext import commands, tasks

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

bot = commands.Bot(command_prefix='!', intents=Intents.default())

bot_channel = None

@bot.event
async def on_ready():
    global bot_channel
    for guild in bot.guilds:
        if guild.name == GUILD:
            break

    bot_channel = utils.get(guild.channels, name='bot-spam')

    print(
        f'{bot.user} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})\n'
        f'{bot.user} will announce street cleaning on channel with id: {bot_channel.id}\n'
    )
    
@bot.event
async def on_member_join(member):
    await member.create_dm()
    await member.dm_channel.send(
        f'Hi {member.name}, welcome to The Jackson Street Experience!'
    )

@tasks.loop(hours=24)
async def every_day():
    message_channel = bot.get_channel(bot_channel) # replace with your channel id
    today = datetime.date.today()
    if today.weekday() in [2, 3]: # 2 corresponds to Wednesday, 3 corresponds to Thursday
        week_of_month = (today.day - 1) // 7 + 1
        if week_of_month == 3:
            await message_channel.send('Street cleanup is today!')

@every_day.before_loop
async def before():
    for _ in range(60 * 60 * 24): # loop the checking every seconds in one day
        now = datetime.datetime.now()
        if now.hour == 9:
            break
        await asyncio.sleep(60) # wait 60 seconds before looping again. This is necessary to mitigate high resource usage.

def run_bot():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(every_day.start())
    

def main():
    run_bot()

if __name__ == "__main__":
    main()