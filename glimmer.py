import traceback

import discord
from discord import TextChannel
from discord.ext import commands

from objects import errors
from objects.channel_logger import ChannelLogger
from objects.config import Config
from objects.glimcontext import GlimContext
from objects.help_formatter import GlimmerHelpFormatter
from objects.logger import Log
from utils import canvases, render, sqlite as sql, utils
from utils.version import VERSION


def get_prefix(bot_, msg: discord.Message):
    return [sql.guild_get_prefix_by_id(msg.guild.id), bot_.user.mention + " "] \
        if msg.guild else [cfg.prefix, bot_.user.mention + " "]


cfg = Config()
log = Log(''.join(cfg.name.split()))
bot = commands.Bot(command_prefix=get_prefix, formatter=GlimmerHelpFormatter())
bot.remove_command('help')
ch_log = ChannelLogger(bot)
extensions = [
    "commands.animotes",
    "commands.canvas",
    "commands.configuration",
    "commands.faction",
    "commands.general",
    "commands.template",
]
sql.menu_locks_delete_all()


@bot.event
async def on_ready():
    log.info("Starting Starlight Glimmer v{}!".format(VERSION))
    if sql.version_get() is None:
        sql.version_init(VERSION)
        is_new_version = False
    else:
        old_version = sql.version_get()
        is_new_version = old_version != VERSION and old_version is not None
        if is_new_version:
            log.info("Database is a previous version. Updating...")
            sql.version_update(VERSION)
            if old_version < 1.6 <= VERSION:
                # Fix legacy templates not having a size
                for t in sql.template_get_all():
                    t.size = await render.calculate_size(t)
                    sql.template_update(t)

    log.info("Loading extensions...")
    for extension in extensions:
        try:
            bot.load_extension(extension)
        except Exception as e:
            log.error("Failed to load extension {}\n{}: {}".format(extension, type(e).__name__, e))

    log.info("Performing guilds check...")
    for g in bot.guilds:
        log.info("'{0.name}' (ID: {0.id})".format(g))
        row = sql.guild_get_by_id(g.id)
        if row:
            prefix = row.prefix if row.prefix else cfg.prefix
            if g.name != row.name:
                await ch_log.log("Guild **{1}** is now known as **{0.name}** `(ID:{0.id})`".format(g, row.name))
                sql.guild_update(g.id, name=g.name)
            if is_new_version:
                ch = next((x for x in g.channels if x.id == row.alert_channel), None)
                if ch:
                    await ch.send(GlimContext.get_from_guild(g, "bot.update").format(VERSION, prefix))
                    log.info("- Sent update message")
                else:
                    log.info("- Could not send update message: alert channel not found.")
        else:
            j = g.me.joined_at
            await ch_log.log("Joined guild **{0.name}** (ID: `{0.id}`)".format(g, j.isoformat(' ')))
            log.info("Joined guild '{0.name}' (ID: {0.id}) between sessions at {1}".format(g, j.timestamp()))
            sql.guild_add(g.id, g.name, int(j.timestamp()))
            await print_welcome_message(g)

    db_guilds = sql.guild_get_all()
    if len(bot.guilds) != len(db_guilds):
        for g in db_guilds:
            if not any(x for x in bot.guilds if x.id == g.id):
                log.info("Kicked from guild '{0}' (ID: {1}) between sessions".format(g.name, g.id))
                await ch_log.log("Kicked from guild **{0}** (ID: `{1}`)".format(g.name, g.id))
                sql.guild_delete(g.id)

    log.info('I am ready!')
    await ch_log.log("I am ready!")
    print("I am ready!")


@bot.event
async def on_guild_join(guild):
    log.info("Joined new guild '{0.name}' (ID: {0.id})".format(guild))
    await ch_log.log("Joined new guild **{0.name}** (ID: `{0.id}`)".format(guild))
    sql.guild_add(guild.id, guild.name, int(guild.me.joined_at.timestamp()))
    await print_welcome_message(guild)


@bot.event
async def on_guild_remove(guild):
    log.info("Kicked from guild '{0.name}' (ID: {0.id})".format(guild))
    await ch_log.log("Kicked from guild **{0.name}** (ID: `{0.id}`)".format(guild))
    sql.guild_delete(guild.id)


@bot.event
async def on_guild_update(before, after):
    if before.name != after.name:
        log.info("Guild {0.name} is now known as {1.name} (ID: {1.id})")
        await ch_log.log("Guild **{0.name}** is now known as **{1.name}** (ID: `{1.id}`)".format(before, after))
        sql.guild_update(after.id, name=after.name)


@bot.event
async def on_guild_role_delete(role):
    sql.guild_delete_role(role.id)


@bot.before_invoke
async def on_command_preprocess(ctx):
    log.command(ctx)


@bot.event
async def on_command_error(ctx, error):
    # Command errors
    if isinstance(error, commands.BadArgument):
        pass
    elif isinstance(error, commands.CommandInvokeError) \
            and isinstance(error.original, discord.HTTPException)\
            and error.original.code == 50013:
        pass
    elif isinstance(error, commands.CommandOnCooldown):
        await ctx.send(ctx.s("error.cooldown").format(error.retry_after))
    elif isinstance(error, commands.CommandNotFound):
        pass
    elif isinstance(error, commands.MissingRequiredArgument):
        pass
    elif isinstance(error, commands.NoPrivateMessage):
        await ctx.send(ctx.s("error.no_dm"))

    # Check errors
    elif isinstance(error, errors.BadArgumentErrorWithMessage):
        await ctx.send(error.message)
    elif isinstance(error, errors.IdempotentActionError):
        try:
            f = discord.File("assets/y_tho.png", "y_tho.png")
            await ctx.send(ctx.s("error.why"), file=f)
        except IOError:
            await ctx.send(ctx.s("error.why"))
    elif isinstance(error, errors.NoAttachmentError):
        await ctx.send(ctx.s("error.no_attachment"))
    elif isinstance(error, errors.NoJpegsError):
        try:
            f = discord.File("assets/disdain_for_jpegs.gif", "disdain_for_jpegs.gif")
            await ctx.send(ctx.s("error.jpeg"), file=f)
        except IOError:
            await ctx.send(ctx.s("error.jpeg"))
    elif isinstance(error, errors.NoPermissionError):
        await ctx.send(ctx.s("error.no_permission"))
    elif isinstance(error, errors.NotPngError):
        await ctx.send(ctx.s("error.not_png"))
    elif isinstance(error, errors.PilImageError):
        await ctx.send(ctx.s("error.bad_image"))
    elif isinstance(error, errors.TemplateHttpError):
        await ctx.send(ctx.s("error.cannot_fetch_template"))
    elif isinstance(error, errors.UrlError):
        await ctx.send(ctx.s("error.non_discord_url"))
    elif isinstance(error, errors.HttpPayloadError):
        await ctx.send(ctx.s("error.http").format(canvases.pretty_print[error.canvas]))

    # Uncaught error
    else:
        name = ctx.command.qualified_name if ctx.command else "None"
        await ch_log.log("An error occurred executing `{0}` in server **{1.name}** (ID: `{1.id}`):".format(name, ctx.guild))
        await ch_log.log("```{}```".format(error))
        log.error("An error occurred executing '{}': {}\n{}"
                  .format(name, error, ''.join(traceback.format_exception(None, error, error.__traceback__))))
        await ctx.send(ctx.s("error.unknown"))


@bot.event
async def on_message(message):
    # Ignore channels that can't be posted in
    if message.guild and not message.channel.permissions_for(message.guild.me).send_messages:
        return

    # Ignore other bots
    if message.author.bot:
        return

    # Ignore messages from users currently making a menu choice
    locks = sql.menu_locks_get_all()
    for l in locks:
        if message.author.id == l['user_id'] and message.channel.id == l['channel_id']:
            return

    # Invoke a command if there is one
    ctx = await bot.get_context(message, cls=GlimContext)
    if ctx.invoked_with:
        await bot.invoke(ctx)
        return

    # Autoscan
    await utils.autoscan(ctx)


async def print_welcome_message(guild):
    channels = [x for x in guild.channels if x.permissions_for(guild.me).send_messages and type(x) is TextChannel]
    c = next((x for x in channels if x.name == "general"), next(channels, None))
    if c:
        await c.send("Hi! I'm {0}. For a full list of commands, pull up my help page with `{1}help`. "
                     "Happy pixel painting!".format(cfg.name, cfg.prefix))
        log.info(" - Printed welcome message".format(guild))
    else:
        log.info("- Could not print welcome message: no default channel found".format(guild))


bot.run(cfg.token)
