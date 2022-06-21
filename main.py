from settings import settings

from bot_commands import create_bot

if __name__ == "__main__":
    bot = create_bot()
    bot.run(settings['token'])
