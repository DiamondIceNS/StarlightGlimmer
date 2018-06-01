STRINGS = {
    # General messages
    "bot.alert_update": "I have updated to version **{0}**! Check out the command help page for new commands with `{1}help`, or visit https://github.com/DiamondIceNS/StarlightGlimmer/releases for the full changelog.",
    "bot.description":
        """Hi! I'm {0}! I'm here to help coordinate pixel art on pixel-placing websites.
        I've got features like canvas preview and template checking that are sure to be useful.
        Let's get pixel painting!""",
    "bot.discord_urls_only": "I can only accept Discord attachment URLs.",  # TODO: Translate
    "bot.help_ending_note": "Type '{0}{1} <command>' for more info on a command.",
    "bot.ping": "Pinging...",
    "bot.pong": "Pong! | **{0}ms**",
    "bot.suggest": "Your suggestion has been sent. Thank you for your input!",
    "bot.version": "My version number is **{0}**",
    "bot.why": "But... why?",  # TODO: Translate
    "bot.yes_no": "\n  `0` - No\n  `1` - Yes",  # TODO: Translate
    "bot.yes_no_invalid": "That is not a valid option. Please try again.",  # TODO: Translate
    "bot.yes_no_timed_out": "Command timed out.",  # TODO: Translate

    # Animotes messages
    "animotes.guild_opt_in": "Emoji sharing has been **enabled** for this guild.",
    "animotes.guild_opt_out": "Emoji sharing has been **disabled** for this guild.",
    "animotes.member_opt_in": "You have successfully **opted-in** to emoji conversion.",
    "animotes.member_opt_out": "You have successfully **opted-out** of emoji conversion.",

    # Canvas messages
    "canvas.invalid_input": "Invalid input: does not match any template name or supported coordinates format.",  # TODO: Translate
    "canvas.repeat_not_found": "Could not find a valid command to repeat.",

    # Render messages
    "render.diff": "{0}/{1} | {2} errors | {3:.2f}% complete",
    "render.diff_bad_color": "{0}/{1} | {2} errors | {3} bad color | {4:.2f}% complete",
    "render.large_template": "(Processing large template, this might take a few seconds...)",
    "render.quantize": "Fixed {0} pixels.",

    # Template messages
    "template.added": "Template '{0}' added!",  # TODO: Translate
    "template.duplicate_list_open": "The following templates already match this image:\n```xl\n",  # TODO: Translate
    "template.duplicate_list_close": "```\nCreate a new template anyway?",  # TODO: Translate
    "template.info_added_by": "Added By",  # TODO: Translate
    "template.info_date_added": "Date Added",  # TODO: Translate
    "template.info_date_modified": "Date Modified",  # TODO: Translate
    "template.info_canvas": "Canvas",  # TODO: Translate
    "template.info_coords": "Coords",  # TODO: Translate
    "template.info_name": "Name",  # TODO: Translate
    "template.info_size": "Size",  # TODO: Translate
    "template.list_close": "\n// Use '{0}templates <page>' to see that page\n// Use '{0}templates info <name>' to see more info on a template```",  # TODO: Translate
    "template.list_no_templates": "This guild currently has no templates.",  # TODO: Translate
    "template.list_open": "**Template List** - Page {0}/{1}\n```xl\n",  # TODO: Translate
    "template.max_templates": "This guild already has the maximum number of templates. Please remove a template before adding another.",  # TODO: Translate
    "template.name_exists_ask_replace": "A template with the name '{0}' already exists for {1} at ({2}, {3}). Replace it?",  # TODO: Translate
    "template.name_exists_no_permission": "A template with that name already exists. Please choose a different name.",  # TODO: Translate
    "template.name_not_found": "Could not find template with name `{0}`.",  # TODO: Translate
    "template.name_too_long": "That name is too long. Please use a name under {0} characters.",  # TODO: Translate
    "template.no_template_named": "There is no template named '{0}'.",  # TODO: Translate
    "template.not_owner": "You do not have permission to modify that template.",  # TODO: Translate
    "template.not_quantized": "This image contains colors that are not part of this canvas's palette. Would you like to quantize it?",  # TODO: Translate
    "template.remove": "Successfully removed '{0}'.",  # TODO: Translate
    "template.updated": "Template '{0}' updated!",  # TODO: Translate


    # Configuration messages
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
                               "'templateadder' - Can add templates, and remove templates they added themself\n"
                               "'templateadmin' - Can add and remove any template\n"
                               "\n// Use '{0}role <type>' to view the current linked role.\n```",  # TODO: Translate
    "configuration.role_not_found": "That role could not be found.",  # TODO: Translate
    "configuration.role_template_adder_check": "Template adder privileges are currently assigned to `@{0}`.",  # TODO: Translate
    "configuration.role_template_adder_cleared": "Template adder privileges successfully cleared.",  # TODO: Translate
    "configuration.role_template_adder_not_set": "Template adder privileges have not been assigned to a role.",  # TODO: Translate
    "configuration.role_template_adder_set": "Template adder privileges assigned to role `@{0}`.",  # TODO: Translate
    "configuration.role_template_admin_check": "Template admin privileges are currently assigned to `@{0}`.",  # TODO: Translate
    "configuration.role_template_admin_cleared": "Template admin privileges successfully cleared.",  # TODO: Translate
    "configuration.role_template_admin_not_set": "Template admin privileges have not been assigned to a role.",  # TODO: Translate
    "configuration.role_template_admin_set": "Template admin privileges assigned to role `@{0}`.",  # TODO: Translate

    # Error messages
    "bot.error.bad_png": "This image seems to be corrupted. Try re-saving it with an image editor or using `{0}quantize`.",
    "bot.error.command_on_cooldown": "That command is on cooldown. Try again in {0:.01f}s.",
    "bot.error.jpeg": "Seriously? A JPEG? Gross! Please create a PNG template instead.",
    "bot.error.missing_attachment": "That command requires an attachment.",
    "bot.error.no_permission": "You do not have permission to use that command.",
    "bot.error.no_png": "That command requires a PNG image.",
    "bot.error.no_private_message": "That command only works in guilds.",
    "bot.error.pil_image_open_exception": "An error occurred while attempting to open an image. Ensure that the supplied image is not corrupted.",  # TODO: Translate
    "bot.error.template.http_error": "Could not access template URL. (Was the original attachment deleted?)",  # TODO: Translate
    "bot.error.unhandled_command_error": "An unknown error occurred. The dev has been notified.",  # TODO: Update
    "bot.error.url_error": "That URL is invalid. I can only accept Discord attachment URLs.",  # TODO: Update

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
    "brief.github": "Gets a link to my GitHub repository.",
    "brief.gridify": "Adds a grid to a template.",
    "brief.help": "Displays this message.",
    "brief.invite": "Gets my invite link.",
    "brief.language": "Sets my language.",
    "brief.listemotes": "Lists all the animated emoji that I know about.",
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
    "brief.registerguild": "Opt-in to emoji sharing for this guild.",
    "brief.repeat": "Repeats the last used canvas command.",
    "brief.suggest": "Sends a suggestion to the developer.",
    "brief.templates": "Manages templates.",
    "brief.templates.add": "Adds a template.",
    "brief.templates.add.pixelcanvas": "Add a template for Pixelcanvas.io.",
    "brief.unregister": "Opt-out of animated emoji replacement.",
    "brief.unregisterguild": "Opt-out of emoji sharing for this guild.",
    "brief.version": "Gets my version number.",

    # Command long help
    "help.alertchannel": """If an alert channel is set, I will post a message in that channel any time my version number changes to alert you to updates.""",
    "help.alertchannel.clear": """This effectively disables update alerts until a new channel is set.""",
    "help.alertchannel.set":
        """Use the #channel mention syntax with this command to ensure the correct channel is set.
    
        This command can only be used by members with the Administrator permission.""",
    "help.autoscan":
        """If enabled, I will watch all messages for coordinates and automatically create previews and diffs according to these rules:
        - Any message with coordinates in the form "@0, 0" will trigger a preview for the default canvas.
        - Any message with a link to a supported canvas will trigger a preview for that canvas.
        - Any message with coordinates in the form "0, 0" with a PNG attached will trigger a diff for the default canvas.
        - Previews take precedence over diffs
        
        See 'setdefaultcanvas' for more information about the default canvas.
        
        Only users with the Administrator role can use this command.""",
    "help.canvas":
        """The default canvas is the canvas that will be used for automatic previews or diffs triggered by autoscan. (See 'autoscan')
        
        Defaults to Pixelcanvas.io.
        
        This command can only be used by members with the Administrator permission.""",
    "help.canvas.pixelcanvas": """This command can only be used by members with the Administrator permission.""",
    "help.canvas.pixelzio": """This command can only be used by members with the Administrator permission.""",
    "help.canvas.pixelzone": """This command can only be used by members with the Administrator permission.""",
    "help.canvas.pxlsspace": """This command can only be used by members with the Administrator permission.""",
    "help.changelog": None,
    "help.diff":
        """Takes an uploaded template, compares it to the current state of the canvas, and calculates how complete it is. It will also generate an image showing you where the unfinished pixels are.
        
        If the template is smaller than 200x200, you can create a larger image with a zoom factor. (i.e. "0, 0 #4) You cannot zoom an image to be larger than 400x400.
        
        Template must be PNG format.
        
        NOTE: "Bad color" pixels are pixels that are not part of the canvas's palette. (See `quantize`)
        
        If autoscan is enabled, this happens automatically using the default canvas. (See 'autoscan' and 'setdefaultcanvas')""",
    "help.diff.pixelcanvas": None,
    "help.diff.pixelzio": None,
    "help.diff.pixelzone": None,
    "help.diff.pxlsspace": None,
    "help.ditherchart": None,
    "help.ditherchart.pixelcanvas": None,
    "help.ditherchart.pixelzio": None,
    "help.ditherchart.pixelzone": None,
    "help.ditherchart.pxlsspace": None,
    "help.github": None,
    "help.gridify":
        """Takes an uploaded template and creates a gridded version for an easier reference. Use the 'size' parameter to set how large the individual pixels should be. (Default 1) You cannot zoom an image to be larger than 1000x1000.""",
    "help.help": None,
    "help.invite": None,
    "help.language": """Use this command with no arguments to see the current and available languages.""",
    "help.listemotes": """See 'registerserver' for more information about emoji sharing.""",
    "help.ping": None,
    "help.prefix":
        """Max length is 5 characters. You really shouldn't need more than 2.
        
        This command can only be used by members with the Administrator permission.""",
    "help.preview":
        """Given a coordinate pair or a URL, renders a live view of a canvas at those coordinates.
        
        You can create a zoomed-in preview by adding a zoom factor. (i.e. "0, 0 #4") Maximum zoom is 16.
        
        If you do not specify a canvas to use, the default canvas will be used.
        
        If autoscan is enabled, this happens automatically using the default canvas. (See 'autoscan' and 'setdefaultcanvas')""",
    "help.preview.pixelcanvas": None,
    "help.preview.pixelzio": None,
    "help.preview.pixelzone": None,
    "help.preview.pxlsspace": None,
    "help.quantize":
        """Takes an attached image and converts its colors to the palette of a given canvas.
        
        This should primarily be used if the 'pcdiff' command is telling you your template has 'bad color' in it. Using this command to create templates from raw images is not suggested.""",
    "help.quantize.pixelcanvas": None,
    "help.quantize.pixelzio": None,
    "help.quantize.pixelzone": None,
    "help.quantize.pxlsspace": None,
    "help.register":
        """If you opt-in with this command, I will watch for any time you try to use an animated emoji and replace your message with another that has the emoji in it. You only need to opt-in once for this to apply to all guilds. Use this command again to opt-out.
        
        If your guild has opted-in to emoji sharing, you can use emoji from any other guild that has also opted-in. (See 'registerguild')
        
        I can't use animated emoji from guilds I am not in, so I cannot use animated emoji from other guilds posted by Discord Nitro users or from Twitch-integrated guilds.
        
        This feature requires that I have the Manage Messages permission.""",
    "help.registerguild":
        """If opted-in, members of this guild will be able to use animated emoji from any other guild that has also opted-in. In return, animated emoji from this guild can also be used by any of those guilds. This is not required to use animated emoji from this guild.
        
        NOTE: Opting-in to emoji sharing will let other guilds see this guild's name and ID. If your guild is not a public guild, enabling this feature is not recommended.
        
        This command can only be used by members with the Manage Emojis permission.""",
    "help.repeat": "This command only applies to 'preview', 'diff', and their autoscan invocations. Only 50 messages back will be searched.",
    "help.suggest": None,
    "help.templates": None,
    "help.templates.add":
        """This command can accept either a direct file attachment or a Discord attachment URL. Template must be in PNG format.""",  # TODO
    "help.templates.add.pixelcanvas": None,
    "help.unregister": "See 'register'.",
    "help.unregisterguild":
        """See 'registerguild'.
        
        This command can only be used by members with the Manage Emojis permission.""",
    "help.version": None,

    # Command names
    "command.alertchannel": "alertchannel",
    "command.alertchannel.clear": "clear",
    "command.alertchannel.set": "set",
    "command.autoscan": "autoscan",
    "command.canvas": "canvas",
    "command.canvas.pixelcanvas": "pixelcanvas",
    "command.canvas.pixelzio": "pixelzio",
    "command.canvas.pixelzone": "pixelzone",
    "command.canvas.pxlsspace": "pxlsspace",
    "command.changelog": "changelog",
    "command.diff": "diff",
    "command.diff.pixelcanvas": "pixelcanvas",
    "command.diff.pixelzio": "pixelzio",
    "command.diff.pixelzone": "pixelzone",
    "command.diff.pxlsspace": "pxlsspace",
    "command.ditherchart": "ditherchart",
    "command.ditherchart.pixelcanvas": "pixelcanvas",
    "command.ditherchart.pixelzio": "pixelzio",
    "command.ditherchart.pixelzone": "pixelzone",
    "command.ditherchart.pxlsspace": "pxlsspace",
    "command.github": "github",
    "command.gridify": "gridify",
    "command.help": "help",
    "command.invite": "invite",
    "command.language": "language",
    "command.listemotes": "listemotes",
    "command.ping": "ping",
    "command.prefix": "prefix",
    "command.preview": "preview",
    "command.preview.pixelcanvas": "pixelcanvas",
    "command.preview.pixelzio": "pixelzio",
    "command.preview.pixelzone": "pixelzone",
    "command.preview.pxlsspace": "pxlsspace",
    "command.quantize": "quantize",
    "command.quantize.pixelcanvas": "pixelcanvas",
    "command.quantize.pixelzio": "pixelzio",
    "command.quantize.pixelzone": "pixelzone",
    "command.quantize.pxlsspace": "pxlsspace",
    "command.register": "register",
    "command.registerguild": "registerguild",
    "command.repeat": "repeat",
    "command.suggest": "suggest",
    "command.templates": "templates",
    "command.templates.add": "add",
    "command.templates.add.pixelcanvas": "pixelcanvas",
    "command.unregister": "unregister",
    "command.unregisterguild": "unregisterguild",
    "command.version": "version",

    # Command signatures
    "signature.alertchannel": "alertchannel <subcommand>",
    "signature.alertchannel.clear": "alertchannel clear",
    "signature.alertchannel.set": "alertchannel set <channel>",
    "signature.autoscan": "autoscan",
    "signature.canvas": "canvas <canvas>",
    "signature.canvas.pixelcanvas": "canvas [pixelcanvas|pc]",
    "signature.canvas.pixelzio": "canvas [pixelzio|pzi]",
    "signature.canvas.pixelzone": "canvas [pixelzone|pz]",
    "signature.canvas.pxlsspace": "canvas [pxlsspace|ps]",
    "signature.changelog": "changelog",
    "signature.diff": "diff <subcommand>",
    "signature.diff.pixelcanvas": "diff pixelcanvas <coordinates> (zoom)",
    "signature.diff.pixelzio": "diff pixelzio <coordinates> (zoom)",
    "signature.diff.pixelzone": "diff pixelzone <coordinates> (zoom)",
    "signature.diff.pxlsspace": "diff pxlsspace <coordinates> (zoom)",
    "signature.ditherchart": "ditherchart <subcommand>",
    "signature.ditherchart.pixelcanvas": "ditherchart pixelcanvas",
    "signature.ditherchart.pixelzio": "ditherchart pixelzio",
    "signature.ditherchart.pixelzone": "ditherchart pixelzone",
    "signature.ditherchart.pxlsspace": "ditherchart pxlsspace",
    "signature.github": "github",
    "signature.gridify": "gridify (size)",
    "signature.help": "help",
    "signature.invite": "invite",
    "signature.language": "language (code)",
    "signature.listemotes": "listemotes",
    "signature.ping": "ping",
    "signature.prefix": "prefix <prefix>",
    "signature.preview": "[preview|p] (canvas) <coordinates> (zoom)",
    "signature.preview.pixelcanvas": "[preview|p] [pixelcanvas|pc] <coordinates> (zoom)",
    "signature.preview.pixelzio": "preview pixelzio <coordinates> (zoom)",
    "signature.preview.pixelzone": "preview pixelzone <coordinates> (zoom)",
    "signature.preview.pxlsspace": "preview pxlsspace <coordinates> (zoom)",
    "signature.quantize": "quantize <subcommand>",
    "signature.quantize.pixelcanvas": "quantize pixelcanvas",
    "signature.quantize.pixelzio": "quantize pixelzio",
    "signature.quantize.pixelzone": "quantize pixelzone",
    "signature.quantize.pxlsspace": "quantize pxlsspace",
    "signature.register": "register",
    "signature.registerguild": "registerguild",
    "signature.repeat": "repeat",
    "signature.suggest": "suggest <suggestion>",
    "signature.templates": "templates <subcommand>",
    "signature.templates.add": "templates add (canvas) <name> <x> <y> (url)",
    "signature.templates.add.pixelcanvas": "templates add [pixelcanvas|pc] <name> <x> <y> (url)",
    "signature.unregister": "unregister",
    "signature.unregisterguild": "unregisterguild",
    "signature.version": "version",
}
