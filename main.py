import json
import requests
import discord
import sqlite3

from settings import settings
from GoogleNews import GoogleNews
from discord.ext import commands
from discord_components import DiscordComponents, ComponentsBot, Button, ButtonStyle
from tabulate import tabulate
from random import random

bot_baraholka = commands.Bot(command_prefix=settings['prefix'])
prefix = settings['prefix']
bot_baraholka.remove_command('help')
googlenews = GoogleNews(lang='ru')
conn = sqlite3.connect("Discord_database.db")
cursor = conn.cursor()

# cursor.execute("""CREATE TABLE IF NOT EXISTS users(
#     name TEXT,
#     id INT,
#     money INT,
#     rep INT,
#     lvl INT
# )""")
# conn.commit()

cursor.execute("""CREATE TABLE IF NOT EXISTS shop(
    id INT,
    type TEXT,
    name TEXT, 
    cost INT
)""")
conn.commit()


@bot_baraholka.event
async def on_ready():
    cursor.execute("""CREATE TABLE IF NOT EXISTS users(
        name TEXT,
        id INT,
        money INT,
        rep INT, 
        lvl INT
    )""")
    print(f"Logged on as {settings['bot']}")
    DiscordComponents(bot_baraholka)
    await bot_baraholka.change_presence(status=discord.Status.online, activity=discord.Game('-Help'))
    for guild in bot_baraholka.guilds:
        for member in guild.members:
            if cursor.execute(f"SELECT id FROM users WHERE id = {member.id}").fetchone() is None:
                cursor.execute(f"INSERT INTO users VALUES ('{member}', {member.id}, 0, 0, 1)")
            else:
                pass
    conn.commit()


@bot_baraholka.event
async def on_member_join(member):
    if cursor.execute(f"SELECT id FROM users WHERE id = {member.id}").fetchone() is None:
        cursor.execute(f"INSERT INTO users VALUES ('{member}', {member.id}, 0, 0, 1)")
        conn.commit()
    else:
        pass


@bot_baraholka.command(aliases=['balance', 'cash'])
async def __balance(ctx, member: discord.Member = None):
    if member is None:
        await ctx.send(embed=discord.Embed(discription=f"""Баланс пользователя **{ctx.author}** составляет **{cursor.execute("SELECT money FROM users WHERE id = {}".format(ctx.author.id)).fetchone()[0]} :leaves:**"""))
    else:
        await ctx.send(embed=discord.Embed(discription=f"""Баланс пользователя **{member}** составляет **{cursor.execute("SELECT money FROM users WHERE id = {}".format(member.id)).fetchone()[0]}:leaves:**"""))


@bot_baraholka.command()
async def hello(ctx):
    author = ctx.message.author
    await ctx.send(f'Hello, {author.mention}!')


@bot_baraholka.command(aliases=['Help', 'help', 'HELP', 'hELP', 'хелп', 'Хелп', 'ХЕЛП', 'хЕЛП'])
async def __help(ctx):
    embed = discord.Embed(
        color=0xff9900,
        title='Доступные команды: ',
        description='БОТ находится в разработке',
    )
    embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)

    embed.add_field(name='Информация',
                    value=f'`{prefix}help` '
                          f'`{prefix}menu` '
                          f'`{prefix}search` '
                          f'`{prefix}news`  ',
                    inline=False)

    embed.add_field(name='Модерирование',
                    value=f'`{prefix}mute` '
                          f'`{prefix}unmute` '
                          f'`{prefix}ban` '
                          f'`{prefix}kick` ',
                    inline=False)
    embed.set_thumbnail(url=bot_baraholka.user.avatar_url)

    embed.set_footer(icon_url=bot_baraholka.user.avatar_url,
                     text=f'{bot_baraholka.user.name} © Copyright 2022 | Все права защищены')

    await ctx.send(embed=embed)

    print(f'[Logs:info] Справка по командам была успешно выведена | {bot_baraholka}help ')


@bot_baraholka.command()
async def search(ctx, *, rummage):
    topic = str(rummage)
    item = GoogleNews(period='2d')
    item.search(rummage)
    # googlenews.get_page(2)
    item.page_at(2)

    item.get_texts()
    urls = item.get_links()
    img = item.get_texts()
    news_em = discord.Embed(
        title=f'Новости о {topic}',
        color=discord.Color.red(),
    )
    news_em.set_thumbnail(url=bot_baraholka.user.avatar_url)

    for j in range(10, len(img)):
        news_em.add_field(name=str(img[j]), value=f'[Кликне чтоб посмотреть подробней]({str(urls[j])}) \n --------- \n',
                          inline=False)
    await ctx.send(embed=news_em)


@search.error
async def search(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f'{ctx.author.name}, Укажите аргумент!')


@bot_baraholka.command()
async def news(ctx, *, rummage=''):
    count = 10
    rummage = rummage.split()
    if rummage:
        query = rummage[0]
    if len(rummage) > 1:
        count = rummage[1]
    item = json.loads(requests.get(
        f'https://newsapi.org/v2/everything?{"q=" + query if rummage else "domains=news.google.com,lenta.ru,rbc.ru,russian.rt.com"}&language=ru&pageSize={count if int(count) < 15 else 15}&page=1&from=2022-05-18&sortBy=publishedAt&apiKey={settings["NEWS_API_KEY"]}').text)
    item = item['articles']
    news_em = discord.Embed(title=f'Главные события', color=discord.Color.red())
    news_em.set_thumbnail(url=bot_baraholka.user.avatar_url)

    for article in item:
        news_em.add_field(name=article['title'], value=f"{article['description']} [Смотреть]({article['url']})",
                          inline=False)
    await ctx.send(embed=news_em)


@bot_baraholka.command()
async def menu(ctx):
    await ctx.send(
        embed=discord.Embed(title="Меню взаимодействия"),
        components=[
            Button(style=ButtonStyle.green, label="Новости", emoji="📰"),
            Button(style=ButtonStyle.URL, label="GitHub", emoji="🗃", url="https://github.com/ShootkaXd/bot.git")
        ]
    )
    interaction = await bot_baraholka.wait_for("button_click")
    if interaction.channel == ctx.channel:
        if interaction.component.label == "Новости":
            count = 10
            rummage = ''
            if rummage:
                query = rummage[0]
            if len(rummage) > 1:
                count = rummage[1]
            item = json.loads(requests.get(
                f'https://newsapi.org/v2/everything?{"q=" + query if rummage else "domains=news.google.com,lenta.ru,rbc.ru,russian.rt.com"}&language=ru&pageSize={count if int(count) < 15 else 15}&page=1&from=2022-05-18&sortBy=publishedAt&apiKey={settings["NEWS_API_KEY"]}').text)
            item = item['articles']
            news_em = discord.Embed(title=f'Главные события', color=discord.Color.red())
            news_em.set_thumbnail(url=bot_baraholka.user.avatar_url)

            for article in item:
                news_em.add_field(name=article['title'], value=f"{article['description']} [Смотреть]({article['url']})",
                                  inline=False)
            await ctx.send(embed=news_em)


''' Административные команды '''


@bot_baraholka.command(aliases=['kick', 'кик', 'Кик', 'Kick'])
@commands.has_permissions(administrator=True)
async def __kick(ctx, member: discord.Member, *, reason=None):
    await member.kick(reason=reason)

    emb_em = discord.Embed(title='Информация',
                           description=f'{member.name.title()}, был выгнан',
                           colour=discord.Color.dark_gold())

    emb_em.set_author(name=member, icon_url=member.avatar_url)
    emb_em.set_footer(text=f'Был выгнан администратором {ctx.message.author.name}', icon_url=ctx.author.avatar_url)

    await ctx.send(embed=emb_em)

    print(f'[Logs:moderation] Пользователь {member} был кикнут | {prefix}kick ')


@__kick.error
async def __kick(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        cmd_em = discord.Embed(
            title='Команды',
            colour=discord.Color.dark_gold()
        )
        cmd_em.add_field(name='ОШИБКА!', value="У вас недостаточно прав!", inline=False)
        await ctx.send(embed=cmd_em)

    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f'{ctx.author.name}, Укажите аргумент!')


@bot_baraholka.command(aliases=['Ban', 'ban', 'бан', 'Бан'])
@commands.has_permissions(administrator=True)
async def __ban(ctx, member: discord.Member, *, reason=None):
    await member.ban(reason=reason)

    emb_em = discord.Embed(title='Информация',
                           description=f'{member.name.title()}, был заблокирован',
                           colour=discord.Color.dark_gold())

    emb_em.set_author(name=member, icon_url=member.avatar_url)
    emb_em.set_footer(text=f'Был заблокирован администратором {ctx.message.author.name}',
                      icon_url=ctx.author.avatar_url)

    await ctx.send(embed=emb_em)

    print(f'[Logs:moderation] Пользователь {member} был заблокирован | {prefix}ban ')


@__ban.error
async def __ban(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        cmd_em = discord.Embed(
            title='Команды',
            colour=discord.Color.dark_gold()
        )
        cmd_em.add_field(name='ОШИБКА!', value="У вас недостаточно прав!", inline=False)
        await ctx.send(embed=cmd_em)

    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f'{ctx.author.name}, Укажите аргумент!')


@bot_baraholka.command(aliases=['cmd', 'цмд'])
@commands.has_permissions(administrator=True)
async def __cmd(ctx):
    cmd_em = discord.Embed(
        title='Команды',
        colour=discord.Color.dark_gold()
    )
    cmd_em.add_field(name='News Command', value='```-news [Показывает вам новости по интересующей вас теме]``` '
                                                '```-search [Видео на интересующие новости]```'
                                                '```-help, -cmd, -kick -ban```')
    await ctx.send(embed=cmd_em)


@__cmd.error
async def __cmd(ctx, goodbye):
    if isinstance(goodbye, commands.MissingPermissions):
        cmd_em = discord.Embed(
            title='Команды',
            colour=discord.Color.dark_gold()
        )
        cmd_em.add_field(name='ОШИБКА!', value="У вас недостаточно прав!", inline=False)
        await ctx.send(embed=cmd_em)


bot_baraholka.run(settings['token'])
