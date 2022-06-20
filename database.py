import sqlite3
import os
from typing import Optional

from settings import settings
import database_designer as db_designer

db_designer.initialize_database()

connection = sqlite3.connect(settings['db_file'])
cursor = connection.cursor()
sql = cursor.execute


def action(func):
    def act(*args, no_action=False, **kwargs):
        func(*args, **kwargs)
        if (not no_action):
            connection.commit()
    return act


def get_user(id):
    return sql(
        f"SELECT id FROM users WHERE id = {id}"
    ).fetchone()


@action
def add_user(id):
    sql(f"INSERT INTO users VALUES ({id}, 0, 0, 0)")


@action
def add_user_experience(id, amount):
    user = get_user(id)
    sql(f"UPDATE users SET lvl={user['level'] + amount} WHERE id = {id}")


@action
def add_user_money(id, amount):
    user = get_user(id)
    sql(f"UPDATE users SET money={user['money'] + amount} WHERE id = {id}")


@action
def take_user_money(id, amount):
    user = get_user(id)

    new_money = user['money'] - amount

    if (new_money < 0):
        raise ValueError("Not enough money for operation")

    sql(f"UPDATE users SET money={new_money} WHERE id = {id}")


@action
def add_user_item(id, name):
    sql(f"INSERT INTO items (user_id, name) VALUES ({id}, {name})")


def get_items(page_size, page, filter: Optional[dict] = None):
    query = "SELECT * FROM items"
    if (filter is not None and len(filter) > 0):
        query += " WHERE "
        for key, value in filter.items():
            query += f"{key} = {value}"
    query += f" ORDERY BY id LIMIT {page_size*page-1}, {page_size*page}"
    return sql(query).fetchall()


def get_shop_item(id):
    return sql(f"SELECT * FROM shop_items WHERE item_id = {id}").fetchone()

@action
def remove_shop_item(item_id):
    sql(f"DELETE FROM shop_items WHERE item_id = {item_id}")

@action
def add_shop_item(item_id, cost):
    item = get_shop_item(item_id)
    sql(f"""INSERT INTO shop_items (item_id, user_id, cost) 
      VALUES ({item['id']}, {item['user_id']}, {cost})""")

def get_shop_items(page_size, page, filter: Optional[dict] = None):
    query = "SELECT * FROM shop_items"
    if (filter is not None and len(filter) > 0):
        query += " WHERE "
        for key, value in filter.items():
            query += f"{key} = {value}"
    query += f" ORDERY BY id LIMIT {page_size*page-1}, {page_size*page}"
    return sql(query).fetchall()


def get_shop_item(item_id):
    return sql(f"SELECT * FROM items WHERE id = {item_id}").fetchone()


@action
def buy_shop_item(user_id, item_id):
    remove_shop_item(item_id, no_action=True)
    sql(f"UPDATE items SET user_id = {user_id} WHERE id = {item_id}")


def get_user_level(id):
    experience = get_user(id)['level']
    level = 0
    while (experience >= 100):
        level += 1
        experience -= 100*level
    return level
