import logging
import traceback

import discord
from discord import TextChannel

from commands import *
from objects.bot_objects import GlimContext
from objects.errors import *
import utils
from utils import canvases, config, http, render, sqlite as sql
from utils.version import VERSION


def get_prefix(bot_, msg: discord.Message):
    return [sql.guild_get_prefix_by_id(msg.guild.id), bot_.user.mention + " "] \
        if msg.guild else [config.PREFIX, bot_.user.mention + " "]


log = logging.getLogger(__name__)
bot = commands.Bot(command_prefix=get_prefix)
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
                    try:
                        t.size = await render.calculate_size(await http.get_template(t.url, t.name))
                        sql.template_update(t)
                    except TemplateHttpError:
                        log.error("Error retrieving template {0.name}. Skipping...".format(t))

    log.info("Loading cogs...")
    cogs = [
        Animotes(bot),
        Canvas(bot),
        Configuration(bot),
        Faction(bot),
        General(bot),
        Template(bot),
    ]
    for c in cogs:
        try:
            bot.add_cog(c)
        except Exception as e:
            log.error("Failed to load a cog: {}\n{}: {}".format(c, type(e).__name__, e))

    log.info("Performing guilds check...")
    for g in bot.guilds:
        log.info("'{0.name}' (ID: {0.id})".format(g))
        db_g = sql.guild_get_by_id(g.id)
        if db_g:
            prefix = db_g.prefix if db_g.prefix else config.PREFIX
            if g.name != db_g.name:
                if config.CHANNEL_LOG_GUILD_RENAMES:
                    await utils.channel_log(bot, "Guild **{1}** is now known as **{0.name}** `(ID:{0.id})`".format(g, db_g.name))
                sql.guild_update(g.id, name=g.name)
            if is_new_version:
                ch = next((x for x in g.channels if x.id == db_g.alert_channel), None)
                if ch:
                    data = await http.get_changelog(VERSION)
                    if data:
                        e = discord.Embed(title=data['name'], url=data['url'], color=13594340,
                                          description=data['body']) \
                            .set_author(name=data['author']['login']) \
                            .set_thumbnail(url=data['author']['avatar_url']) \
                            .set_footer(text="Released " + data['published_at'])
                        await ch.send(GlimContext.get_from_guild(g, "bot.update").format(VERSION, prefix), embed=e)
                    else:
                        await ch.send(GlimContext.get_from_guild(g, "bot.update_no_changelog").format(VERSION, prefix))
                    log.info("- Sent update message")
                else:
                    log.info("- Could not send update message: alert channel not found.")
        else:
            j = g.me.joined_at
            if config.CHANNEL_LOG_GUILD_JOINS:
                await utils.channel_log(bot, "Joined guild **{0.name}** (ID: `{0.id}`)".format(g, j.isoformat(' ')))
            log.info("Joined guild '{0.name}' (ID: {0.id}) between sessions at {1}".format(g, j.timestamp()))
            sql.guild_add(g.id, g.name, int(j.timestamp()))
            await print_welcome_message(g)

    db_guilds = sql.guild_get_all()
    if len(bot.guilds) != len(db_guilds):
        for g in db_guilds:
            if not any(x for x in bot.guilds if x.id == g.id):
                log.info("Kicked from guild '{0}' (ID: {1}) between sessions".format(g.name, g.id))
                if config.CHANNEL_LOG_GUILD_KICKS:
                    await utils.channel_log(bot, "Kicked from guild **{0}** (ID: `{1}`)".format(g.name, g.id))
                sql.guild_delete(g.id)

    log.info('I am ready!')
    await utils.channel_log(bot, "I am ready!")
    print("I am ready!")


@bot.event
async def on_guild_join(guild):
    log.info("Joined new guild '{0.name}' (ID: {0.id})".format(guild))
    if config.CHANNEL_LOG_GUILD_JOINS:
        await utils.channel_log(bot, "Joined new guild **{0.name}** (ID: `{0.id}`)".format(guild))
    sql.guild_add(guild.id, guild.name, int(guild.me.joined_at.timestamp()))
    await print_welcome_message(guild)


@bot.event
async def on_guild_remove(guild):
    log.info("Kicked from guild '{0.name}' (ID: {0.id})".format(guild))
    if config.CHANNEL_LOG_GUILD_KICKS:
        await utils.channel_log(bot, "Kicked from guild **{0.name}** (ID: `{0.id}`)".format(guild))
    sql.guild_delete(guild.id)


@bot.event
async def on_guild_update(before, after):
    if before.name != after.name:
        log.info("Guild {0.name} is now known as {1.name} (ID: {1.id})")
        if config.CHANNEL_LOG_GUILD_RENAMES:
            await utils.channel_log(bot, "Guild **{0.name}** is now known as **{1.name}** (ID: `{1.id}`)".format(before, after))
        sql.guild_update(after.id, name=after.name)


@bot.event
async def on_guild_role_delete(role):
    sql.guild_delete_role(role.id)


@bot.before_invoke
async def on_command_preprocess(ctx):
    invocation_type = "A" if ctx.is_autoscan else "I"
    if ctx.is_default:
        invocation_type += "D"
    if ctx.is_template:
        invocation_type += "T"
    if ctx.is_repeat:
        invocation_type += "R"
    if ctx.guild:
        log.info("[{0}] {1.name}#{1.discriminator} used '{2}' in {3.name} (UID:{1.id} GID:{3.id})"
                  .format(invocation_type, ctx.author, ctx.command.qualified_name, ctx.guild))
    else:
        log.info("[{0}] {1.name}#{1.discriminator} used '{2}' in DM (UID:{1.id})"
                  .format(invocation_type, ctx.author, ctx.command.qualified_name, ctx.guild))
    log.info(ctx.message.content)


@bot.event
async def on_command_error(ctx, error):
    # Command errors
    if isinstance(error, commands.BadArgument):
        pass
    elif isinstance(error, commands.CommandInvokeError) \
            and isinstance(error.original, discord.HTTPException) \
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
    elif isinstance(error, BadArgumentErrorWithMessage):
        await ctx.send(error.message)
    elif isinstance(error, FactionNotFoundError):
        await ctx.send(ctx.s("error.faction_not_found"))
    elif isinstance(error, IdempotentActionError):
        try:
            f = discord.File("assets/y_tho.png", "y_tho.png")
            await ctx.send(ctx.s("error.why"), file=f)
        except IOError:
            await ctx.send(ctx.s("error.why"))
    elif isinstance(error, NoAttachmentError):
        await ctx.send(ctx.s("error.no_attachment"))
    elif isinstance(error, NoJpegsError):
        try:
            f = discord.File("assets/disdain_for_jpegs.gif", "disdain_for_jpegs.gif")
            await ctx.send(ctx.s("error.jpeg"), file=f)
        except IOError:
            await ctx.send(ctx.s("error.jpeg"))
    elif isinstance(error, NoSelfPermissionError):
        await ctx.send(ctx.s("error.no_self_permission"))
    elif isinstance(error, NoTemplatesError):
        if error.is_canvas_specific:
            await ctx.send(ctx.s("error.no_templates_for_canvas"))
        else:
            await ctx.send(ctx.s("error.no_templates"))
    elif isinstance(error, NoUserPermissionError):
        await ctx.send(ctx.s("error.no_user_permission"))
    elif isinstance(error, NotPngError):
        await ctx.send(ctx.s("error.not_png"))
    elif isinstance(error, PilImageError):
        await ctx.send(ctx.s("error.bad_image"))
    elif isinstance(error, TemplateHttpError):
        await ctx.send(ctx.s("error.cannot_fetch_template").format(error.template_name))
    elif isinstance(error, TemplateNotFoundError):
        await ctx.send(ctx.s("error.template_not_found"))
    elif isinstance(error, UrlError):
        await ctx.send(ctx.s("error.non_discord_url"))
    elif isinstance(error, HttpCanvasError):
        await ctx.send(ctx.s("error.http_canvas").format(canvases.pretty_print[error.canvas]))
    elif isinstance(error, HttpGeneralError):
        await ctx.send(ctx.s("error.http"))

    # Uncaught error
    else:
        name = ctx.command.qualified_name if ctx.command else "None"
        await utils.channel_log(bot,
            "An error occurred executing `{0}` in server **{1.name}** (ID: `{1.id}`):".format(name, ctx.guild))
        await utils.channel_log(bot, "```{}```".format(error))
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
    channels = (x for x in guild.channels if x.permissions_for(guild.me).send_messages and type(x) is TextChannel)
    c = next((x for x in channels if x.name == "general"), next(channels, None))
    if c:
        await c.send("Hi! I'm {0}. For a full list of commands, pull up my help page with `{1}help`. "
                     "Happy pixel painting!".format(config.NAME, config.PREFIX))
        log.info(" - Printed welcome message".format(guild))
    else:
        log.info("- Could not print welcome message: no default channel found".format(guild))


bot.run(config.TOKEN)
