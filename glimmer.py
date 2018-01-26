import re
from discord.ext import commands
from time import time

from utils.channel_logger import ChannelLogger
from utils.config import Config
from utils.logger import Log
from utils.render import preview, diff
from utils.version import *

cfg = Config()
log = Log('StarlightGlimmer')
description = """
Hi! I'm a Pixelcanvas.io helper bot!

If you ever post a link to pixelcanvas.io, I'll send you a preview of the spot you linked to.
Also, if you upload a PNG template and give me the coordinates of its top left corner, I'll show you the pixels that
don't match and tell you how many mistakes there are.

Lastly, I answer to the following commands:
"""
bot = commands.Bot(command_prefix=cfg.prefix, description=description)
channel_logger = ChannelLogger(bot)

extensions = [
    "commands.pixelcanvas",
    "commands.animotes"
]


@bot.event
async def on_ready():
    log.info("I am ready!")
    for g in bot.guilds:
        log.info("Servicing guild '{0.name}' (ID: {0.id})".format(g))
    for extension in extensions:
        try:
            bot.load_extension(extension)
        except Exception as e:
            log.error("Failed to load extension {}\n{}: {}".format(extension, type(e).__name__, e))


@bot.event
async def on_guild_join(guild):
    log.info("Joined new guild '{0.name}' (ID: {0.id})".format(guild))
    await channel_logger.log_to_channel("Joined new guild **{0.name}** (ID: `{0.id}`)".format(guild))


@bot.event
async def on_guild_remove(guild):
    log.info("Kicked from guild '{0.name}' (ID: {0.id})".format(guild))
    await channel_logger.log_to_channel("Kicked from guild **{0.name}** (ID: `{0.id}`)".format(guild))


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        pages = bot.formatter.format_help_for(ctx, ctx.command)
        for p in pages:
            await ctx.send(p)

    else:
        channel_logger.log_to_channel("An error occurred while executing command {0} in server **{1.name}** "
                                      "(ID: `{1.id}`):".format(ctx.command.qualified_name, ctx.guild))
        channel_logger.log_to_channel("```{}```".format(error))
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

    m1 = re.search('(?:(experimental)?\.pixelcanvas\.io/)?@(-?\d+), ?(-?\d+)/?\s?#?([248])?(?:\d+)?(?: ?(-e))?',
                   message.content)
    m2 = re.search('\(?(-?\d+), ?(-?\d+)\)?(?: (-e)?)?', message.content)
    if m1 is not None:
        x = int(m1.group(2))
        y = int(m1.group(3))
        zoom = int(m1.group(4)) if m1.group(4) is not None else 1
        is_exp = m1.group(1) is not None or m1.group(5) is not None
        await preview(ctx, x, y, zoom, is_exp)

    elif m2 is not None and len(message.attachments) > 0:
        x = int(m2.group(1))
        y = int(m2.group(2))
        att = message.attachments[0]
        is_exp = m2.group(3) is not None
        await diff(ctx, x, y, att, is_exp)


@bot.command()
async def ping(ctx):
    """Pong!"""
    ping_start = time()
    ping_msg = await ctx.send("Pinging...")
    ping_time = time() - ping_start
    await ping_msg.edit(content="Pong! | **{0:.01f}s**".format(ping_time))


@bot.command()
async def github(ctx):
    """Get a link to the GitHub repository"""
    await ctx.send("https://github.com/DiamondIceNS/StarlightGlimmer")


@bot.command()
async def version(ctx):
    """Get the bot's version"""
    await ctx.send("My version number is **{}**".format(VERSION))


@bot.command()
async def suggest(ctx, *, suggestion: str):
    """Suggest a bot feature or change to the dev"""
    await channel_logger.log_to_channel("New suggestion from **{0.name}#{0.discriminator}** (ID: `{0.id}`) in guild "
                                        "**{1.name}** (ID: `{1.id}`):".format(ctx.author, ctx.guild))
    await channel_logger.log_to_channel("> `{}`".format(suggestion))
    await ctx.send("Your suggestion has been sent. Thank you for your input!")


bot.run(cfg.token)
