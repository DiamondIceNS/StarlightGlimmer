from discord.ext import commands
from utils import utils


class HttpPayloadError(commands.CommandError):
    def __init__(self, canvas):
        self.canvas = canvas


class IdempotentActionError(commands.CommandError):
    pass


class NoPermissionError(commands.CommandError):
    pass


class NoJpegsError(commands.CommandError):
    pass


class NotPngError(commands.CommandError):
    pass


class PilImageError(commands.CommandError):
    pass


class TemplateHttpError(commands.CommandError):
    pass


class UrlError(commands.CommandError):
    pass


def admin_only():
    def predicate(ctx):
        if not ctx.guild:
            return True
        if utils.is_admin(ctx):
            return True
        else:
            raise NoPermissionError
    return commands.check(predicate)


def template_admin_only():
    def predicate(ctx):
        if not ctx.guild:
            return True
        if utils.is_template_admin(ctx) or utils.is_admin(ctx):
            return True
        else:
            raise NoPermissionError
    return commands.check(predicate)


def template_adder_only():
    def predicate(ctx):
        if not ctx.guild:
            return True
        if utils.is_template_adder(ctx) or utils.is_template_admin(ctx) or utils.is_admin(ctx):
            return True
        else:
            raise NoPermissionError
    return commands.check(predicate)
