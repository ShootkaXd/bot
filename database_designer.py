import sqlite3
from settings import settings

conn = sqlite3.connect(settings['db_file'])
cursor = conn.cursor()


def initialize_database():
    cursor.execute("""CREATE TABLE IF NOT EXISTS users(
        id INT PRIMARY KEY NOT NULL,
        money INT,
        rep INT, 
        level INT
    )""")
    
    conn.commit()

    cursor.execute("""CREATE TABLE IF NOT EXISTS items(
        id INT PRIMARY KEY AUTOINCREMENT,
        user_id INT NOT NULL,
        name TEXT,
        FOREIGN KEY (user_id) REFERENCES users(id) ON UPDATE CASCADE ON DELETE CASCADE
    )""")

    conn.commit()

    cursor.execute("""CREATE TABLE IF NOT EXISTS shop_items(
        id INT PRIMARY KEY NOT NULL,
        user_id INT NOT NULL,
        cost INT,
        FOREIGN KEY (id) REFERENCES items(id) ON UPDATE CASCADE ON DELETE CASCADE,
        FOREIGN KEY (user_id) REFERENCES users(id) ON UPDATE CASCADE ON DELETE CASCADE
    )""")

    conn.commit()

    conn.close()
