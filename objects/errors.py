from discord.ext import commands


class HttpPayloadError(commands.CommandError):
    def __init__(self, canvas):
        self.canvas = canvas


class IdempotentActionError(commands.CommandError):
    pass


class NoAttachmentError(commands.CommandError):
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
