class DbGuild:
    def __init__(self, guild_id, name, join_date, prefix, alert_channel, autoscan, canvas, language, template_admin,
                 template_adder, bot_admin, faction_name, faction_alias, faction_color, faction_desc, faction_emblem,
                 faction_invite):
        self.id = guild_id
        self.name = name
        self.join_date = join_date
        self.prefix = prefix
        self.alert_channel = alert_channel
        self.autoscan = autoscan
        self.canvas = canvas
        self.language = language
        self.template_admin = template_admin
        self.template_adder = template_adder
        self.bot_admin = bot_admin
        self.faction_name = faction_name
        self.faction_alias = faction_alias
        self.faction_color = faction_color
        self.faction_desc = faction_desc
        self.faction_emblem = faction_emblem
        self.faction_invite = faction_invite
