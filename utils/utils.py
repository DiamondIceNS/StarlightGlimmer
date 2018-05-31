from utils import sqlite as sql
from utils import checks
from discord.utils import get as dget
import discord
import aiohttp
import asyncio
import io


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
        await ctx.send(ctx.getlang("bot.error.missing_attachment"))
        return
    att = ctx.message.attachments[0]
    if att.filename[-4:].lower() != ".png":
        if att.filename[-4:].lower() == ".jpg" or att.filename[-5:].lower() == ".jpeg":
            try:
                f = discord.File("assets/disdain_for_jpegs.gif", "disdain_for_jpegs.gif")
                await ctx.send(ctx.getlang("bot.error.jpeg"), file=f)
            except IOError:
                await ctx.send(ctx.getlang("bot.error.jpeg"))
            return
        await ctx.send(ctx.getlang("bot.error.no_png"))
        return
    return att


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


async def yes_no(ctx, question):
    sql.add_menu_lock(ctx.channel.id, ctx.author.id)
    query_msg = await ctx.send(question + "\n  `0` - No\n  `1` - Yes")  # TODO: Localize string

    def check(m):
        return ctx.channel.id == m.channel.id and ctx.author.id == m.author.id

    try:
        resp_msg = await ctx.bot.wait_for('message', timeout=60.0, check=check)
        while not (resp_msg.content == "0" or resp_msg.content == "1"):
            await ctx.send("That is not a valid option. Please try again.")  # TODO: localize string
            resp_msg = await ctx.bot.wait_for('message', timeout=60.0, check=check)
    except asyncio.TimeoutError:
        await query_msg.edit(content="Command timed out.")  # TODO: localize string
        return False
    finally:
        sql.remove_menu_lock(ctx.channel.id, ctx.author.id)
    return resp_msg.content == "1"
