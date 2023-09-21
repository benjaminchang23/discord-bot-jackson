import datetime
import os
from dotenv import load_dotenv

import pytz

import discord
from discord import Intents, utils
from discord.ext import commands, tasks


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

bot_channel = None

task_times = [
    datetime.time(22, 26, 0, tzinfo=pytz.utc),
    datetime.time(22, 27, 0, tzinfo=pytz.utc),
    datetime.time(22, 28, 0, tzinfo=pytz.utc),
    datetime.time(22, 29, 0, tzinfo=pytz.utc),
    datetime.time(22, 30, 0, tzinfo=pytz.utc),
    datetime.time(22, 31, 0, tzinfo=pytz.utc),
    datetime.time(22, 32, 0, tzinfo=pytz.utc),
    datetime.time(22, 33, 0, tzinfo=pytz.utc),
    datetime.time(22, 34, 0, tzinfo=pytz.utc),
    datetime.time(22, 35, 0, tzinfo=pytz.utc),
]

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

@client.event
async def on_member_join(member):
    await member.create_dm()
    await member.dm_channel.send(
        f'Hi {member.name}, welcome to The Jackson Street Experience!'
    )

def trash_check():
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
    return response

@tasks.loop(time=task_times)
async def daily_task():
    global bot_channel
    today = datetime.date.today()
    print(f"daily_task time: {today}")
    if today.weekday() in [2, 3]: # 2 corresponds to Wednesday, 3 corresponds to Thursday
        week_of_month = (today.day - 1) // 7 + 1
        if week_of_month == 3:
            await bot_channel.send('Street cleanup is today!')
    elif today.weekday() == 6: # 6 is Sunday
        response = trash_check()
        print(response)
        await bot_channel.send(response)

@client.event
async def on_message(message):
    global bot_channel
    if message.author == client.user:
        return
    if message.content.startswith("!"):
        content = message.content[1:]
        if content.startswith("trash"):
            response = trash_check()
            print(response)
            await bot_channel.send(response)
        # print("I see a message!")
        # await bot_channel.send("I see a message!")

@client.event
async def on_ready():
    global bot_channel
    for guild in client.guilds:
        if guild.name == GUILD:
            break

    bot_channel = utils.get(guild.channels, name='general')

    print(
        f'{client.user} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})\n'
        f'{client.user} will announce chores on channel with id: {bot_channel.id}\n'
    )

    members = '\n - '.join([member.name for member in guild.members])
    print(f'Guild Members:\n - {members}')
    today = datetime.date.today()
    print(f"daily_task time: {today}")
    print(f'task_times: {task_times}')

def run_bot():
    client.run(TOKEN)

def main():
    run_bot()

if __name__ == "__main__":
    main()
