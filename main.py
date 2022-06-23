import sqlite3

from settings import settings

from database import DataBase
from bot import Bot

if __name__ == "__main__":
    db = DataBase()
    bot = Bot(db)
    
    bot.run(settings['token'])
