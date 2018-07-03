from discord.ext import commands
from discord.utils import get as dget

from lang import en_US, pt_BR
from utils import canvases, sqlite as sql


class GlimContext(commands.Context):
    def __init__(self, **attrs):
        super().__init__(**attrs)
        self.is_repeat = False
        self.is_autoscan = False
        self.is_default = False
        self.is_template = False

    langs = {
        'en-us': "English (US)",
        'pt-br': "Português (BR)"
    }

    @property
    def canvas(self):
        return sql.guild_get_canvas_by_id(self.guild.id)

    @property
    def canvas_pretty(self):
        return canvases.pretty_print[self.canvas]

    @property
    def lang(self):
        return sql.guild_get_language_by_id(self.guild.id)

    @staticmethod
    def get_from_guild(guild, str_id):
        language = sql.guild_get_language_by_id(guild.id).lower()
        if language == "en-us":
            return en_US.STRINGS.get(str_id, None)
        if language == "pt-br":
            return en_US.STRINGS.get(str_id, None)

    def s(self, str_id):
        language = sql.guild_get_language_by_id(self.guild.id).lower()
        if language == "en-us":
            return en_US.STRINGS.get(str_id, None)
        if language == "pt-br":
            return pt_BR.STRINGS.get(str_id, None)

    async def invoke_default(self, cmd: str):
        default_canvas = self.canvas
        cmds = cmd.split('.')
        self.command = dget(self.bot.commands, name=cmds[0])
        self.view.index = 0
        self.view.preview = 0
        self.view.get_word()
        if len(cmds) > 1:
            for c in cmds[1:]:
                self.command = dget(self.command.commands, name=c)
                self.view.skip_ws()
                self.view.get_word()
        self.command = dget(self.command.commands, name=default_canvas)
        self.is_default = True
        if self.command is not None:
            await self.bot.invoke(self)
