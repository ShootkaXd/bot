import sqlite3
from typing import List, Optional

from settings import settings

LEVEL_THRESHOLD = int(settings['messages_per_level'])
DB_PATH = settings['db_file']

class DataBase:
    def __init__(self):
        self.connection = sqlite3.connect(DB_PATH)
        self.cursor = self.connection.cursor()
        self.sql = self.cursor.execute

        self.initialize()
    
    @staticmethod
    def data(item_names: List[str]):
        def decorator(func):
            def parse(*args, **kwargs) -> Optional[dict | List[dict]]:
                result = func(*args, **kwargs)

                if result is None:
                    return None
                
                return dict(zip(item_names, result))

            return parse

        return decorator

    @staticmethod
    def data_many(item_names: List[str]):
        def decorator(func):
            def parse(*args, **kwargs) -> Optional[dict | List[dict]]:
                result = func(*args, **kwargs)

                if result is None:
                    return []
                
                for row in result:
                    yield dict(zip(item_names, row))

            return parse

        return decorator

    @staticmethod
    def action(func):
        def act(self, *args, no_action=False, **kwargs):
            func(self, *args, **kwargs)

            if not no_action:
                self.connection.commit()

        return act

    def initialize(self):
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY NOT NULL,
            money INTEGER,
            rep INTEGER, 
            level INTEGER
        )""")

        self.connection.commit()

        self.cursor.execute("""CREATE TABLE IF NOT EXISTS items(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id) ON UPDATE CASCADE ON DELETE CASCADE
        )""")

        self.connection.commit()

        self.cursor.execute("""CREATE TABLE IF NOT EXISTS shop_items(
            id INT PRIMARY KEY NOT NULL,
            user_id INTEGER NOT NULL,
            cost INTEGER,
            FOREIGN KEY (id) REFERENCES items(id) ON UPDATE CASCADE ON DELETE CASCADE,
            FOREIGN KEY (usqer_id) REFERENCES users(id) ON UPDATE CASCADE ON DELETE CASCADE
        )""")

        self.connection.commit()

    @data(['id', 'money', 'rep', 'level'])
    def get_user(self, id):
        return self.sql(
            f"SELECT * FROM users WHERE id = {id}"
        ).fetchone()

    @action
    def add_user(self, id):
        self.sql(f"INSERT INTO users VALUES ({id}, 0, 0, 0)")

    @action
    def add_user_experience(self, id, amount):
        user = self.get_user(id)
        self.sql(f"UPDATE users SET level={user['level'] + amount} WHERE id = {id}")

    @action
    def add_user_money(self, id, amount):
        user = self.get_user(id)
        self.sql(f"UPDATE users SET money={user['money'] + amount} WHERE id = {id}")

    @action
    def take_user_money(self, id, amount):
        user = self.get_user(id)

        new_money = user['money'] - amount

        if new_money < 0:
            raise ValueError("Not enough money for operation")

        self.sql(f"UPDATE users SET money={new_money} WHERE id = {id}")

    @action
    def add_user_item(self, id, name):
        self.sql(f"INSERT INTO items (user_id, name) VALUES ({id}, '{name}')")

    def _get_table_items(self, table_name, page_size, page, filter: Optional[dict] = None):
        query = f"SELECT * FROM {table_name}"
        if filter is not None and len(filter) > 0:
            query += " WHERE "
            for key, value in filter.items():
                query += f"{key} = {value} AND "
            query = query[:-5]
        query += f" LIMIT {page_size * (page - 1)}, {page_size * page}"
        return self.sql(query).fetchall()

    @data_many(['id', 'user_id', 'name'])
    def get_items(self, page_size, page, filter: Optional[dict] = None):
        return self._get_table_items('items', page_size, page, filter)

    @data(['id', 'user_id', 'name'])
    def get_item(self, id):
        return self.sql(f"SELECT * FROM items WHERE id = {id}").fetchone()

    @action
    def remove_shop_item(self, item_id):
        self.sql(f"DELETE FROM shop_items WHERE id = {item_id}")

    @action
    def add_shop_item(self, item_id, cost):
        item = self.get_item(item_id)
        self.sql(f"""INSERT INTO shop_items (id, user_id, cost) 
          VALUES ({item['id']}, {item['user_id']}, {cost})""")

    @data_many(['item_id', 'user_id', 'cost'])
    def get_shop_items(self, page_size, page, filter: Optional[dict] = None):
        return self._get_table_items('shop_items', page_size, page, filter)

    @data(['item_id', 'user_id', 'cost'])
    def get_shop_item(self, item_id):
        return self.sql(f"SELECT * FROM shop_items WHERE id = {item_id}").fetchone()

    @action
    def buy_shop_item(self, user_id, item_id):
        self.remove_shop_item(item_id, no_action=True)
        self.sql(f"UPDATE items SET user_id = {user_id} WHERE id = {item_id}")

    def get_user_level(self, id):
        experience = self.get_user(id)['level']
        level = 0
        while experience >= LEVEL_THRESHOLD*(level + 1):
            level += 1
            experience -= LEVEL_THRESHOLD * level
        return level
