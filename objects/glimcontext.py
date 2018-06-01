from discord.ext import commands
from discord.utils import get as dget
from utils import canvases, sqlite as sql
from lang import en_US, pt_BR


langs = {
    'en-us': "English (US)",
    'pt-br': "Português (BR)"
}


class GlimContext(commands.Context):
    def __init__(self, **attrs):
        super().__init__(**attrs)
        self.is_repeat = False
        self.is_autoscan = False
        self.is_default = False
        self.is_template = False

    @property
    def canvas(self):
        return sql.select_guild_by_id(self.guild.id)['default_canvas']

    @property
    def canvas_pretty(self):
        return canvases.pretty_print(self.canvas)

    @property
    def lang(self):
        return sql.get_guild_language(self.guild.id)

    @staticmethod
    def get_str_from_guild(guild, str_id):
        language = sql.get_guild_language(guild.id).lower()
        if language == "en-us":
            return en_US.STRINGS[str_id]
        if language == "pt-br":
            return en_US.STRINGS[str_id]

    def get_str(self, str_id):
        language = sql.get_guild_language(self.guild.id).lower()

        if language == "en-us":
            return en_US.STRINGS[str_id]
        if language == "pt-br":
            return pt_BR.STRINGS[str_id]

    async def invoke_default(self, cmd: str):
        default_canvas = self.canvas
        cmds = cmd.split('.')
        self.command = dget(self.bot.commands, name=cmds[0])
        if len(cmds) > 1:
            self.view.index = 0
            self.view.preview = 0
            self.view.get_word()
            for c in cmds[1:]:
                self.command = dget(self.command.commands, name=c)
                self.view.skip_ws()
                self.view.get_word()
        self.command = dget(self.command.commands, name=default_canvas)
        self.is_default = True
        if self.command is not None:
            await self.bot.invoke(self)
