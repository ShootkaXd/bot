from settings import settings
from GoogleNews import GoogleNews
import discord
from discord.ext import commands


bot_baraholka = commands.Bot(command_prefix=settings['prefix'])
prefix = settings['prefix']
bot_baraholka.remove_command('help')
googlenews = GoogleNews(lang='ru')


@bot_baraholka.event
async def on_ready():
    print(f"Logged on as {settings['bot']}")
    await bot_baraholka.change_presence(status=discord.Status.online, activity=discord.Game('$Help')) # Статус бота


@bot_baraholka.event
async def on_command_error(ctx, error):
    pass


@bot_baraholka.command()
async def hello(ctx):
    author = ctx.message.author # Объявляем переменную author и записываем туда информацию об авторе.
    await ctx.send(f'Hello, {author.mention}!') # Выводим сообщение с упоминанием автора, обращаясь к переменной author.


@bot_baraholka.command(aliases=['Help', 'help', 'HELP', 'hELP', 'хелп', 'Хелп', 'ХЕЛП', 'хЕЛП'])
async def __help(ctx):
    embed = discord.Embed(
        color = 0xff9900,
        title = 'Доступные команды: ',
        description = 'БОТ находится в разработке',
    )
    embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)

    embed.add_field(name='Информация',
                  value=f'`{prefix}help` '
                        f'`{prefix}search` '
                        f'`{prefix}news` ',
                  inline=False)

    embed.add_field(name='Модерирование',
                  value=f'`{prefix}мут` '
                        f'`{prefix}ban` '
                        f'`{prefix}kick` '
                        f'`{prefix}cmd` ',
                  inline=False)
    embed.set_thumbnail(url=bot_baraholka.user.avatar_url)

    embed.set_footer(icon_url=bot_baraholka.user.avatar_url, text=f'{bot_baraholka.user.name} © Copyright 2022 | Все права защищены')

    await ctx.send(embed = embed)

    print(f'[Logs:info] Справка по командам была успешно выведена | {bot_baraholka}help ')


@bot_baraholka.command()
async def search(ctx, *, search):
    topic = str(search)
    googlenews = GoogleNews(period='2d')
    googlenews.search(search)
    # googlenews.get_page(2)
    googlenews.page_at(2)

    texts = googlenews.get_texts()
    urls = googlenews.get_links()
    img = googlenews.get_texts()
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


''' Административные команды '''


@bot_baraholka.command(aliases=['kick', 'кик', 'Кик', 'Kick'])
@commands.has_permissions(administrator=True)
async def __kick(ctx, member: discord.Member, *, reason=None):
    await ctx.channnel.purge(limit=1)
    await ctx.message.add_reaction('✅')
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
                           description=f'{member.name.title()}, был выгнан',
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
