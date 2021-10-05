# Bot.py
import asyncio
import datetime
import os
import random
import schedule
import threading
import time
from queue import Queue

from dotenv import load_dotenv

from discord.ext import commands
from discord import utils

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

bot = commands.Bot(command_prefix='!')

rooms = ['dining room', 'family room', 'kitchen', 'office']
accessways = ['deck', 'porch', 'stairs']

daily = ['wipe kitchen countertops', 'wipe dining table', 'sort mail', 'clean room', 'check trash and recycling bins', 'water plants']
weekly = ['clean toilet', 'clean shower', 'clean water fixtures (knobs, handles, faucets', 'check fridge contents', 'clean stovetop', 'clean accessway', 'weed garden']
monthly = []

# queues
daily_q = Queue()

chore_channel = None

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
    global chore_channel
    for guild in bot.guilds:
        if guild.name == GUILD:
            break

    chore_channel = utils.get(guild.channels, name='bot-spam')

    print(
        f'{bot.user} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})\n'
        f'{bot.user} will announce chores on channel with id: {chore_channel.id}\n'
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

@bot.command(name='schedule', help='Responds with current chore schedule')
async def schedule_check(ctx):
    response = schedule.get_jobs()
    await ctx.channel.send(response)

@bot.command(name='trash', help='Responds with an expected trash and recycling time')
async def trash_check(ctx):
    datetime_20210301 = datetime.date(2021, 3, 1)
    datetime_today = datetime.date.today()
    datetime_trash = next_monday(datetime_today)
    mondays = whole_weeks_since(datetime_20210301)

    # TODO add email sync as on_event listener
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

@bot.event
async def alert_chore(chore_list):
    global chore_channel
    chore_string = f'Daily chore alert: {chore_list}'
    print(chore_string)
    await chore_channel.send(chore_string)

def chore_publish_daily():
    print('Publish daily chores')
    chore_list = []
    daily_chores = 3

    if daily_q.empty():
        [daily_q.put(v) for v in random.sample(daily, len(daily))]

    while daily_chores > 0:
        daily_chores-=1
        chore_list.append(daily_q.get())

    if bot.is_ready():
        # print(f'Current_user: {bot.user}')
        bot.loop.create_task(alert_chore(chore_list))

def init_schedule():
    print(f'Init schedule at: {datetime.datetime.now()}')
    schedule.every().day.at("18:00").do(chore_publish_daily)

    schedule.every(30).seconds.do(chore_publish_daily)
    # schedule.every().sunday.at("18:00").do()
    # schedule.every().sunday.at("18:00").do(chore_publish_monthly)

def run_bot():
    bot.run(TOKEN)

def choose_programming():
    while True:
        schedule.run_pending()
        time.sleep(10)

def main():
    init_schedule()
    schedule_thread = threading.Thread(target=choose_programming, daemon=True)
    schedule_thread.start()
    run_bot()

if __name__ == "__main__":
    main()