import discord
import traceback
from discord import TextChannel
from discord.ext import commands

from objects.glimcontext import GlimContext
from utils import canvases, checks, sqlite as sql, utils
from objects.channel_logger import ChannelLogger
from objects.config import Config
from objects.help_formatter import GlimmerHelpFormatter
from objects.logger import Log
from utils.version import VERSION


def get_prefix(bot, msg):
    return sql.guild_get_prefix_by_id(msg.guild.id)


cfg = Config()
log = Log(''.join(cfg.name.split()))
bot = commands.Bot(command_prefix=get_prefix, formatter=GlimmerHelpFormatter())
bot.remove_command('help')
ch_log = ChannelLogger(bot)
extensions = [
    "commands.animotes",
    "commands.canvas",
    "commands.configuration",
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
        is_new_version = sql.version_get() != VERSION and sql.version_get() is not None
        if is_new_version:
            log.info("Database is a previous version. Updating...")
            sql.version_update(VERSION)

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
            prefix = row['prefix'] if row['prefix'] else cfg.prefix
            if g.name != row['name']:
                await ch_log.log("Guild **{1}** is now known as **{0.name}** `(ID:{0.id})`".format(g, row['name']))
                sql.guild_update(g.id, name=g.name)
            if is_new_version:
                ch = next((x for x in g.channels if x.id == row['alert_channel']), None)
                if ch:
                    await ch.send(GlimContext.get_from_guild(g, "bot.alert_update").format(VERSION, prefix))
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
            if not any(x for x in bot.guilds if x.id == g['id']):
                log.info("Kicked from guild '{0}' (ID: {1}) between sessions".format(g['name'], g['id']))
                await ch_log.log("Kicked from guild **{0}** (ID: `{1}`)".format(g['name'], g['id']))
                sql.guild_delete(g['id'])

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
        return
    if isinstance(error, commands.CommandInvokeError):
        if isinstance(error.original, discord.HTTPException) and error.original.code == 50013:
            return
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(ctx.get("bot.error.command_on_cooldown").format(error.retry_after))
        return
    if isinstance(error, commands.CommandNotFound):
        return
    if isinstance(error, commands.MissingRequiredArgument):
        return
    if isinstance(error, commands.NoPrivateMessage):
        await ctx.send(ctx.get("bot.error.no_private_message"))
        return

    # Check errors
    if isinstance(error, checks.IdempotentActionError):
        try:
            f = discord.File("assets/y_tho.png", "y_tho.png")
            await ctx.send(ctx.get("bot.why"), file=f)
        except IOError:
            await ctx.send(ctx.get("bot.why"))
        return
    if isinstance(error, checks.NoJpegsError):
        try:
            f = discord.File("assets/disdain_for_jpegs.gif", "disdain_for_jpegs.gif")
            await ctx.send(ctx.get("bot.error.jpeg"), file=f)
        except IOError:
            await ctx.send(ctx.get("bot.error.jpeg"))
        return
    if isinstance(error, checks.NoPermissionError):
        await ctx.send(ctx.get("bot.error.no_permission"))
        return
    if isinstance(error, checks.NotPngError):
        await ctx.send(ctx.get("bot.error.no_png"))
        return
    if isinstance(error, checks.PilImageError):
        await ctx.send(ctx.get("bot.error.pil_open_exception"))
        return
    if isinstance(error, checks.TemplateHttpError):
        await ctx.send(ctx.get("bot.error.template_http_error"))
        return
    if isinstance(error, checks.UrlError):
        await ctx.send(ctx.get("bot.error.url_error"))
        return
    if isinstance(error, checks.HttpPayloadError):
        await ctx.send(ctx.get("bot.error.http_payload_error").format(canvases.pretty_print[error.canvas]))
        return

    # Uncaught error
    name = ctx.command.qualified_name if ctx.command else "None"
    await ch_log.log("An error occurred executing `{0}` in server **{1.name}** (ID: `{1.id}`):".format(name, ctx.guild))
    await ch_log.log("```{}```".format(error))
    log.error("An error occurred executing '{}': {}\n{}"
              .format(name, error, ''.join(traceback.format_exception(None, error, error.__traceback__))))
    await ctx.send(ctx.get("bot.error.unhandled_command_error"))


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
