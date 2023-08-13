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

# assume 0 as start of week
def next_monday(d):
    days_ahead = 0 - d.weekday()
    if days_ahead <= 0: # Target day already happened this week
        days_ahead += 7
    return d + datetime.timedelta(days_ahead)

def whole_weeks_since(d):
    datetime_today = datetime.date.today()
    datetime_since = datetime_today - d
    return datetime_since.days // 7

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

    datetime_20210301 = datetime.date(2021, 3, 1)
    datetime_today = datetime.date.today()
    datetime_trash = next_monday(datetime_today)

    print(f"Today is {datetime_today} next expected trash time is {datetime_trash} sometime in the morning.\n")

    mondays = whole_weeks_since(datetime_20210301)
    print(f"{mondays} Mondays since {datetime_20210301}")

    if mondays % 2 == 0:
        print(f"no recycling")
    

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

@bot.command(name='trash', help='Responds with an expected trash and recycling time')
async def trash_check(ctx):
    datetime_20210301 = datetime.date(2021, 3, 1)
    datetime_today = datetime.date.today()
    datetime_trash = next_monday(datetime_today)
    mondays = whole_weeks_since(datetime_20210301)

    # TODO add email sync as on_event listener this will cover holidays and other unexpected changes
    response = f"Today is {datetime_today} next expected trash time is {datetime_trash} sometime in the morning.\n"
    if mondays % 2 == 0:
        response += "No recycling til next cycle\n"
    else:
        response += "Recycling should be put down on the curb\n"
    await ctx.channel.send(response)

@bot.event
async def on_error(event, *args, **kwargs):
    with open('err.log', 'a') as f:
        if event == 'trash_check':
            print(f'Error: trash_check exception from: {args[0]}\n')
            f.write(f'Unhandled message: {args[0]}\n')
        else:
            raise

def run_bot():
    every_day.start()
    bot.run(TOKEN)

def main():
    run_bot()

if __name__ == "__main__":
    main()