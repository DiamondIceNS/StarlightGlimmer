from utils import sqlite as sql
from discord.utils import get as dget


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
