from discord.ext import commands

from objects import errors
from utils import utils


def admin_only():
    def predicate(ctx):
        if not ctx.guild:
            return True
        if utils.is_admin(ctx):
            return True
        else:
            raise errors.NoUserPermissionError
    return commands.check(predicate)


def template_admin_only():
    def predicate(ctx):
        if not ctx.guild:
            return True
        if utils.is_template_admin(ctx) or utils.is_admin(ctx):
            return True
        else:
            raise errors.NoUserPermissionError
    return commands.check(predicate)


def template_adder_only():
    def predicate(ctx):
        if not ctx.guild:
            return True
        if utils.is_template_adder(ctx) or utils.is_template_admin(ctx) or utils.is_admin(ctx):
            return True
        else:
            raise errors.NoUserPermissionError
    return commands.check(predicate)
