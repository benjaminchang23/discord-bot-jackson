
#!/usr/bin/env python3

import logging
import os
import sys

def create_file_h(log_path, file_name):
    file_path = os.path.join(log_path, file_name)
    return logging.FileHandler(file_path)

def init_logger(bot, debug=False):
    # Log directory.
    if not os.path.exists(bot.log_dir):
        os.makedirs(bot.log_dir)

    # Root logging level.
    logging.getLogger().setLevel(logging.DEBUG)

    # Log format.
    formatter = ColorFormatter('%(asctime)s %(name)s %(levelname)s %(module)s %(funcName)s %(lineno)d: %(message)s', datefmt="[%Y/%m/%d %H:%M]")
    
    # Set up discord logger.
    discord_log = logging.getLogger("discord")
    discord_log.setLevel(logging.INFO)

    discord_file_h = create_file_h(bot.log_dir, "discord.log")
    discord_file_h.setLevel(logging.INFO)
    discord_file_h.setFormatter(formatter)
    discord_log.addHandler(discord_file_h)
    
    # Set up bot logger.
    bot_logger = logging.getLogger("jackson-bot")
   
    bot_file_h = create_file_h(bot.log_dir, "jackson-bot.log")
    bot_file_h.setFormatter(formatter)
    bot_logger.addHandler(bot_file_h)

    # If debug is enabled, also write to stdout.
    if debug:
        bot_std_h = logging.StreamHandler(sys.stdout)
        bot_std_h.setFormatter(formatter)
        bot_logger.addHandler(bot_std_h)

        discord_std_h = logging.StreamHandler(sys.stdout)
        discord_std_h.setLevel(logging.INFO)
        discord_std_h.setFormatter(formatter)
        discord_log.addHandler(discord_std_h)

    bot_logger.debug("Returning bot logger.")
    return bot_logger