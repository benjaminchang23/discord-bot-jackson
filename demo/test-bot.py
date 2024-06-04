from calendar import Calendar
import datetime
from math import ceil
import os
from dotenv import load_dotenv

import pytz

import discord
from discord import Intents, utils
from discord.ext import commands, tasks

_street_sweep_days = [1, 2] # 1 corresponds to Tuesday, 2 corresponds to Wednesday
_street_sweep_week = 3
_winter_datetime_months = [1, 2, 3, 12]

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

bot_channel = None

task_times = [
    datetime.time(22, 0, 0, tzinfo=pytz.utc),
]


def week_calc_calendar(datetime_today: datetime.date):
    # for a week starting on sunday like a calendar
    cal = Calendar(6)
    weeks = cal.monthdayscalendar(datetime_today.year, datetime_today.month)
    for x in range(len(weeks)):
        if datetime_today.day in weeks[x]:
            return x + 1
    raise ValueError(f"Could not calculate week from {datetime_today}")


def week_calc_math(datetime_today: datetime.date):
    first_day = datetime_today.replace(day=1)
    dom = datetime_today.day
    adjusted_dom = dom + (1 + first_day.weekday()) % 7

    return int(ceil(adjusted_dom/7.0))


def week_calc(datetime_today: datetime.date):
    week_of_month_cal = week_calc_calendar(datetime_today)
    week_of_month_math = week_calc_math(datetime_today)
    assert week_of_month_cal == week_of_month_math, f"{datetime_today} cal: {week_of_month_cal} math: {week_of_month_math}"
    return week_of_month_cal


def this_month_street_sweep_tuesday(datetime_today: datetime.date):
    week_of_month = week_calc(datetime_today)
    if week_of_month < _street_sweep_week:
        street_sweep_datetime = datetime.datetime(datetime_today.year, datetime_today.month, 1)
    elif week_of_month == _street_sweep_week:
        street_sweep_datetime = datetime.datetime(datetime_today.year, datetime_today.month, 1)
    else:
        # we can ignore 12 + 1 months and just check to exclude 12 
        street_sweep_datetime = datetime.datetime(datetime_today.year, datetime_today.month + 1, 1)
        if street_sweep_datetime in _winter_datetime_months:
            raise RuntimeError("handle this case better")


def street_sweep_check():
    datetime_today = datetime.date.today()
    if datetime_today.month in _winter_datetime_months:
        return f"Today is in one of the winter months, which do not have street sweeping"
    datetime_street = this_month_street_sweep_tuesday(datetime_today)
    return f"Today is {datetime_today}, expected street sweeping this month on the near side is at {datetime_street}, far side at {datetime_street + datetime.timedelta(days=1)} sometime in the morning"


# assume 0 as start of week
def next_monday(datetime_today: datetime.date):
    days_ahead = 0 - datetime_today.weekday()
    if days_ahead <= 0: # Target day already happened this week
        days_ahead += 7
    return datetime_today + datetime.timedelta(days_ahead)


def whole_weeks_since(datetime_20210301: datetime.date):
    datetime_today = datetime.date.today()
    datetime_since = datetime_today - datetime_20210301
    return datetime_since.days // 7


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
    datetime_today = datetime.date.today()
    if datetime_today.weekday() in _street_sweep_days: # 1 corresponds to Tuesday, 2 corresponds to Wednesday
        if datetime_today.month not in _winter_datetime_months: # no street sweeping in the winter
            week_of_month = week_calc(datetime_today)
            if week_of_month == _street_sweep_week:
                # 148906826790993920
                # 694758082479128637
                user_ids = ["148906826790993920", "694758082479128637"]
                mentions = ""
                for user_id in user_ids:
                    mentions += "<@" + user_id + "> "
                await bot_channel.send(mentions + 'Street cleanup is tomorrow!')
    elif datetime_today.weekday() == 6: # 6 is Sunday
        response = trash_check()
        print(response)
        await bot_channel.send(response)


@client.event
async def on_member_join(member):
    await member.create_dm()
    await member.dm_channel.send(
        f'Hi {member.name}, welcome to The Jackson Street Experience!'
    )


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
        elif content.startswith("street"):
            response = street_sweep_check()
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
    now = str(datetime.datetime.now(pytz.utc))
    print(f"daily_task time: {now}")
    print(f'task_times: {task_times}')

    if not daily_task.is_running():
        daily_task.start()


def run_bot():
    client.run(TOKEN)


def main():
    run_bot()


if __name__ == "__main__":
    main()
