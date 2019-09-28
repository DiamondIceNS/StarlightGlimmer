import asyncio
import logging
import re
import time

import discord
from discord.ext.commands.view import StringView
from discord.utils import get as dget

from objects.errors import NoAttachmentError, NoJpegsError, NotPngError
from utils import config, sqlite as sql

log = logging.getLogger(__name__)


async def autoscan(ctx):
    if ctx.guild and not sql.guild_is_autoscan(ctx.guild.id):
        return

    canvas = sql.guild_get_canvas_by_id(ctx.guild.id) if ctx.guild else "pixelcanvas"

    cmd = None
    view = ""
    m_pc = re.search('pixelcanvas\.io/@(-?\d+),(-?\d+)(?:(?: |#| #)(-?\d+))?', ctx.message.content)
    m_pz = re.search('pixelzone\.io/\?p=(-?\d+),(-?\d+)(?:,(\d+))?(?:(?: |#| #)(-?\d+))?', ctx.message.content)
    m_ps = re.search('pxls\.space/#x=(\d+)&y=(\d+)(?:&scale=(\d+))?(?:(?: |#| #)(-?\d+))?', ctx.message.content)
    m_pre_def = re.search('@(-?\d+)(?: |,|, )(-?\d+)(?:(?: |#| #)(-?\d+))?', ctx.message.content)
    m_dif_def = re.search('(?:(-l) )?(-?\d+)(?: |,|, )(-?\d+)(?:(?: |#| #)(-?\d+))?', ctx.message.content)
    if m_pc:
        cmd = dget(dget(ctx.bot.commands, name='preview').commands, name='pixelcanvas')
        view = ' '.join(m_pc.groups(default='1'))
    elif m_pz:
        cmd = dget(dget(ctx.bot.commands, name='preview').commands, name='pixelzone')
        view = '{} {} {}'.format(m_pz.group(1), m_pz.group(2), m_pz.group(4) or m_pz.group(3) or '1')
    elif m_ps:
        cmd = dget(dget(ctx.bot.commands, name='preview').commands, name='pxlsspace')
        view = '{} {} {}'.format(m_ps.group(1), m_ps.group(2), m_ps.group(4) or m_ps.group(3) or '1')
    elif m_pre_def:
        cmd = dget(dget(ctx.bot.commands, name='preview').commands, name=canvas)
        view = ' '.join(m_pre_def.groups(default='1'))
    elif m_dif_def and len(ctx.message.attachments) > 0 and ctx.message.attachments[0].filename[-4:].lower() == ".png":
        cmd = dget(dget(ctx.bot.commands, name='diff').commands, name=canvas)
        view = '{} {} {} {}'.format(m_dif_def.group(1) or "", m_dif_def.group(2), m_dif_def.group(3),
                                    m_dif_def.group(4) or 1)

    if cmd:
        ctx.command = cmd
        ctx.view = StringView(view)
        ctx.is_autoscan = True
        await ctx.bot.invoke(ctx)
        return True


async def channel_log(bot, msg):
    if config.LOGGING_CHANNEL_ID:
        channel = bot.get_channel(config.LOGGING_CHANNEL_ID)
        if not channel:
            log.warning("Can't find logging channel")
        else:
            try:
                await channel.send("`{}` {}".format(time.strftime('%H:%M:%S', time.localtime()), msg))
            except discord.errors.Forbidden:
                log.warning("Forbidden from logging channel!")


def get_botadmin_role(ctx):
    role_id = sql.guild_get_by_id(ctx.guild.id).bot_admin
    r = dget(ctx.guild.roles, id=role_id)
    if role_id and not r:
        sql.guild_update(ctx.guild.id, bot_admin=None)
        return None
    return r


def get_templateadmin_role(ctx):
    role_id = sql.guild_get_by_id(ctx.guild.id).template_admin
    r = dget(ctx.guild.roles, id=role_id)
    if role_id and not r:
        sql.guild_update(ctx.guild.id, template_admin=None)
        return None
    return r


def get_templateadder_role(ctx):
    role_id = sql.guild_get_by_id(ctx.guild.id).template_adder
    r = dget(ctx.guild.roles, id=role_id)
    if role_id and not r:
        sql.guild_update(ctx.guild.id, template_adder=None)
        return None
    return r


def is_admin(ctx):
    role_id = sql.guild_get_by_id(ctx.guild.id).bot_admin
    r = dget(ctx.author.roles, id=role_id)
    return bool(r) or ctx.author.permissions_in(ctx.channel).administrator


def is_template_admin(ctx):
    role_id = sql.guild_get_by_id(ctx.guild.id).template_admin
    r = dget(ctx.author.roles, id=role_id)
    return bool(r)


def is_template_adder(ctx):
    role_id = sql.guild_get_by_id(ctx.guild.id).template_adder
    r = dget(ctx.author.roles, id=role_id)
    return bool(not role_id or r)


async def verify_attachment(ctx):
    if len(ctx.message.attachments) < 1:
        raise NoAttachmentError
    att = ctx.message.attachments[0]
    if att.filename[-4:].lower() != ".png":
        if att.filename[-4:].lower() == ".jpg" or att.filename[-5:].lower() == ".jpeg":
            raise NoJpegsError
        raise NotPngError
    return att


async def yes_no(ctx, question):
    sql.menu_locks_add(ctx.channel.id, ctx.author.id)
    query_msg = await ctx.send("{}\n  `0` - {}\n  `1` - {}".format(question, ctx.s("bot.no"), ctx.s("bot.yes")))

    def check(m):
        return ctx.channel.id == m.channel.id and ctx.author.id == m.author.id

    try:
        resp_msg = await ctx.bot.wait_for('message', timeout=60.0, check=check)
        while not (resp_msg.content == "0" or resp_msg.content == "1"):
            await ctx.send(ctx.s("error.invalid_option"))
            resp_msg = await ctx.bot.wait_for('message', timeout=60.0, check=check)
    except asyncio.TimeoutError:
        await query_msg.edit(content=ctx.s("error.timed_out"))
        return False
    finally:
        sql.menu_locks_delete(ctx.channel.id, ctx.author.id)
    return resp_msg.content == "1"
