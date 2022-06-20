from dis import disco
import json
import requests

from GoogleNews import GoogleNews

import discord
from discord.ext import commands
from discord_components import Button, ButtonStyle

from settings import settings
from bot_designer import bot_clear as bot
import database as db

prefix = settings['prefix']

googlenews = GoogleNews(lang='ru')


@bot.command(aliases=['balance', 'cash'])
async def __balance(ctx, member: discord.Member = None):
    if member is None:
        member = ctx.author
        id = ctx.author.id
    else:
        id = member.id

    await ctx.send(embed=discord.Embed(
        description=f"""Баланс пользователя {member} составляет {db.get_user(id)['money']} :newspaper:"""))


@bot.command()
async def hello(ctx):
    author = ctx.message.author
    await ctx.send(f'Hello, {author.mention}!')


@bot.command(aliases=['Help', 'help', 'HELP', 'hELP', 'хелп', 'Хелп', 'ХЕЛП', 'хЕЛП'])
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
    embed.set_thumbnail(url=bot.user.avatar_url)

    embed.set_footer(icon_url=bot.user.avatar_url,
                     text=f'{bot.user.name} © Copyright 2022 | Все права защищены')

    await ctx.send(embed=embed)

    print(
        f'[Logs:info] Справка по командам была успешно выведена | {bot}help ')


@bot.command()
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
    news_em.set_thumbnail(url=bot.user.avatar_url)

    for j in range(10, len(img)):
        news_em.add_field(name=str(img[j]), value=f'[Кликне чтоб посмотреть подробней]({str(urls[j])}) \n --------- \n',
                          inline=False)
    await ctx.send(embed=news_em)


@search.error
async def search(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f'{ctx.author.name}, Укажите аргумент!')


@bot.command()
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
    news_em = discord.Embed(title=f'Главные события',
                            color=discord.Color.red())
    news_em.set_thumbnail(url=bot.user.avatar_url)

    for article in item:
        news_em.add_field(name=article['title'], value=f"{article['description']} [Смотреть]({article['url']})",
                          inline=False)

    await ctx.send(embed=news_em)


@bot.command(aliases=['inventory'])
async def __inventory(ctx, page=1):
    items = db.get_items(10, page, {'user_id': ctx.author.id})
    embed = discord.Embed(title="Инвентарь")

    for item in items:
        embed.add_field(name=f"{item['id']}", value=item['name'])

    await ctx.send(embed=embed)


@bot.command(aliases=['sale', 'продать'])
async def __sale(ctx: commands.Context, id, cost):
    item = db.get_items(1, 1, {'user_id': ctx.author.id, 'id': id})[0]

    db.add_shop_item(item['id'], cost)

    await ctx.message.add_reaction('✅')


@bot.command(aliases=['shop', 'магазин'])
async def __shop(ctx: commands.Context, page):
    items = db.get_shop_items(50, page)
    embed = discord.Embed(title="Инвентарь")

    for item in items:
        embed.add_field(name=f"{item['id']}", value=item['name'])

    await ctx.send(embed=embed)


@bot.command(aliases=['buy', 'купить'])
async def __buy(ctx: commands.Context, item_id):
    item = db.get_shop_item(item_id)

    if (item is None):
        raise ValueError("No such item in shop")

    db.take_user_money(ctx.author.id, item['cost'])

    db.buy_shop_item(ctx.author.id, item['id'])

    await ctx.message.add_reaction('✅')


@bot.command()
async def menu(ctx):
    await ctx.send(
        embed=discord.Embed(title="Меню взаимодействия"),
        components=[
            Button(style=ButtonStyle.green, label="Новости", emoji="📰"),
            Button(style=ButtonStyle.URL, label="GitHub", emoji="🗃",
                   url="https://github.com/ShootkaXd/bot.git")
        ]
    )
    interaction = await bot.wait_for("button_click")
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
            news_em = discord.Embed(
                title=f'Главные события', color=discord.Color.red())
            news_em.set_thumbnail(url=bot.user.avatar_url)

            for article in item:
                news_em.add_field(name=article['title'], value=f"{article['description']} [Смотреть]({article['url']})",
                                  inline=False)
            await ctx.send(embed=news_em)


''' Административные команды '''

@bot.command(aliases=['give'])
@commands.has_permissions(manage_guild=True)
async def __give_item(ctx, member: discord.Member, name):
    db.add_user_item(member.id, name)

    await ctx.message.add_reaction('✅')

@bot.command(aliases=['pay'])
@commands.has_permissions(manage_guild=True)
async def __pay(ctx, member: discord.Member = None, amount: int = None):
    if member is None:
        await ctx.send(f"**{ctx.author}**, укажите пользователя, которому желаете выдать определенную сумму")
        return
    if amount is None:
        await ctx.send(f"**{ctx.author}**, укажите пользователя, которому желаете выдать определенную сумму")
        return
    if amount < 1:
        await ctx.send(f"**{ctx.author}**, укажите сумму больше 1")
        return

    db.add_user_money(member.id, amount)

    await ctx.message.add_reaction('✅')


@bot.command(aliases=['kick', 'кик', 'Кик', 'Kick'])
@commands.has_permissions(kick_members=True)
async def __kick(ctx, member: discord.Member, *, reason=None):
    await member.kick(reason=reason)

    emb_em = discord.Embed(title='Информация',
                           description=f'{member.name.title()}, был изгнан',
                           colour=discord.Color.dark_gold())

    emb_em.set_author(name=member, icon_url=member.avatar_url)
    emb_em.set_footer(
        text=f'Был изгнан пользователем {ctx.message.author.name}', icon_url=ctx.author.avatar_url)

    await ctx.send(embed=emb_em)

    print(
        f'[Logs:moderation] Пользователь {member} был кикнут | {prefix}kick ')


@__kick.error
async def __kick(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        cmd_em = discord.Embed(
            title='Команды',
            colour=discord.Color.dark_gold()
        )
        cmd_em.add_field(
            name='ОШИБКА!', value="У вас недостаточно прав!", inline=False)
        await ctx.send(embed=cmd_em)

    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f'{ctx.author.name}, Укажите аргумент!')


@bot.command(aliases=['Ban', 'ban', 'бан', 'Бан'])
@commands.has_permissions(ban_members=True)
async def __ban(ctx, member: discord.Member, *, reason=None):
    await member.ban(reason=reason)

    emb_em = discord.Embed(title='Информация',
                           description=f'{member.name.title()}, был заблокирован',
                           colour=discord.Color.dark_gold())

    emb_em.set_author(name=member, icon_url=member.avatar_url)
    emb_em.set_footer(text=f'Был заблокирован пользователем {ctx.message.author.name}',
                      icon_url=ctx.author.avatar_url)

    await ctx.send(embed=emb_em)

    print(
        f'[Logs:moderation] Пользователь {member} был заблокирован | {prefix}ban ')


@__ban.error
async def __ban(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        cmd_em = discord.Embed(
            title='Команды',
            colour=discord.Color.dark_gold()
        )
        cmd_em.add_field(
            name='ОШИБКА!', value="У вас недостаточно прав!", inline=False)
        await ctx.send(embed=cmd_em)

    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f'{ctx.author.name}, Укажите аргумент!')


@bot.command(aliases=['cmd', 'цмд'])
@commands.has_permissions(administrator=True)
async def __cmd(ctx):
    cmd_em = discord.Embed(
        title='Команды',
        colour=discord.Color.dark_gold()
    )
    cmd_em.add_field(name='Admin', value='```-news [Показывает вам новости по интересующей вас теме]``` '
                                         '```-search [Видео на интересующие новости]```'
                                         '```-pay @ [Выдать деньги пользователю]```'
                                         '```-help, -cmd, -kick -ban```')
    await ctx.send(embed=cmd_em)


@__cmd.error
async def __cmd(ctx, goodbye):
    if isinstance(goodbye, commands.MissingPermissions):
        cmd_em = discord.Embed(
            title='Команды',
            colour=discord.Color.dark_gold()
        )
        cmd_em.add_field(
            name='ОШИБКА!', value="У вас недостаточно прав!", inline=False)
        await ctx.send(embed=cmd_em)
