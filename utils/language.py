import utils.sqlite
import lang.en_US


def getlang(guild_id, str_id):
    language = utils.sqlite.get_guild_language(guild_id)

    if language == "en_US":
        return lang.en_US.STRINGS[str_id]


