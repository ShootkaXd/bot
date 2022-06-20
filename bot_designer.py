import discord

from discord.ext import commands
from discord_components import DiscordComponents

from settings import settings
from database import add_user, add_user_experience, cursor, connection as conn, get_user, get_user_level

intents = discord.Intents.default()
intents.members = True

prefix = settings['prefix']


def create_bot_clean():
    bot = commands.Bot(command_prefix=prefix, intents=intents)

    bot.remove_command('help')

    @bot.event
    async def on_command_error(ctx, error):
        await ctx.message.add_reaction("❌")

    @bot.event
    async def on_member_join(member):
        if get_user(member.id) is None:
            add_user(member.id)

    @bot.event
    async def on_ready():
        print(f"Logged on as {settings['bot_name']}")
        DiscordComponents(bot)
        await bot.change_presence(
            status=discord.Status.online,
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name='-Help'
            )
        )
        for guild in bot.guilds:
            for member in guild.members:
                if get_user(member.id) is None:
                    add_user(member.id)
        conn.commit()

    @bot.event
    async def on_message(message: discord.Message):
        if (message.author.id == bot.user.id):
            return

        old_level = get_user_level(message.author.id)

        add_user_experience(message.author.id, 1)

        new_level = get_user_level(message.author.id)

        if (new_level > old_level):
            await message.reply("Поздравляю с новым уровнем!")

    return bot
