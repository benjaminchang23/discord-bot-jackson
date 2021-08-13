# Bot.py
import datetime
import os
import random
import schedule
import threading
import time

from dotenv import load_dotenv

from discord.ext import commands

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

bot = commands.Bot(command_prefix='!')

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
    for guild in bot.guilds:
        if guild.name == GUILD:
            break

    print(
        f'{bot.user} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})\n'
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

# @bot.command(name='chores', help='Responds with the expected chore schedule')
# async def chore_check(ctx):


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

def chore_notify():
    print("Time to do the following chores:")

def init_schedule():
    schedule.every().day.at("18:00").do(chore_notify)

def run_bot():
    bot.run(TOKEN)

def run_schedule():
    schedule.run_pending()
    time.sleep(1)

def main():
    schedule_thread = threading.Thread(target=run_schedule, args=(1,), daemon=True)
    run_bot()

if __name__ == "__main__":
    main()