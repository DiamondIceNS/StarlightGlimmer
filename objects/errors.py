from discord.ext import commands


class BadArgumentErrorWithMessage(commands.CommandError):
    def __init__(self, message):
        self.message = message


class FactionNotFoundError(commands.CommandError):
    pass


class HttpGeneralError(commands.CommandError):
    pass


class HttpCanvasError(commands.CommandError):
    def __init__(self, canvas):
        self.canvas = canvas


class IdempotentActionError(commands.CommandError):
    pass


class NoAttachmentError(commands.CommandError):
    pass


class NoSelfPermissionError(commands.CommandError):
    pass


class NoTemplatesError(commands.CommandError):
    def __init__(self, is_canvas_specific=False):
        self.is_canvas_specific = is_canvas_specific


class NoUserPermissionError(commands.CommandError):
    pass


class NoJpegsError(commands.CommandError):
    pass


class NotPngError(commands.CommandError):
    pass


class PilImageError(commands.CommandError):
    pass


class TemplateHttpError(commands.CommandError):
    def __init__(self, template_name):
        self.template_name = template_name


class TemplateNotFoundError(commands.CommandError):
    pass


class UrlError(commands.CommandError):
    pass
