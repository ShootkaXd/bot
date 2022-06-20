import sqlite3

conn = sqlite3.connect("db.db")
cursor = conn.cursor()


def initialize_database():
    cursor.execute("""CREATE TABLE IF NOT EXISTS users(
        id INT PRIMARY KEY,
        money INT,
        rep INT, 
        level INT
    )""")

    cursor.execute("""CREATE TABLE IF NOT EXISTS items(
        id INT PRIMARY KEY,
        user_id INT NOT NULL,
        name TEXT,
        FOREIGN KEY (user_id) REFERENCES users(id) ON UPDATE CASCADE ON DELETE CASCADE
    )""")

    cursor.execute("""CREATE TABLE IF NOT EXISTS shop_items(
        item_id INT PRIMARY KEY,
        user_id INT NOT NULL,
        cost INT,
        FOREIGN KEY (items) REFERENCES items(id) ON UPDATE CASCADE ON DELETE CASCADE
        FOREIGN KEY (users) REFERENCES users(id) ON UPDATE CASCADE ON DELETE CASCADE
    )""")

    conn.close()
