import re
from discord.ext import commands
from discord import TextChannel
from time import time

from utils.channel_logger import ChannelLogger
from utils.config import Config
from utils.logger import Log
from utils.render import *
from utils.version import VERSION
from utils.exceptions import *
import utils.sqlite as sql


def get_prefix(bot, msg):
    if msg.guild is not None:
        row = sql.select_guild_by_id(msg.guild.id)
        if row is not None and row['prefix'] is not None:
            return row['prefix']
    return cfg.prefix


cfg = Config()
log = Log('StarlightGlimmer')
description = """
Hi! I'm a Pixelcanvas.io helper bot!

If you ever post a link to a supported pixel-placing website, I'll send you a preview of the spot you linked to.
Also, if you upload a PNG template and give me the coordinates of its top left corner, I'll show you the pixels that
don't match and tell you how many mistakes there are.

Lastly, I answer to the following commands:
"""
bot = commands.Bot(command_prefix=get_prefix, description=description)
channel_logger = ChannelLogger(bot)

extensions = [
    "commands.pixelcanvas",
    "commands.pixelzio",
    "commands.configuration",
    "commands.animotes"
]


@bot.event
async def on_ready():
    log.info("Performing guild check...")
    new_ver_alert = sql.get_version() != VERSION
    if new_ver_alert:
        sql.update_version(VERSION)
    for g in bot.guilds:
        log.info("Servicing guild '{0.name}' (ID: {0.id})".format(g))
        row = sql.select_guild_by_id(g.id)
        if row is not None:
            prefix = row['prefix'] if row['prefix'] is not None else "g!"
            if g.name != row['name']:
                await channel_logger.log_to_channel("Guild ID `{0.id}` changed name from **{1}** to **{0.name}** since "
                                                    "last bot start".format(g, row['name']))
                sql.update_guild(g.id, name=g.name)
            alert_channel_id = row['alert_channel'] if row['alert_channel'] is not None else 0
            if new_ver_alert and alert_channel_id is not 0:
                alert_channel = next((x for x in g.channels if x.id == alert_channel_id), None)
                if alert_channel is not None:
                    await alert_channel.send("This bot has updated to version **{}**! Check out the command help page "
                                             "for new commands with `{}help`, or visit https://github.com/DiamondIceNS/"
                                             "StarlightGlimmer/releases for the full changelog.".format(VERSION,
                                                                                                        prefix))
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
             next((x for x in guild.channels if x.permissions_for(guild.me).send_messages and type(x) is TextChannel), None))
    if c is not None:
        log.info("Printing welcome message to guild {0.name} (ID: {0.id})".format(guild))
        await c.send("Hi! I'm Starlight Glimmer. "
                     "For a full list of commands, pull up my help page with `{}help`. "
                     "Happy pixel painting!".format("g!"))
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
    if isinstance(error, commands.MissingRequiredArgument):
        pages = bot.formatter.format_help_for(ctx, ctx.command)
        for p in pages:
            await ctx.send(p)
        return
    if isinstance(error, commands.BadArgument):
        pages = bot.formatter.format_help_for(ctx, ctx.command)
        for p in pages:
            await ctx.send(p)
        return
    if isinstance(error, NoPermission):
        await ctx.send("You do not have permission to use this command.")
        return
    if isinstance(error, commands.NoPrivateMessage):
        await ctx.send("That command only works in guilds.")
        return
    await channel_logger.log_to_channel("An error occurred while executing command {0} in server **{1.name}** "
                                        "(ID: `{1.id}`):".format(ctx.command.qualified_name, ctx.guild))
    await channel_logger.log_to_channel("```{}```".format(error))
    log.error("An error occurred while executing command {}: {}".format(ctx.command.qualified_name, error))


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

    if message.content == "{} help".format(bot.user.mention):
        pages = bot.formatter.format_help_for(ctx, bot)
        for p in pages:
            await ctx.send(p)
        return

    if sql.select_guild_by_id(ctx.guild.id)['autoscan'] == 1:
        default_canvas = sql.select_guild_by_id(ctx.guild.id)['default_canvas']
        pc_match = re.search(
            '(?:(experimental\.)?pixelcanvas\.io/)@(-?\d+), ?(-?\d+)/?(?:\s?#?(\d+))?(?: ?(-e))?',
            message.content)
        pzio_match = re.search('(?:pixelz.io/)@(-?\d+), ?(-?\d+)/?(?:\s?#?(\d+))?', message.content)

        prev_match = re.search('@\(?(-?\d+), ?(-?\d+)\)?(?: ?#(\d+))?(?: (-e)?)?', message.content)
        else_match = re.search('\(?(-?\d+), ?(-?\d+)\)?(?: ?#(\d+))?(?: (-e)?)?', message.content)
        if pc_match is not None:
            x = int(pc_match.group(2))
            y = int(pc_match.group(3))
            zoom = int(pc_match.group(4)) if pc_match.group(4) is not None else 1
            is_exp = pc_match.group(1) is not None or pc_match.group(5) is not None
            await pixelcanvasio_preview(ctx, x, y, zoom, is_exp)
            return

        if pzio_match is not None:
            x = int(pzio_match.group(1))
            y = int(pzio_match.group(2))
            zoom = int(pzio_match.group(3)) if pzio_match.group(3) is not None else 1
            zoom = max(min(zoom, 16), 1)
            await pixelzio_preview(ctx, x, y, zoom)
            return

        if prev_match is not None:
            x = int(prev_match.group(1))
            y = int(prev_match.group(2))
            zoom = int(prev_match.group(3)) if prev_match.group(3) is not None else 1
            zoom = max(min(zoom, 16), 1)
            is_exp = prev_match.group(4) is not None
            if default_canvas == "pixelcanvas.io":
                await pixelcanvasio_preview(ctx, x, y, zoom, is_exp)
            elif default_canvas == "pixelz.io":
                await pixelzio_preview(ctx, x, y, zoom)
            return

        if else_match is not None:
            x = int(else_match.group(1))
            y = int(else_match.group(2))
            zoom = int(else_match.group(3)) if else_match.group(3) is not None else 1
            zoom = max(min(zoom, 16), 1)
            is_exp = else_match.group(4) is not None
            if len(message.attachments) > 0:
                att = message.attachments[0]
                if default_canvas == "pixelcanvas.io":
                    await pixelcanvasio_diff(ctx, x, y, att, is_exp)
                elif default_canvas == "pixelz.io":
                    await pixelzio_diff(ctx, x, y, att)
            else:
                if default_canvas == "pixelcanvas.io":
                    await pixelcanvasio_preview(ctx, x, y, zoom, is_exp)
                elif default_canvas == "pixelz.io":
                    await pixelzio_preview(ctx, x, y, zoom)


@bot.command()
async def ping(ctx):
    """Pong!"""
    ping_start = time()
    ping_msg = await ctx.send("Pinging...")
    ping_time = time() - ping_start
    await ping_msg.edit(content="Pong! | **{0:.01f}s**".format(ping_time))


@bot.command()
async def github(ctx):
    """Get a link to my GitHub repository"""
    await ctx.send("https://github.com/DiamondIceNS/StarlightGlimmer")


@bot.command()
async def changelog(ctx):
    """Get a link to my releases page for changelog info"""
    await ctx.send("https://github.com/DiamondIceNS/StarlightGlimmer/releases")


@bot.command()
async def version(ctx):
    """Get my version"""
    await ctx.send("My version number is **{}**".format(VERSION))


@bot.command()
async def suggest(ctx, *, suggestion: str):
    """Suggest a bot feature or change to the dev"""
    await channel_logger.log_to_channel("New suggestion from **{0.name}#{0.discriminator}** (ID: `{0.id}`) in guild "
                                        "**{1.name}** (ID: `{1.id}`):".format(ctx.author, ctx.guild))
    await channel_logger.log_to_channel("> `{}`".format(suggestion))
    await ctx.send("Your suggestion has been sent. Thank you for your input!")


bot.run(cfg.token)
