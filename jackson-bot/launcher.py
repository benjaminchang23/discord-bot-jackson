"""
Community Bot Launcher
Parameters:
- key
- database file path (if empty, initializes a new one)
Exit Codes:
0 - Normal Shutdown
1 - Unexpected Error
2 - Invalid Token
20 - Restart
"""
import argparse
import discord
from discord.ext import commands
import sys

from core import Bot
from core import init_logger

def run_bot(args):
    bot = Bot(args.token, args.database, debug=args.debug)
    print("Loading loggers...")
    bot.logger = init_logger(bot, args.debug)
    bot.logger.debug("Loaded loggers.")

    if bot.config["token"] is None:
        bot.logger.error("Invalid or missing token!")
        bot.shutdown_mode = 2
        sys.exit(bot.shutdown_mode)
      
    bot.logger.debug("Loading extensions...")
    bot.load_extension("mysterybot.core.cog_manager")
    #bot.load_extnesion("mysterybot.core.timer")
    
    print('''
                                                          ______________
                                                         |##############
              __             __                          |##############
_____________|  |_____     _(   )                        |##############
UUUUUUUUUUUUU|__|UUUUU| ,-'      )_                      |##############
UUU_UUUUUU_UUUUUU_UUUU|(   (  /    )                     |   __   __   _
UU|_|UUUU|_|UUUU|_|UUU|.  \   )  _) )                    |  |  | |  | | 
UUUUUUUUUUUUUUUUUUUUUU| `.  .    )  )                    |  |__| |__| |_
======================|(_   |  )  _)                     |
     __     __    __  |(__(_|____)_______________________|   __   __   _
|   |__|   |__|  |__| |uuuuuuuuuuuuuuuuuuuuuuuuuuuu,'.uuu|  |  | |  | | 
|   |__|   |__|  |__| |uuuuuuuuuuuuuuuuuuuuuuuuuu,'   `.u|  |__| |__| |_
======================|uuuu_uuuuuu_uuuuuu_uuuuu,'__   __`.
     __     __    __  |uuu| |uuuu| |uuuu| |uuuu||  | |  ||   __   __   _
|   |__|   |__|  |__| |uuu|_|uuuu|_|uuuu|_|uuuu||__| |__||  |  | |  | | 
|   |__|   |__|  |__| |=_====__================'         |  |__| |__| |_
======================||  | |  |  __   __   __   __   __ |______________
  ___  __    ________ ||__| |__| |  | |  | |  | |  | |  ||+++++++++++++_
||_|_||  |  |  |     || _______  |__| |__| |__| |__| |__||++.-------.+| 
||_|_||- |  | -|     |||   |   |                         |++|   |   |+|_
 |_|_||  |  |  |_____|||   |o  |  _     ____________  _  |++|   |-  |+++
---. _|--|__|--|_____|||===|   |_|_|_  /_|__|_______| _|_|++|___|___|+++
----`. ___             ;---'---'      |  |_-|       |__     |       \   
--(_)-'_ _\___________/________|____/_'-(_)-----(_)-' _\____|________\__
________________________________________________________________________
(credit to jrei)
            ''')
    bot.logger.info("Running bot")
    try:
        bot.run(bot.config["token"])
    except KeyboardInterrupt:
        bot.logger.info("Shutting down bot...")
        bot.shutdown_mode = 0
    finally:
        sys.exit(bot.shutdown_mode)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="jackson-bot - Discord Bot")
    parser.add_argument("--debug", "-d", help="Enable debug mode.", action="store_true")
    parser.add_argument("--token", "-t", help="Bot token.", required=True)
    parser.add_argument("--database", "-d", help="Bot owner id.", required=True)
    args = parser.parse_args()
    args = parser.parse_args()
    
    run_bot(args)