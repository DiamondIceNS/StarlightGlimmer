from discord.ext import commands
from utils import sqlite as sql
from lang import en_US, pt_BR


langs = {
    'en-us': "English (US)",
    'pt-br': "Português (BR)"
}


class GlimContext(commands.Context):
    def getlang(self, str_id):
        language = sql.get_guild_language(self.guild.id).lower()

        if language == "en-us":
            return en_US.STRINGS[str_id]
        if language == "pt-br":
            return pt_BR.STRINGS[str_id]
