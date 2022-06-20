from bot_commands import bot
from settings import settings

from bot_commands import create_bot

if __name__ == "__main__":
    create_bot().run(settings['token'])
