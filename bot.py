from datetime import datetime, timedelta
import json
import requests

import discord
from discord.ext import commands
from discord_components import Button, ButtonStyle, DiscordComponents

from settings import settings
from database import DataBase

PREFIX = settings['prefix']


class Bot(commands.Bot):
    def __init__(self, db: DataBase):
        self.db = db

        intents = discord.Intents.default()
        intents.members = True

        super(Bot, self).__init__(command_prefix=PREFIX, intents=intents)

        self.remove_command('help')
        self.add_commands()

    async def on_command_error(self, ctx, error):
        await ctx.message.add_reaction("❌")
        
        await super(Bot, self).on_command_error(ctx, error)

    async def on_member_join(self, member):
        if self.db.get_user(member.id) is None:
            self.db.add_user(member.id)

    async def on_ready(self):
        print(f"Logged on as {settings['bot_name']}")

        DiscordComponents(self)

        await self.change_presence(
            status=discord.Status.online,
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name='-Help'
            )
        )

        for guild in self.guilds:
            for member in guild.members:
                if self.db.get_user(member.id) is None:
                    self.db.add_user(member.id)

    async def __check_level_and_reply(self, message: discord.Message):
        old_level = self.db.get_user_level(message.author.id)

        self.db.add_user_experience(message.author.id, 1)

        new_level = self.db.get_user_level(message.author.id)

        if new_level > old_level:
            self.db.add_user_money(message.author.id, int(settings['level_reward']))
            await message.reply("Поздравляю с новым уровнем!")

    async def on_message(self, message: discord.Message):
        if len(message.content) > 3:
            await self.__check_level_and_reply(message)

        await super(Bot, self).on_message(message)

    def add_commands(self):
        @self.command(aliases=['balance', 'cash', 'баланс'])
        async def __balance(ctx, member: discord.Member = None):
            if member is None:
                member = ctx.author
                id = ctx.author.id
            else:
                id = member.id

            await ctx.send(embed=discord.Embed(
                description=f"""Баланс пользователя {member} составляет {self.db.get_user(id)['money']} :newspaper:"""))

        @self.command()
        async def hello(ctx):
            author = ctx.message.author
            await ctx.send(f'Hello, {author.mention}!')

        @self.command(aliases=['Help', 'help', 'HELP', 'hELP', 'хелп', 'Хелп', 'ХЕЛП', 'хЕЛП'])
        async def __help(ctx):
            embed = discord.Embed(
                color=0xff9900,
                title='Доступные команды: ',
                description='БОТ находится в разработке',
            )
            embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)

            embed.add_field(name='Информация',
                            value=f'`{PREFIX}help` '
                                f'`{PREFIX}menu` '
                                f'`{PREFIX}search` '
                                f'`{PREFIX}news`  ',
                            inline=False)

            embed.add_field(name='Модерирование',
                            value=f'`{PREFIX}mute` '
                                  f'`{PREFIX}unmute` '
                                  f'`{PREFIX}ban` '
                                  f'`{PREFIX}kick` ',
                            inline=False)
            embed.set_thumbnail(url=self.user.avatar_url)

            embed.set_footer(icon_url=self.user.avatar_url,
                             text=f'{self.user.name} © Copyright 2022 | Все права защищены')

            await ctx.send(embed=embed)

            print(
                f'[Logs:info] Справка по командам была успешно выведена | {self}help ')

        @self.command()
        async def news(ctx, *, rummage=''):
            count = 10
            rummage = rummage.split()
            if rummage:
                query = rummage[0]

            if len(rummage) > 1:
                count = rummage[1]

            item = json.loads(requests.get(
                f'https://newsapi.org/v2/everything?'
                f'{"q=" + query if rummage else "domains=news.google.com,lenta.ru,rbc.ru,russian.rt.com"}'
                f'&language=ru&pageSize={count if int(count) < 15 else 15}'
                f'&page=1&from={(datetime.utcnow() - timedelta(days=1)).isoformat("T")}'
                f'&sortBy=publishedAt&apiKey={settings["NEWS_API_KEY"]}').text
            )

            item = item['articles']

            news_em = discord.Embed(title=f'Главные события',
                                    color=discord.Color.red())
            news_em.set_thumbnail(url=self.user.avatar_url)

            for article in item:
                news_em.add_field(name=article['title'],
                                  value=f"{article['description']} [Смотреть]({article['url']})",
                                  inline=False)

            await ctx.send(embed=news_em)

        @self.command(aliases=['level', 'lvl', 'уровень'])
        async def __level(ctx: commands.Context, member: discord.Member = None):
            user = member if member is not None else ctx.author
            await ctx.message.reply(f"Уровень пользователя {user} равен {self.db.get_user_level(user.id)}")

        @self.command(aliases=['inventory', 'инвентарь'])
        async def __inventory(ctx, page=1):
            items = self.db.get_items(10, page, {'user_id': ctx.author.id})
            embed = discord.Embed(title="Инвентарь")
            embed.description = ''

            for item in items:
                embed.description += f"**{item['id']} - {item['name']}**\n"

            await ctx.send(embed=embed)

        @self.command(aliases=['sell', 'продать'])
        async def __sell(ctx: commands.Context, id, cost):
            item = list(self.db.get_items(1, 1, {'user_id': ctx.author.id, 'id': id}))[0]

            self.db.add_shop_item(item['id'], cost)

            await ctx.message.add_reaction('✅')

        @self.command(aliases=['shop', 'магазин'])
        async def __shop(ctx: commands.Context, page=1):
            items = self.db.get_shop_items(50, page)
            embed = discord.Embed(title="Магазин")
            embed.description = ''

            for shop_item in items:
                item = self.db.get_item(shop_item['item_id'])
                embed.description += f"**{item['id']} - {item['name']}**\n"

            await ctx.send(embed=embed)

        @self.command(aliases=['buy', 'купить'])
        async def __buy(ctx: commands.Context, item_id):
            item = self.db.get_shop_item(item_id)

            if (item is None):
                raise ValueError("No such item in shop")

            self.db.take_user_money(ctx.author.id, int(item['cost']))

            self.db.buy_shop_item(ctx.author.id, item['item_id'])

            self.db.add_user_money(item['user_id'], int(item['cost']))

            await ctx.message.add_reaction('✅')

        @self.command()
        async def menu(ctx):
            await ctx.send(
                embed=discord.Embed(title="Меню взаимодействия"),
                components=[
                    Button(style=ButtonStyle.green, label="Новости", emoji="📰"),
                    Button(style=ButtonStyle.URL, label="GitHub", emoji="🗃",
                           url="https://github.com/ShootkaXd/bot.git")
                ]
            )
            interaction = await self.wait_for("button_click")
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
                    news_em.set_thumbnail(url=self.user.avatar_url)

                    for article in item:
                        news_em.add_field(name=article['title'], value=f"{article['description']} [Смотреть]({article['url']})",
                                        inline=False)
                    await ctx.send(embed=news_em)

        ''' Административные команды '''

        @self.command(aliases=['give'])
        @commands.has_permissions(manage_guild=True)
        async def __give_item(ctx, member: discord.Member, name):
            self.db.add_user_item(member.id, name)

            await ctx.message.add_reaction('✅')

        @self.command(aliases=['pay'])
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

            self.db.add_user_money(member.id, amount)

            await ctx.message.add_reaction('✅')

        @self.command(aliases=['kick', 'кик', 'Кик', 'Kick'])
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
                f'[Logs:moderation] Пользователь {member} был кикнут | {PREFIX}kick ')

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

        @self.command(aliases=['Ban', 'ban', 'бан', 'Бан'])
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
                f'[Logs:moderation] Пользователь {member} был заблокирован | {PREFIX}ban ')

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

        @self.command(aliases=['cmd', 'цмд'])
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
