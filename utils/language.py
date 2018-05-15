import utils.sqlite
from lang import en_US, pt_BR


def getlang(guild_id, str_id):
    language = utils.sqlite.get_guild_language(guild_id)

    if language == "en-US":
        return en_US.STRINGS[str_id]
    if language == "pt-BR":
        return pt_BR.STRINGS[str_id]

