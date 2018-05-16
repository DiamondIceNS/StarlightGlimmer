import discord
import re
import traceback
from discord import TextChannel
from discord.ext import commands
from discord.utils import get as dget
from time import time

import utils.sqlite as sql
from utils.channel_logger import ChannelLogger
from utils.config import Config
from utils.exceptions import NoPermission
from utils.language import getlang
from utils.logger import Log
from utils.help_formatter import GlimmerHelpFormatter
from utils.version import VERSION


def get_prefix(bot, msg):
    return sql.get_guild_prefix(msg.guild.id)


cfg = Config()
log = Log(''.join(cfg.name.split()))
bot = commands.Bot(command_prefix=get_prefix, formatter=GlimmerHelpFormatter())
channel_logger = ChannelLogger(bot)
extensions = [
    "commands.animotes",
    "commands.canvas",
    "commands.configuration"
]


@bot.event
async def on_ready():
    log.info("Performing guild check...")
    if sql.get_version() is None:
        sql.init_version(VERSION)
        new_ver_alert = False
    else:
        new_ver_alert = sql.get_version() != VERSION and sql.get_version() is not None
        if new_ver_alert:
            sql.update_version(VERSION)
    for g in bot.guilds:
        log.info("Servicing guild '{0.name}' (ID: {0.id})".format(g))
        row = sql.select_guild_by_id(g.id)
        if row is not None:
            prefix = row['prefix'] if row['prefix'] is not None else cfg.prefix
            if g.name != row['name']:
                await channel_logger.log_to_channel("Guild ID `{0.id}` changed name from **{1}** to **{0.name}** since "
                                                    "last bot start".format(g, row['name']))
                sql.update_guild(g.id, name=g.name)
            alert_channel_id = row['alert_channel'] if row['alert_channel'] is not None else 0
            if new_ver_alert and alert_channel_id is not 0:
                alert_channel = next((x for x in g.channels if x.id == alert_channel_id), None)
                if alert_channel is not None:
                    await alert_channel.send(getlang(g.id, "bot.alert_update").format(VERSION, prefix))
                    log.info("Sent update message to guild {0.name} (ID: {0.id})")
                else:
                    log.info("Could not send update message to guild {0.name} (ID: {0.id}): "
                             "Alert channel could not be found.")
        else:
            await channel_logger.log_to_channel("Joined guild **{0.name}** (ID: `{0.id}`) between sessions at `{1}`"
                                                .format(g, g.me.joined_at.isoformat(' ')))
            sql.add_guild(g.id, g.name, int(g.me.joined_at.timestamp()))
            await print_welcome_message(g)

    db_guilds = sql.get_all_guilds()
    if len(bot.guilds) != len(db_guilds):
        for g in db_guilds:
            if not any(x for x in bot.guilds if x.id == g['id']):
                log.info("Kicked from guild '{0}' (ID: {1}) between sessions".format(g['name'], g['id']))
                await channel_logger.log_to_channel("Kicked from guild **{0}** (ID: `{1}`)".format(g['name'], g['id']))
                sql.delete_guild(g['id'])

    for extension in extensions:
        try:
            bot.load_extension(extension)
        except Exception as e:
            log.error("Failed to load extension {}\n{}: {}".format(extension, type(e).__name__, e))

    print("I am ready!")
    log.info('I am ready!')
    await channel_logger.log_to_channel("I am ready!")


async def print_welcome_message(guild):
    c = next((x for x in guild.channels if x.name == "general" and x.permissions_for(guild.me).send_messages
              and type(x) is TextChannel),
             next((x for x in guild.channels if x.permissions_for(guild.me).send_messages and type(x) is TextChannel),
                  None))
    if c is not None:
        log.info("Printing welcome message to guild {0.name} (ID: {0.id})".format(guild))
        await c.send("Hi! I'm {0}. For a full list of commands, pull up my help page with `{1}help`. "
                     "Happy pixel painting!".format(cfg.name, cfg.prefix))
    else:
        log.info("Welcome message not printed for channel {0.name} (ID: {0.id}): Could not find a default channel."
                 .format(guild))


@bot.event
async def on_guild_join(guild):
    log.info("Joined new guild '{0.name}' (ID: {0.id})".format(guild))
    await channel_logger.log_to_channel("Joined new guild **{0.name}** (ID: `{0.id}`)".format(guild))
    sql.add_guild(guild.id, guild.name, int(guild.me.joined_at.timestamp()))
    await print_welcome_message(guild)


@bot.event
async def on_guild_remove(guild):
    log.info("Kicked from guild '{0.name}' (ID: {0.id})".format(guild))
    await channel_logger.log_to_channel("Kicked from guild **{0.name}** (ID: `{0.id}`)".format(guild))
    sql.delete_guild(guild.id)


@bot.event
async def on_guild_update(before, after):
    if before.name != after.name:
        log.info("Guild {0.name} is now known as {1.name} (ID: {1.id})")
        await channel_logger.log_to_channel("Guild **{0.name}** is now known as **{1.name}** (ID: `{1.id}`)"
                                            .format(before, after))
        sql.update_guild(after.id, name=after.name)


@bot.event
async def on_command_error(ctx, error):
    print(type(error))
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(getlang(ctx.guild.id, "bot.error.command_on_cooldown").format(error.retry_after))
        return
    if isinstance(error, commands.CommandNotFound):
        return
    if isinstance(error, commands.MissingRequiredArgument):
        return
    if isinstance(error, commands.BadArgument):
        return
    if isinstance(error, NoPermission):
        await ctx.send(getlang(ctx.guild.id, "bot.error.no_permission"))
        return
    if isinstance(error, commands.NoPrivateMessage):
        await ctx.send(getlang(ctx.guild.id, "bot.error.no_private_message"))
        return
    if isinstance(error, commands.CommandInvokeError) and isinstance(error.original, discord.HTTPException) \
            and error.original.code == 50013:
        return
    cname = ctx.command.qualified_name if ctx.command is not None else "None"
    await channel_logger.log_to_channel("An error occurred while executing command `{0}` in server **{1.name}** "
                                        "(ID: `{1.id}`):".format(cname, ctx.guild))
    await channel_logger.log_to_channel("```{}```".format(error))
    log.error("An error occurred while executing command {}: {}\n{}"
              .format(cname, error, ''.join(traceback.format_exception(None, error, error.__traceback__))))
    await ctx.send(getlang(ctx.guild.id, "bot.error.unhandled_command_error"))


@bot.event
async def on_message(message):
    if message.author.bot:
        return

    ctx = await bot.get_context(message)
    if ctx.invoked_with:
        await bot.invoke(ctx)
        return

    if message.guild is not None and not message.channel.permissions_for(message.guild.me).send_messages:
        return

    if sql.select_guild_by_id(ctx.guild.id)['autoscan'] == 1:
        default_canvas = sql.select_guild_by_id(ctx.guild.id)['default_canvas']

        if re.search('pixelcanvas\.io/@-?\d+,-?\d+', message.content) is not None:
            ctx.command = dget(dget(bot.commands, name='preview').commands, name='pixelcanvas')
        elif re.search('pixelz\.io/@-?\d+,-?\d+', message.content) is not None:
            ctx.command = dget(dget(bot.commands, name='preview').commands, name='pixelzio')
        elif re.search('pixelzone\.io/\?p=-?\d+,-?\d+', message.content) is not None:
            ctx.command = dget(dget(bot.commands, name='preview').commands, name='pixelzone')
        elif re.search('pxls\.space/#x=\d+&y=\d+', message.content) is not None:
            ctx.command = dget(dget(bot.commands, name='preview').commands, name='pxlsspace')
        elif re.search('@\(?-?\d+, ?-?\d+\)?', message.content) is not None:
            ctx.command = dget(dget(bot.commands, name='preview').commands, name=default_canvas)
        elif re.search('\(?-?\d+, ?-?\d+\)?', message.content) is not None and len(message.attachments) > 0 \
                and message.attachments[0].filename[-4:].lower() == ".png":
            ctx.command = dget(dget(bot.commands, name='diff').commands, name=default_canvas)

        if ctx.command is not None:
            await bot.invoke(ctx)


@bot.command()
async def ping(ctx):
    ping_start = time()
    ping_msg = await ctx.send(getlang(ctx.guild.id, "bot.ping"))
    ping_time = time() - ping_start
    await ping_msg.edit(content=getlang(ctx.guild.id, "bot.pong").format(int(ping_time*1000)))


@bot.command()
async def github(ctx):
    await ctx.send("https://github.com/DiamondIceNS/StarlightGlimmer")


@bot.command()
async def changelog(ctx):
    await ctx.send("https://github.com/DiamondIceNS/StarlightGlimmer/releases")


@bot.command()
async def version(ctx):
    await ctx.send(getlang(ctx.guild.id, "bot.version").format(VERSION))


@bot.command()
async def suggest(ctx, *, suggestion: str):
    await channel_logger.log_to_channel("New suggestion from **{0.name}#{0.discriminator}** (ID: `{0.id}`) in guild "
                                        "**{1.name}** (ID: `{1.id}`):".format(ctx.author, ctx.guild))
    await channel_logger.log_to_channel("> `{}`".format(suggestion))
    await ctx.send(getlang(ctx.guild.id, "bot.suggest"))


@bot.group(name="ditherchart", invoke_without_command=True)
async def ditherchart(ctx):
    pass


@ditherchart.command(name="pixelcanvas")
async def ditherchart_pixelcanvas(ctx):
    f = discord.File("assets/dither_chart_pixelcanvas.png", "assets/dither_chart_pixelcanvas.png")
    await ctx.send(file=f)


@ditherchart.command(name="pixelzio")
async def ditherchart_pixelzio(ctx):
    f = discord.File("assets/dither_chart_pixelzio.png", "assets/dither_chart_pixelzio.png")
    await ctx.send(file=f)


@ditherchart.command(name="pixelzone")
async def ditherchart_pixelzio(ctx):
    f = discord.File("assets/dither_chart_pixelzone.png", "assets/dither_chart_pixelzone.png")
    await ctx.send(file=f)


@ditherchart.command(name="pxlsspace")
async def ditherchart_pixelzio(ctx):
    f = discord.File("assets/dither_chart_pxlsspace.png", "assets/dither_chart_pxlsspace.png")
    await ctx.send(file=f)


@bot.command()
async def invite(ctx):
    await ctx.send(cfg.invite)


bot.run(cfg.token)
