import aiohttp
import asyncio
import discord
import io
import re
from discord.utils import get as dget

from utils import checks, sqlite as sql


async def autoscan(ctx):
    if sql.select_guild_by_id(ctx.guild.id)['autoscan'] == 1:
        default_canvas = sql.select_guild_by_id(ctx.guild.id)['default_canvas']

        cmd = None
        if re.search('pixelcanvas\.io/@-?\d+,-?\d+', ctx.message.content) is not None:
            cmd = dget(dget(ctx.bot.commands, name='preview').commands, name='pixelcanvas')
        elif re.search('pixelz\.io/@-?\d+,-?\d+', ctx.message.content) is not None:
            cmd = dget(dget(ctx.bot.commands, name='preview').commands, name='pixelzio')
        elif re.search('pixelzone\.io/\?p=-?\d+,-?\d+', ctx.message.content) is not None:
            cmd = dget(dget(ctx.bot.commands, name='preview').commands, name='pixelzone')
        elif re.search('pxls\.space/#x=\d+&y=\d+', ctx.message.content) is not None:
            cmd = dget(dget(ctx.bot.commands, name='preview').commands, name='pxlsspace')
        elif re.search('@\(?-?\d+, ?-?\d+\)?', ctx.message.content) is not None:
            cmd = dget(dget(ctx.bot.commands, name='preview').commands, name=default_canvas)
        elif re.search('\(?-?\d+, ?-?\d+\)?', ctx.message.content) is not None and len(ctx.message.attachments) > 0 \
                and ctx.message.attachments[0].filename[-4:].lower() == ".png":
            cmd = dget(dget(ctx.bot.commands, name='diff').commands, name=default_canvas)

        if cmd:
            ctx.command = cmd
            ctx.is_autoscan = True
            await ctx.bot.invoke(ctx)
            return True


async def get_template(url):
    async with aiohttp.ClientSession() as sess:
        async with sess.get(url) as resp:
            if resp.status != 200:
                raise checks.TemplateHttpError
            if resp.content_type == "image/jpg" or resp.content_type == "image/jpeg":
                raise checks.NoJpegsError
            if resp.content_type != "image/png":
                raise checks.NotPngError
            return io.BytesIO(await resp.read())


def get_templateadmin_role(ctx):
    role_id = sql.select_guild_by_id(ctx.guild.id)['template_admin_role']
    r = dget(ctx.guild.roles, id=role_id)
    if role_id and not r:
        sql.clear_template_admin_role(ctx.guild.id)
        return None
    return r


def get_templateadder_role(ctx):
    role_id = sql.select_guild_by_id(ctx.guild.id)['template_adder_role']
    r = dget(ctx.guild.roles, id=role_id)
    if role_id and not r:
        sql.clear_template_adder_role(ctx.guild.id)
        return None
    return r


def is_admin(ctx):
    return ctx.author.permissions_in(ctx.channel).administrator


def is_template_admin(ctx):
    role_id = sql.select_guild_by_id(ctx.guild.id)['template_admin_role']
    r = dget(ctx.author.roles, id=role_id)
    return bool(r)


def is_template_adder(ctx):
    role_id = sql.select_guild_by_id(ctx.guild.id)['template_adder_role']
    r = dget(ctx.author.roles, id=role_id)
    return bool(not role_id or r)


async def verify_attachment(ctx):
    if len(ctx.message.attachments) < 1:
        await ctx.send(ctx.get_str("bot.error.missing_attachment"))
        return
    att = ctx.message.attachments[0]
    if att.filename[-4:].lower() != ".png":
        if att.filename[-4:].lower() == ".jpg" or att.filename[-5:].lower() == ".jpeg":
            try:
                f = discord.File("assets/disdain_for_jpegs.gif", "disdain_for_jpegs.gif")
                await ctx.send(ctx.get_str("bot.error.jpeg"), file=f)
            except IOError:
                await ctx.send(ctx.get_str("bot.error.jpeg"))
            return
        await ctx.send(ctx.get_str("bot.error.no_png"))
        return
    return att


async def yes_no(ctx, question):
    sql.add_menu_lock(ctx.channel.id, ctx.author.id)
    query_msg = await ctx.send(question + ctx.get_str("bot.yes_no"))

    def check(m):
        return ctx.channel.id == m.channel.id and ctx.author.id == m.author.id

    try:
        resp_msg = await ctx.bot.wait_for('message', timeout=60.0, check=check)
        while not (resp_msg.content == "0" or resp_msg.content == "1"):
            await ctx.send(ctx.get_str("bot.yes_no_invalid"))
            resp_msg = await ctx.bot.wait_for('message', timeout=60.0, check=check)
    except asyncio.TimeoutError:
        await query_msg.edit(content=ctx.get_str("bot.yes_no_timed_out"))
        return False
    finally:
        sql.remove_menu_lock(ctx.channel.id, ctx.author.id)
    return resp_msg.content == "1"
