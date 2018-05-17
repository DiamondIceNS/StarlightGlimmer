import utils.sqlite
from lang import en_US, pt_BR

langs = {
    'en-us': "English (US)",
    'pt-br': "Português (BR)"
}


def getlang(guild_id, str_id):
    language = utils.sqlite.get_guild_language(guild_id).lower()

    if language == "en-us":
        return en_US.STRINGS[str_id]
    if language == "pt-br":
        return pt_BR.STRINGS[str_id]

