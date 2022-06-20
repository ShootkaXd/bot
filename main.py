import os

from . import database_designer
from bot_commands import bot
import settings

if __name__ == "__main__":
    bot.run(settings['token'])
