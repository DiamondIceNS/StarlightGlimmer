STRINGS = {
    # Global messages
    "bot.added_by": "Added By",
    "bot.alias": "Alias",  # TODO: Translate
    "bot.canvas": "Canvas",
    "bot.canvases": "Canvases",  # TODO: Translate
    "bot.coordinates": "Coordinates",
    "bot.date_added": "Date Added",
    "bot.date_modified": "Date Modified",
    "bot.dimensions": "Dimensions",  # TODO: Translate
    "bot.errors": "Errors",  # TODO: Translate
    "bot.faction": "Faction",  # TODO: Translate
    "bot.name": "Name",
    "bot.no": "No",
    "bot.page": "Page",  # TODO: Translate
    "bot.percent": "Percent",  # TODO: Translate
    "bot.size": "Size",
    "bot.total": "Total",  # TODO: Translate
    "bot.visibility": "Visibility",  # TODO: Translate
    "bot.yes": "Yes",

    # Error messages
    "error.bad_png": "This image seems to be corrupted. Try re-saving it with an image editor or using `{0}quantize`.",
    "error.cooldown": "That command is on cooldown. Try again in {0:.01f}s.",
    "error.non_discord_url": "I can only accept Discord attachment URLs.",
    "error.http": "{0} seems to be having connection issues. Try again later.",
    "error.why": "But... why?",
    "error.invalid_color": "That is not a valid color.",  # TODO: Translate
    "error.jpeg": "Seriously? A JPEG? Gross! Please create a PNG template instead.",
    "error.no_attachment": "That command requires an attachment.",
    "error.no_permission": "You do not have permission to use that command.",
    "error.not_png": "That command requires a PNG image.",
    "error.no_dm": "That command only works in guilds.",
    "error.bad_image": "An error occurred while attempting to open an image. Ensure that the supplied image is not corrupted.",
    "error.cannot_fetch_template": "Could not access template URL. (Was the original attachment deleted?)",
    "error.unknown": "An unknown error occurred. The dev has been notified.",
    "error.invalid_option": "That is not a valid option. Please try again.",
    "error.timed_out": "Command timed out.",

    # Animotes command messages
    "animotes.opt_in": "You have successfully **opted-in** to emoji conversion.",
    "animotes.opt_out": "You have successfully **opted-out** of emoji conversion.",

    # Canvas command messages
    "canvas.diff": "{0}/{1} | {2} errors | {3} complete",
    "canvas.diff_bad_color": "{0}/{1} | {2} errors | {bad} bad color | {3} complete",
    "canvas.invalid_input": "Invalid input: does not match any template name or supported coordinates format.",
    "canvas.large_template": "(Processing large template, this might take a few seconds...)",
    "canvas.quantize": "Fixed {0} pixels.",
    "canvas.repeat_not_found": "Could not find a valid command to repeat.",

    # Configuration command messages
    "configuration.alert_channel_cleared": "Alert channel has been cleared.",
    "configuration.alert_channel_set": "Alert channel has been set to {0}.",
    "configuration.autoscan_disabled": "Autoscan has been disabled.",
    "configuration.autoscan_enabled": "Autoscan has been enabled.",
    "configuration.canvas_check": "This guild's default canvas is **{0}**.\n"
                                  "To change the default canvas, run this command again with a supported canvas. (Use `{1}help canvas` to see a list.)",
    "configuration.canvas_set": "Default canvas has been set to **{0}**.",
    "configuration.language_check": "This guild's current language is **{1}**.\n"
                                   "To set a new language, run this command again with one of the following options:\n"
                                   "```{0}```",
    "configuration.language_set": "Language has been set to **English (US)**.",
    "configuration.prefix_set": "Prefix for this guild has been set to **{0}**.",
    "configuration.role_list": "**Roles List**\n```xl\n"
                               "'botadmin'      - Can do anything an Administrator can do\n"
                               "'templateadder' - Can add templates, and remove templates they added themself\n"
                               "'templateadmin' - Can add and remove any template\n"
                               "\n// Use '{0}role <type>' to view the current linked role.\n```",
    "configuration.role_not_found": "That role could not be found.",
    "configuration.role_bot_admin_check": "Bot admin privileges are currently assigned to `@{0}`.",
    "configuration.role_bot_admin_cleared": "Bot admin privileges successfully cleared.",
    "configuration.role_bot_admin_not_set": "Bot admin privileges have not been assigned to a role.",
    "configuration.role_bot_admin_set": "Bot admin privileges assigned to role `@{0}`.",
    "configuration.role_template_adder_check": "Template adder privileges are currently assigned to `@{0}`.",
    "configuration.role_template_adder_cleared": "Template adder privileges successfully cleared.",
    "configuration.role_template_adder_not_set": "Template adder privileges have not been assigned to a role.",
    "configuration.role_template_adder_set": "Template adder privileges assigned to role `@{0}`.",
    "configuration.role_template_admin_check": "Template admin privileges are currently assigned to `@{0}`.",
    "configuration.role_template_admin_cleared": "Template admin privileges successfully cleared.",
    "configuration.role_template_admin_not_set": "Template admin privileges have not been assigned to a role.",
    "configuration.role_template_admin_set": "Template admin privileges assigned to role `@{0}`.",
    "bot.update": "I have updated to version **{0}**! Visit https://github.com/DiamondIceNS/StarlightGlimmer/releases for the full changelog.",

    # Faction command messages
    "faction.alias_already_exists": "A faction with that alias already exists.",  # TODO: Translate
    "faction.already_hidden": "That faction is already hidden.",  # TODO: Translate
    "faction.already_faction": "This guild is already a faction.",  # TODO: Translate
    "faction.clear_alias": "Faction alias cleared.",  # TODO: Translate
    "faction.clear_hide": "Unhid faction `{}`.",  # TODO: Translate
    "faction.clear_color": "Faction color cleared.",  # TODO: Translate
    "faction.clear_description": "Faction description cleared.",  # TODO: Translate
    "faction.clear_emblem": "Faction emblem cleared.",  # TODO: Translate
    "faction.clear_invite": "Faction invite cleared.",  # TODO: Translate
    "faction.clear_invite_cannot_delete": "Faction invite cleared, but I don't have permission to completely delete it.",  # TODO: Translate
    "faction.created": "Faction `{}` created.",  # TODO: Translate
    "faction.disbanded": "Faction successfully disbanded.",  # TODO: Translate
    "faction.faction_list_footer_1": "// Use '{0}faction <page>' to see that page",  # TODO: Translate
    "faction.faction_list_footer_2": "// Use '{0}faction info <name>' to see more info on a faction",  # TODO: Translate
    "faction.list_header": "Faction List",  # TODO: Translate
    "faction.must_be_a_faction": "This guild needs to become a faction to use that command.",  # TODO: Translate
    "faction.name_already_exists": "A faction with that name already exists.",  # TODO: Translate
    "faction.no_factions": "There doesn't seem to be any guilds yet...",  # TODO: Translate
    "faction.not_a_faction_yet": "This guild has not created a faction yet.",  # TODO: Translate
    "faction.not_found": "That faction could not be found.",  # TODO: Translate
    "faction.set_alias": "Faction alias set to `{}`.",  # TODO: Translate
    "faction.set_hide": "Hid faction `{}`.",  # TODO: Translate
    "faction.set_color": "Faction color set.",  # TODO: Translate
    "faction.set_description": "Faction description set.",  # TODO: Translate
    "faction.set_emblem": "Faction emblem set.",  # TODO: Translate
    "faction.set_invite": "Faction invite set.",  # TODO: Translate
    "faction.set_name": "Faction renamed to `{}`.",  # TODO: Translate

    # General command messages
    "bot.help_ending_note": "Type '{0}{1} <command>' for more info on a command.",
    "bot.ping": "Pinging...",
    "bot.pong": "Pong! | **{0}ms**",
    "bot.suggest": "Your suggestion has been sent. Thank you for your input!",
    "bot.version": "My version number is **{0}**",

    # Template command messages
    "template.added": "Template '{0}' added!",
    "template.calculating": "Calculating...",  # TODO: Translate
    "template.duplicate_list_open": "The following templates already match this image:\n```xl\n",  
    "template.duplicate_list_close": "```\nCreate a new template anyway?",
    "template.fetching_data": "Fetching data from {}...",  # TODO: Translate
    "template.list_all_footer_1": "// Use '{0}template all <page>' to see that page",  # TODO: Translate
    "template.list_all_footer_2": "// Use '{0}template info -f <faction> <name>' to see more info on a template",  # TODO: Translate
    "template.list_header": "Template List",  # TODO: Translate
    "template.list_footer_1": "// Use '{0}template <page>' to see that page",  # TODO: Translate
    "template.list_footer_2": "// Use '{0}template info <name>' to see more info on a template",  # TODO: Translate
    "template.list_no_templates": "This guild currently has no templates.",
    "template.max_templates": "This guild already has the maximum number of templates. Please remove a template before adding another.",  
    "template.name_exists_ask_replace": "A template with the name '{0}' already exists for {1} at ({2}, {3}). Replace it?",  
    "template.name_exists_no_permission": "A template with that name already exists. Please choose a different name.",  
    "template.name_not_found": "Could not find template with name `{0}`.",  
    "template.name_too_long": "That name is too long. Please use a name under {0} characters.",  
    "template.no_template_named": "There is no template named '{0}'.",  
    "template.not_owner": "You do not have permission to modify that template.",  
    "template.not_quantized": "This image contains colors that are not part of this canvas's palette. Would you like to quantize it?",  
    "template.remove": "Successfully removed '{0}'.",
    "template.template_report_header": "Template Report",  # TODO: Translate
    "template.updated": "Template '{0}' updated!",

    # Command brief help
    "brief.alertchannel": "Set or clear the channel used for update alerts.",
    "brief.alertchannel.clear": "Clears the alert channel.",
    "brief.alertchannel.set": "Sets the alert channel.",
    "brief.autoscan": "Toggles automatic preview and diff.",
    "brief.canvas": "Sets the default canvas website for this guild.",
    "brief.canvas.pixelcanvas": "Sets the default canvas to Pixelcanvas.io.",
    "brief.canvas.pixelzio": "Sets the default canvas to Pixelz.io.",
    "brief.canvas.pixelzone": "Sets the default canvas to Pixelzone.io.",
    "brief.canvas.pxlsspace": "Sets the default canvas to Pxls.space.",
    "brief.changelog": "Gets a link to my releases page.",
    "brief.diff": "Checks completion status of a template on a canvas.",
    "brief.diff.pixelcanvas": "Creates a diff using Pixelcanvas.io.",
    "brief.diff.pixelzio": "Creates a diff using Pixelz.io.",
    "brief.diff.pixelzone": "Creates a diff using Pixelzone.io.",
    "brief.diff.pxlsspace": "Creates a diff using Pxls.space",
    "brief.ditherchart": "Gets a chart of canvas colors dithered together.",
    "brief.ditherchart.pixelcanvas": "Gets a dither chart of Pixelcanvas.io colors.",
    "brief.ditherchart.pixelzio": "Gets a dither chart of Pixelz.io colors.",
    "brief.ditherchart.pixelzone": "Gets a dither chart of Pixelzone.io colors.",
    "brief.ditherchart.pxlsspace": "Gets a dither chart of Pxls.space colors.",
    "brief.faction": "Manages factions.",
    "brief.faction.create": "Create a faction for this guild.",
    "brief.faction.disband": "Disband this guild's faction.",
    "brief.faction.info": "Get info about a faction.",
    "brief.faction.hide": "Hide a faction from public lists.",
    "brief.faction.unhide": "Unhide a faction from public lists.",
    "brief.faction.set": "Set a property of this guild's faction.",
    "brief.faction.set.name": "Set the name of this guild's faction.",
    "brief.faction.set.alias": "Set the alias of this guild's faction.",
    "brief.faction.set.invite": "Set the invite link of this guild's faction.",
    "brief.faction.set.desc": "Set the description of this guild's faction.",
    "brief.faction.set.emblem": "Set the emblem of this guild's faction",
    "brief.faction.set.color": "Set the color of this guild's faction.",
    "brief.faction.clear": "Clear a property of this guild's faction.",
    "brief.faction.clear.alias": "Clear the alias of this guild's faction.",
    "brief.faction.clear.invite": "Clear the invite of this guild's faction.",
    "brief.faction.clear.desc": "Clear the description of this guild's faction.",
    "brief.faction.clear.emblem": "Clear the emblem of this guild's faction.",
    "brief.faction.clear.color": "Clear the color of this guild's faction.",
    "brief.github": "Gets a link to my GitHub repository.",
    "brief.gridify": "Adds a grid to a template.",
    "brief.help": "Displays this message.",
    "brief.invite": "Gets my invite link.",
    "brief.language": "Sets my language.",
    "brief.ping": "Pong!",
    "brief.prefix": "Sets my command prefix for this guild.",
    "brief.preview": "Previews the canvas at a given coordinate.",
    "brief.preview.pixelcanvas": "Creates a preview using Pixelcanvas.io.",
    "brief.preview.pixelzio": "Creates a preview using Pixelz.io.",
    "brief.preview.pixelzone": "Creates a preview using Pixelzone.io.",
    "brief.preview.pxlsspace": "Creates a preview using Pxls.space.",
    "brief.quantize": "Rough converts an image to the palette of a canvas.",
    "brief.quantize.pixelcanvas": "Quantizes colors using the palette of Pixelcanvas.io.",
    "brief.quantize.pixelzio": "Quantizes colors using the palette of Pixelz.io.",
    "brief.quantize.pixelzone": "Quantizes colors using the palette of Pixelzone.io.",
    "brief.quantize.pxlsspace": "Quantizes colors using the palette of Pxls.space.",
    "brief.register": "Opt-in to animated emoji replacement.",
    "brief.repeat": "Repeats the last used canvas command.",
    "brief.role": "Assign bot privileges to a role.",
    "brief.role.botadmin": "Configure Bot Admin privileges.",
    "brief.role.botadmin.clear": "Clear the role assigned to Bot Admin.",
    "brief.role.botadmin.set": "Set the role assigned to Bot Admin.",
    "brief.role.templateadder": "Configure Template Adder privileges.",
    "brief.role.templateadder.clear": "Clear the role assigned to Template Adder.",
    "brief.role.templateadder.set": "Set the role assigned to Template Adder.",
    "brief.role.templateadmin": "Configure Template Admin privileges.",
    "brief.role.templateadmin.clear": "Clear the role assigned to Template Admin.",
    "brief.role.templateadmin.set": "Set the role assigned to Template Admin.",
    "brief.suggest": "Sends a suggestion to the developer.",
    "brief.template": "Manages templates.",
    "brief.template.add": "Adds a template.",
    "brief.template.add.pixelcanvas": "Adds a template for Pixelcanvas.io.",
    "brief.template.add.pixelzio": "Adds a template for Pixelz.io.",
    "brief.template.add.pixelzone": "Adds a template for Pixelzone.io.",
    "brief.template.add.pxlsspace": "Adds a template for Pxls.space.",
    "brief.template.all": "List all templates for all factions.",
    "brief.template.check": "Check the completion status of all templates.",
    "brief.template.check.pixelcanvas": "Check the completion status of all Pixelcanvas.io templates.",
    "brief.template.check.pixelzio": "Check the completion status of all Pixelz.io templates.",
    "brief.template.check.pixelzone": "Check the completion status of all Pixelzone.io templates.",
    "brief.template.check.pxlsspace": "Check the completion status of all Pxls.space templates.",
    "brief.template.info": "Displays info about a template.",
    "brief.template.remove": "Removes a template.",
    "brief.unregister": "Opt-out of animated emoji replacement.",
    "brief.version": "Gets my version number.",

    # Command long help
    "help.alertchannel.set": "Use the #channel mention syntax with this command to ensure the correct channel is set.",
    "help.autoscan":
        """If enabled, I will watch all messages for coordinates and automatically create previews and diffs according to these rules:
        - Any message with coordinates in the form "@0, 0" will trigger a preview for the default canvas (see `{p}help canvas`)
        - Any message with a link to a supported canvas will trigger a preview for that canvas.
        - Any message with coordinates in the form "0, 0" with a PNG attached will trigger a diff for the default canvas.
        - Previews take precedence over diffs""",
    "help.canvas": "Defaults to Pixelcanvas.io.",
    "help.diff":
        """Images must be in PNG format.
        Error pixels will be marked in red. Pixels that do not match the canvas palette ('bad color') will be marked in blue (see `{p}help quantize`).
        You cannot zoom an image to contain more than 4 million pixels.""",
    "help.faction.create":
        """Factions must have unique names (6 to 32 chars, case sensitive) and, if at all, unique aliases (1 to 5 chars, case insensitive).
        A guild can only have one faction at any given time.""",
    "help.faction.hide": "You can still view info about hidden factions if you explicitly use their name or alias in commands with the `-f` paramater.",
    "help.faction.set.name": "Faction names must be unique. Min 6 chars, max 32 chars. Case sensitive.",
    "help.faction.set.alias": "Faction aliases must be unique. Min 1 char, max 32 chars. Case insensitive.",
    "help.faction.set.desc": "Max 240 characters.",
    "help.faction.set.emblem": "URLs must be Discord URLs.",
    "help.faction.set.color": "Color must be a valid hexidecimal number. Default 0xCF6EE4.",
    "help.gridify": "You cannot zoom an image to contain more than 4 million pixels.",
    "help.prefix": "Max length is 5 characters. You really shouldn't need more than 2.",
    "help.preview": "Maximum zoom is 16. Minimum zoom is -8.",
    "help.quantize":
        """This should primarily be used if `{p}diff` is telling you your image has 'bad color' in it.
        Using this command to create templates from raw images is not suggested.""",
    "help.register":
        """You only need to register once for this to apply to all guilds.
        This feature requires that I have the Manage Messages permission.""",
    "help.repeat": "This command only applies to 'preview', 'diff', and their autoscan invocations. Only 50 messages back will be searched.",
    "help.role.botadmin": "If a user has a role with this privilege bound to it, that user can use any of my commands with no restrictions. They will have the same permissions as guild Administrators.",
    "help.role.templateadder": "If this privilege is bound to a role, all regular members will lose the ability to modify templates unless they have that role.",
    "help.role.templateadmin": "If a user has a role with this privilege bound to it, that user can add and remove any template using the 'templates' command, regardless of ownership.",
    "help.template.add":
        """Image must be in PNG format. If the image is not quantized to the target canvas's palette, I will offer to quantize it for you.
        A guild can have up to 25 templates at any time.
        Templates must have unique names (max 32 chars, case sensitive). If you attempt to add a new template with the same name as an existing one, it will be replaced if you have permission to remove the old one (see `{p}help remove`).
        I only store URLs to templates. If the message that originally uploaded a template is deleted, its URL will break and the template will be lost. Save backups to your computer just in case.""",
    "help.template.remove": "This command can only be used if the template being removed was added by you, unless you are a Template Admin, Bot Admin, or have the Administrator permission (see 'role').",  
    "help.unregister": "You only need to unregister once for this to apply to all guilds.",

    # Command signatures
    "signature.alertchannel": "(subcommand)",
    "signature.alertchannel.set": "<channel>",
    "signature.canvas": "(subcommand)",
    "signature.diff": ["(subcommand) <coordinates> (zoom)", "(-f faction) <template> (zoom)"],
    "signature.diff.pixelcanvas": "<coordinates> (zoom)",
    "signature.diff.pixelzio": "<coordinates> (zoom)",
    "signature.diff.pixelzone": "<coordinates> (zoom)",
    "signature.diff.pxlsspace": "<coordinates> (zoom)",
    "signature.ditherchart": "(subcommand)",
    "signature.faction": "(subcommand)",
    "signature.faction.create": "<name> (alias)",
    "signature.faction.info": "<faction>",
    "signature.faction.hide": "<faction>",
    "signature.faction.unhide": "<faction>",
    "signature.faction.set": "<subcommand>",
    "signature.faction.set.name": "<name>",
    "signature.faction.set.alias": "<alias>",
    "signature.faction.set.desc": "<description>",
    "signature.faction.set.emblem": ["", "<url>"],
    "signature.faction.set.color": "<color>",
    "signature.faction.clear": "<subcommand>",
    "signature.gridify": ["#(size)", "<template> #(size)"],
    "signature.language": "(code)",
    "signature.prefix": "<prefix>",
    "signature.preview": "(subcommand) <coordinates> #(zoom)",
    "signature.preview.pixelcanvas": "<coordinates> #(zoom)",
    "signature.preview.pixelzio": "<coordinates> #(zoom)",
    "signature.preview.pixelzone": "<coordinates> #(zoom)",
    "signature.preview.pxlsspace": "<coordinates> #(zoom)",
    "signature.quantize": "(subcommand)",
    "signature.quantize.pixelcanvas": ["", "<template>"],
    "signature.quantize.pixelzio": ["", "<template>"],
    "signature.quantize.pixelzone": ["", "<template>"],
    "signature.quantize.pxlsspace": ["", "<template>"],
    "signature.role": "(role)",
    "signature.role.botadmin": "(subcommand)",
    "signature.role.botadmin.set": "<role>",
    "signature.role.templateadder": "(subcommand)",
    "signature.role.templateadder.set": "<role>",
    "signature.role.templateadmin": "(subcommand)",
    "signature.role.templateadmin.set": "<role>",
    "signature.suggest": "<suggestion>",
    "signature.template": "(subcommand)",
    "signature.template.add": "(subcommand) <name> <x> <y> (url)",
    "signature.template.add.pixelcanvas": "<name> <x> <y> (url)",
    "signature.template.add.pixelzio": "<name> <x> <y> (url)",
    "signature.template.add.pixelzone": "<name> <x> <y> (url)",
    "signature.template.add.pxlsspace": "<name> <x> <y> (url)",
    "signature.template.check": "(subcommand)",
    "signature.template.info": "(-f faction) <template>",
    "signature.template.remove": "<template>",

    # Examples
    "example.alertchannel": [("clear", "Clear the alert channel if there is one"),
                             ("set #bot-spam", "Set the alert channel to a channel named 'bot-spam")],
    "example.alertchannel.set": [("#bot-spam", "Set the alert channel to a channel named 'bot-spam'")],
    "example.canvas": [("", "Show the currently set default canvas"),
                       ("pc", "Set the default canvas to Pixelcanvas.io")],
    "example.diff": [("pc 100 100", "(with an attachment) Check an image against Pixelcanvas.io at (100, 100)"),
                     ("520 -94 7", "(with an attachment) Check an image against the default canvas at (520, -94) and magnify the result 7 times"),
                     ("\"My Template\"", "Check a template named 'My Template'"),
                     ("-f CoolFaction CoolTemplate", "Check a template named 'CoolTemplate' belonging to the faction 'CoolFaction'")],
    "example.diff.pixelcanvas": [("100 100", "(with an attachment) Check an image against Pixelcanvas.io at (100, 100)"),
                                 ("100 100 7", "(with an attachment) Check an image against Pixelcanvas.io at (100, 100) and magnify the result 7 times.")],
    "example.diff.pixelzio": [("100 100", "(with an attachment) Check an image against Pixelz.io at (100, 100)"),
                              ("100 100 7", "(with an attachment) Check an image against Pixelz.io at (100, 100) and magnify the result 7 times.")],
    "example.diff.pixelzone": [("100 100", "(with an attachment) Check an image against Pixelzone.io at (100, 100)"),
                               ("100 100 7", "(with an attachment) Check an image against Pixelzone.io at (100, 100) and magnify the result 7 times.")],
    "example.diff.pxlsspace": [("100 100", "(with an attachment) Check an image against Pxls.space at (100, 100)"),
                               ("100 100 7", "(with an attachment) Check an image against Pxls.space at (100, 100) and magnify the result 7 times.")],
    "example.ditherchart": [("pc", "Get the ditherchart for Pixelcanvas.io")],
    "example.faction": [("", "List all factions"),
                        ("create \"My Cool Faction\"", "Create a new faction called 'My Cool Faction'"),
                        ("disband", "Disband your faction"),
                        ("info OtherFaction", "Get info about a faction named 'OtherFaction'")],
    "example.faction.create": [("MyCoolFaction", "Create a new faction called 'MyCoolFaction'"),
                               ("\"My Cool Faction\" mcf", "Create a new faction called 'My Cool Faction' with alias 'mcf'")],
    "example.faction.info": [("OtherFaction", "Get info about a faction named 'OtherFaction'"),
                             ("of", "Get info about a faction with the alias 'of'")],
    "example.faction.hide": [("OtherFaction", "Hide a faction named 'OtherFaction'"),
                              ("of", "Hide a faction with the alias 'of'")],
    "example.faction.unhide": [("OtherFaction", "Unhide a faction named 'OtherFaction'"),
                                ("of", "Unhide a faction with the alias 'of'")],
    "example.faction.set": [("name MyFac", "Rename your faction to 'MyFac'"),
                            ("alias aaaa", "Set your faction alias to 'aaaa'"),
                            ("desc We make cool pixel art!", "Set your faction description to 'We make cool pixel art!'")],
    "example.faction.set.name": [("name MyFac", "Rename your faction to 'MyFac'")],
    "example.faction.set.alias": [("alias aaaa", "Set your faction alias to 'aaaa'")],
    "example.faction.set.desc": [("desc We make cool pixel art!", "Set your faction description to 'We make cool pixel art!'")],
    "example.faction.set.emblem": [("", "(with an attachment) Set your faction emblem to the attached image"),
                                   ("https://cdn.discordapp.com/.../avatar.jpg", "Set your faction emblem to the image at the URL")],
    "example.faction.set.color": [("F38C91", "Set your faction color to hex 0xF38C91")],
    "example.faction.clear": [("alias", "Clear your faction's alias"),
                              ("invite", "Delete your faction's invite link"),
                              ("desc", "Clear your faction's description")],
    "example.gridify": [("#8", "(with an attachment) Gridify an image magnified 8 times"),
                        ("MyTemplate #16", "Gridify a template named 'MyTemplate' magnified 8 times"),
                        ("-c 080808 MyTemplate #10", "Gridify a template named 'MyTemplate' magnified 8 times using hex 0x080808 as the grid color")],
    "example.language": [("", "View my current language and available language options"),
                         ("en-us", "Set my language to English (US)")],
    "example.prefix": [("", "View my current prefix"),
                       ("#", "Set my command prefix to '#'")],
    "example.preview": [("pc 900 900", "Preview Pixelcanvas.io centered on (900, 900)"),
                        ("900 900 7", "Preview the default canvas centered on (900, 900) magnified 7 times"),
                        ("900 900 -7", "Preview the default canvas centered on (900, 900) zoomed out 7 times")],
    "example.preview.pixelcanvas": [("900 900", "Preview Pixelcanvas.io centered on (900, 900)"),
                                    ("900 900 7", "Preview Pixelcanvas.io centered on (900, 900) magnified 7 times"),
                                    ("900 900 -7", "Preview Pixelcanvas.io centered on (900, 900) zoomed out 7 times")],
    "example.preview.pixelzio": [("900 900", "Preview Pixelz.io centered on (900, 900)"),
                                 ("900 900 7", "Preview Pixelz.io centered on (900, 900) magnified 7 times"),
                                 ("900 900 -7", "Preview Pixelz.io centered on (900, 900) zoomed out 7 times")],
    "example.preview.pixelzone": [("900 900", "Preview Pixelzone.io centered on (900, 900)"),
                                  ("900 900 7", "Preview Pixelzone.io centered on (900, 900) magnified 7 times"),
                                  ("900 900 -7", "Preview Pixelzone.io centered on (900, 900) zoomed out 7 times")],
    "example.preview.pxlsspace": [("900 900", "Preview Pxls.space centered on (900, 900)"),
                                  ("900 900 7", "Preview Pxls.space centered on (900, 900) magnified 7 times"),
                                  ("900 900 -7", "Preview Pxls.space centered on (900, 900) zoomed out 7 times")],
    "example.quantize": [("", "(with an attachment) Quantize an attachment to the palette of the default canvas"),
                         ("pc", "(with an attachment) Quantize an attachment to the palette of Pixelcanvas.io"),
                         ("pc MyTemplate", "Quantize a template named 'MyTemplate' to the palette of Pixelcanvas.io")],
    "example.quantize.pixelcanvas": [("", "(with an attachment) Quantize an attachment to the palette of the default canvas"),
                                     ("pc", "(with an attachment) Quantize an attachment to the palette of Pixelcanvas.io"),
                                     ("pc MyTemplate", "Quantize a template named 'MyTemplate' to the palette of Pixelcanvas.io")],
    "example.quantize.pixelzio": [("", "(with an attachment) Quantize an attachment to the palette of Pixelz.io"),
                                  ("MyTemplate", "Quantize a template named 'MyTemplate' to the palette of Pixelz.io")],
    "example.quantize.pixelzone": [("", "(with an attachment) Quantize an attachment to the palette of Pixelzone.io"),
                                   ("MyTemplate", "Quantize a template named 'MyTemplate' to the palette of Pixelzone.io")],
    "example.quantize.pxlsspace": [("", "(with an attachment) Quantize an attachment to the palette of Pxls.space"),
                                   ("pc MyTemplate", "Quantize a template named 'MyTemplate' to the palette of Pxls.space")],
    "example.role": [("", "Show the available permissions"),
                     ("botadmin", "Show the role tied to the botadmin permission"),
                     ("botadmin set admin-role", "Set the botadmin permission to a role called 'admin-role'")],
    "example.role.botadmin": [("", "Show the role tied to the botadmin permission"),
                              ("set admin-role", "Set the botadmin permission to a role called 'admin-role'"),
                              ("clear", "Clear the botadmin permission")],
    "example.role.botadmin.set": [("admin-role", "Set the botadmin permission to a role called 'admin-role'")],
    "example.role.templateadder": [("", "Show the role tied to the templateadder permission"),
                                   ("set adder-role", "Set the templateadder permission to a role called 'adder-role'"),
                                   ("clear", "Clear the templateadder permission")],
    "example.role.templateadder.set": [("adder-role", "Set the templateadder permission to a role called 'adder-role'")],
    "example.role.templateadmin": [("", "Show the role tied to the templateadmin permission"),
                                   ("set t-admin-role", "Set the templateadmin permission to a role called 't-admin-role'"),
                                   ("clear", "Clear the templateadmin permission")],
    "example.role.templateadmin.set": [("t-admin-role", "Set the templateadmin permission to a role called 't-admin-role'")],
    "example.suggest": [("you're mom gay lol", "Send 'you're mom gay lol' to the dev as a suggestion")],
    "example.template": [("", "List all templates for this guild"),
                         ("all", "List all public templates for all factions"),
                         ("add pc MyTemplate 100 100", "(with an attachment) Create a template named 'MyTemplate' for Pixelcanvas.io at (100, 100)"),
                         ("-f OtherFaction", "List all public templates for a faction named 'OtherFaction'")],
    "example.template.add": [("MyTemplate 100 100", "(with an attachment) Create a template named 'MyTemplate' for the default canvas at (100, 100)"),
                             ("pc MyTemplate 100 100", "(with an attachment) Create a template named 'MyTemplate' for Pixelcanvas.io at (100, 100)"),
                             ("pc MyTemplate 100 100 https://cdn.discordapp.com/.../avatar.jpg", "Create a template named 'MyTemplate' for Pixelcanvas.io at (100, 100) using the image at the URL")],
    "example.template.add.pixelcanvas": [("MyTemplate 100 100", "(with an attachment) Create a template named 'MyTemplate' for Pixelcanvas.io at (100, 100)"),
                                         ("MyTemplate 100 100 https://cdn.discordapp.com/.../avatar.jpg", "Create a template named 'MyTemplate' for Pixelcanvas.io at (100, 100) using the image at the URL")],
    "example.template.add.pixelzio": [("MyTemplate 100 100", "(with an attachment) Create a template named 'MyTemplate' for Pixelz.io at (100, 100)"),
                                      ("MyTemplate 100 100 https://cdn.discordapp.com/.../avatar.jpg", "Create a template named 'MyTemplate' for Pixelz.io at (100, 100) using the image at the URL")],
    "example.template.add.pixelzone": [("MyTemplate 100 100", "(with an attachment) Create a template named 'MyTemplate' for Pixelzone.io at (100, 100)"),
                                       ("MyTemplate 100 100 https://cdn.discordapp.com/.../avatar.jpg", "Create a template named 'MyTemplate' for Pixelzone.io at (100, 100) using the image at the URL")],
    "example.template.add.pxlsspace": [("MyTemplate 100 100", "(with an attachment) Create a template named 'MyTemplate' for Pxls.space at (100, 100)"),
                                       ("MyTemplate 100 100 https://cdn.discordapp.com/.../avatar.jpg", "Create a template named 'MyTemplate' for Pxls.space at (100, 100) using the image at the URL")],
    "example.template.check": [("", "Check completion status of all this guild's templates"),
                               ("pc", "Check completion status of all this guild's Pixelcanvas.io templates")],
    "example.template.info": [("MyTemplate", "Get info on a template named 'MyTemplate'"),
                              ("-f CoolFaction CoolTemplate", "Get info on a template named 'CoolTemplate' belonging to a faction named 'CoolFaction'")],
    "example.template.remove": [("MyTemplate", "Remove a template named 'MyTemplate'")],

}
