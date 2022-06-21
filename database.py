import sqlite3
import os
from typing import List, Optional

from settings import settings
import database_designer as db_designer

db_designer.initialize_database()

connection = sqlite3.connect(settings['db_file'])
cursor = connection.cursor()
sql = cursor.execute

level_trashhold = int(settings['messages_per_level'])


def action(func):
    def act(*args, no_action=False, **kwargs):
        func(*args, **kwargs)
        if not no_action:
            connection.commit()
    return act


def data(item_names: List[str], is_list=False):
    def decorator(func):
        def parse(*args, **kwargs) -> Optional[dict | List[dict]]:
            result = func(*args, **kwargs)
            if not is_list:
                if result is None:
                    return None
                return dict(zip(item_names, result))
            if result is None:
                return []
            parsed_items = []
            for item in result:
                parsed_items.append(dict(zip(item_names, item)))
            return parsed_items
        return parse
    return decorator


@data(['id', 'money', 'rep', 'level'])
def get_user(id):
    return sql(
        f"SELECT * FROM users WHERE id = {id}"
    ).fetchone()


@action
def add_user(id):
    sql(f"INSERT INTO users VALUES ({id}, 0, 0, 0)")


@action
def add_user_experience(id, amount):
    user = get_user(id)
    sql(f"UPDATE users SET level={user['level'] + amount} WHERE id = {id}")


@action
def add_user_money(id, amount):
    user = get_user(id)
    sql(f"UPDATE users SET money={user['money'] + amount} WHERE id = {id}")


@action
def take_user_money(id, amount):
    user = get_user(id)

    new_money = user['money'] - amount

    if new_money < 0:
        raise ValueError("Not enough money for operation")

    sql(f"UPDATE users SET money={new_money} WHERE id = {id}")


@action
def add_user_item(id, name):
    sql(f"INSERT INTO items (user_id, name) VALUES ({id}, '{name}')")


def _get_table_items(table_name, page_size, page, filter: Optional[dict] = None):
    query = f"SELECT * FROM {table_name}"
    if filter is not None and len(filter) > 0:
        query += " WHERE "
        for key, value in filter.items():
            query += f"{key} = {value} AND "
        query = query[:-5]
    query += f" LIMIT {page_size * (page - 1)}, {page_size * page}"
    return sql(query).fetchall()


@data(['id', 'user_id', 'name'], is_list=True)
def get_items(page_size, page, filter: Optional[dict] = None):
    return _get_table_items('items', page_size, page, filter)


@data(['id', 'user_id', 'name'])
def get_item(id):
    return sql(f"SELECT * FROM items WHERE id = {id}").fetchone()


@action
def remove_shop_item(item_id):
    sql(f"DELETE FROM shop_items WHERE id = {item_id}")


@action
def add_shop_item(item_id, cost):
    item = get_item(item_id)
    sql(f"""INSERT INTO shop_items (id, user_id, cost) 
      VALUES ({item['id']}, {item['user_id']}, {cost})""")


@data(['item_id', 'user_id', 'cost'], is_list=True)
def get_shop_items(page_size, page, filter: Optional[dict] = None):
    return _get_table_items('shop_items', page_size, page, filter)


@data(['item_id', 'user_id', 'cost'])
def get_shop_item(item_id):
    return sql(f"SELECT * FROM shop_items WHERE id = {item_id}").fetchone()


@action
def buy_shop_item(user_id, item_id):
    remove_shop_item(item_id, no_action=True)
    sql(f"UPDATE items SET user_id = {user_id} WHERE id = {item_id}")


def get_user_level(id):
    experience = get_user(id)['level']
    level = 0
    while experience >= level_trashhold:
        level += 1
        experience -= level_trashhold*level
    return level
