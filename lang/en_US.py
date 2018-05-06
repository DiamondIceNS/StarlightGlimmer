STRINGS = {
    # General messages
    "bot.alert_update": "I have updated to version **{0}**! Check out the command help page for new commands with `{1}help`, or visit https://github.com/DiamondIceNS/StarlightGlimmer/releases for the full changelog.",
    "bot.description":
        """Hi! I'm {0}! I'm here to help coordinate pixel art on pixel-placing websites.
        I've got features like canvas preview and template checking that are sure to be helpful.
        Let's get pixel painting!""",
    "bot.help_ending_note": "Type '{0}{1} <command>' for more info on a command.",
    "bot.ping": "Pinging...",
    "bot.pong": "Pong! | **{0:.01f}s**",
    "bot.suggest": "Your suggestion has been sent. Thank you for your input!",
    "bot.version": "My version number is **{0}**",

    # Animotes messages
    "animotes.guild_opt_in": "Emoji sharing has been **enabled** for this guild.",
    "animotes.guild_opt_out": "Emoji sharing has been **disabled** for this guild.",
    "animotes.member_opt_in": "You have successfully **opted-in** to emoji conversion.",
    "animotes.member_opt_out": "You have successfully **opted-out** of emoji conversion.",

    # Canvas messages
    "render.diff": "{0}/{1} | {2} errors | {3:.2f}% complete",
    "render.diff_bad_color": "{0}/{1} | {2} errors | {3} bad color | {4:.2f}% complete",
    "render.large_template": "(Processing large template, this might take a few seconds...)",
    "render.quantize": "Fixed {0} pixels.",
    "render.repeat_not_found": "Could not find a valid command to repeat.",

    # Configuration messages
    "configuration.alert_channel_cleared": "Alert channel has been cleared.",
    "configuration.alert_channel_set": "Alert channel has been set to {0}.",
    "configuration.autoscan_disabled": "Autoscan has been disabled.",
    "configuration.autoscan_enabled": "Autoscan has been enabled.",
    "configuration.default_canvas_set": "Default canvas has been set to **{0}**.",
    "configuration.prefix_set": "Prefix for this guild has been set to **{0}**.",

    # Error messages
    "bot.error.bad_png": "This image seems to be corrupted. Try re-saving it with an image editor or using `{0}{1}`.",
    "bot.error.command_not_found": "That is not a valid command. Use {0}help to see my commands.",
    "bot.error.command_on_cooldown": "That command is on cooldown. Try again in {0:.01f}s.",
    "bot.error.missing_attachment": "That command requires an attachment.",
    "bot.error.no_canvas": "That command requires a subcommand.",
    "bot.error.no_permission": "You do not have permission to use that command.",
    "bot.error.no_png": "That command requires a PNG image.",
    "bot.error.jpeg": "Seriously? A JPEG? Gross! Please create a PNG template instead.",
    "bot.error.no_private_message": "That command only works in guilds.",
    "bot.error.unhandled_command_error": "An error occurred with that command. The dev has been notified.",

    # Command brief help
    "brief.alertchannel": "Set or clear the channel used for update alerts.",
    "brief.alertchannel.clear": "Clears the alert channel.",
    "brief.alertchannel.set": "Sets the alert channel.",
    "brief.autoscan": "Toggles automatic preview and diff.",
    "brief.changelog": "Gets a link to my releases page.",
    "brief.diff": "Checks completion status of a template on a canvas.",
    "brief.diff.pixelcanvas": "Creates a diff using Pixelcanvas.io.",
    "brief.diff.pixelzio": "Creates a diff using Pixelx.io.",
    "brief.diff.pixelzone": "Creates a diff using Pixelzone.io.",
    "brief.ditherchart": "Gets a chart of canvas colors dithered together.",
    "brief.ditherchart.pixelcanvas": "Gets a dither chart of Pixelcanvas colors.",
    "brief.ditherchart.pixelzio": "Gets a dither chart of Pixelz.io colors.",
    "brief.ditherchart.pixelzone": "Gets a dither chart of Pixelzone colors",
    "brief.github": "Gets a link to my GitHub repository.",
    "brief.help": "Displays this message.",
    "brief.listemotes": "Lists all the animated emoji that I know about.",
    "brief.ping": "Pong!",
    "brief.preview": "Previews the canvas at a given coordinate.",
    "brief.preview.pixelcanvas": "Creates a preview using Pixelcanvas.io.",
    "brief.preview.pixelzio": "Creates a preview using Pixelz.io.",
    "brief.preview.pixelzone": "Creates a preview using Pixelzone.io.",
    "brief.quantize": "Rough converts an image to the palette of a canvas.",
    "brief.quantize.pixelcanvas": "Quantizes colors using the palette of Pixelcanvas.io.",
    "brief.quantize.pixelzio": "Quantizes colors using the palette of Pixelz.io.",
    "brief.quantize.pixelzone": "Quantizes colors using the palette of Pixelzone.io.",
    "brief.register": "Toggles animated emoji replacement for a user.",
    "brief.registerguild": "Toggles emoji sharing for this guild.",
    "brief.repeat": "Repeats the last used canvas command.",
    "brief.setdefaultcanvas": "Sets the default canvas website for this guild.",
    "brief.setdefaultcanvas.pixelcanvas": "Sets the default canvas to Pixelcanvas.io.",
    "brief.setdefaultcanvas.pixelzio": "Sets the default canvas to Pixelz.io.",
    "brief.setdefaultcanvas.pixelzone": "Sets the default canvas to Pixelzone.io.",
    "brief.setprefix": "Sets my command prefix for this guild.",
    "brief.suggest": "Sends a suggestion to the developer.",
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
    "help.ditherchart": None,
    "help.ditherchart.pixelcanvas": None,
    "help.ditherchart.pixelzio": None,
    "help.ditherchart.pixelzone": None,
    "help.github": None,
    "help.help": None,
    "help.listemotes": """See 'registerserver' for more information about emoji sharing.""",
    "help.ping": None,
    "help.preview":
        """Given a coordinate pair or a URL, renders a live view of a canvas at those coordinates.
        
        You can create a zoomed-in preview by adding a zoom factor. (i.e. "0, 0 #4") Maximum zoom is 16.
        
        If autoscan is enabled, this happens automatically using the default canvas. (See 'autoscan' and 'setdefaultcanvas')""",
    "help.preview.pixelcanvas": None,
    "help.preview.pixelzio": None,
    "help.preview.pixelzone": None,
    "help.quantize":
        """Takes an attached image and converts its colors to the palette of a given canvas.
        
        This should primarily be used if the 'pcdiff' command is telling you your template has 'bad color' in it. Using this command to create templates from raw images is not suggested.""",
    "help.quantize.pixelcanvas": None,
    "help.quantize.pixelzio": None,
    "help.quantize.pixelzone": None,
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
    "help.setdefaultcanvas":
        """The default canvas is the canvas that will be used for automatic previews or diffs triggered by autoscan. (See 'autoscan')
        
        Defaults to Pixelcanvas.io.
        
        This command can only be used by members with the Administrator permission.""",
    "help.setdefaultcanvas.pixelcanvas": """This command can only be used by members with the Administrator permission.""",
    "help.setdefaultcanvas.pixelzio": """This command can only be used by members with the Administrator permission.""",
    "help.setdefaultcanvas.pixelzone": """This command can only be used by members with the Administrator permission.""",
    "help.setprefix":
        """Max length is 10 characters. You really shouldn't need more than 2.
        
        This command can only be used by members with the Administrator permission.""",
    "help.suggest": None,
    "help.version": None,

    # Command names
    "command.alertchannel": "alertchannel",
    "command.alertchannel.clear": "clear",
    "command.alertchannel.set": "set",
    "command.autoscan": "autoscan",
    "command.changelog": "changelog",
    "command.diff": "diff",
    "command.diff.pixelcanvas": "pixelcanvas",
    "command.diff.pixelzio": "pixelzio",
    "command.diff.pixelzone": "pixelzone",
    "command.ditherchart": "ditherchart",
    "command.ditherchart.pixelcanvas": "pixelcanvas",
    "command.ditherchart.pixelzio": "pixelzio",
    "command.ditherchart.pixelzone": "pixelzone",
    "command.github": "github",
    "command.help": "help",
    "command.listemotes": "listemotes",
    "command.ping": "ping",
    "command.preview": "preview",
    "command.preview.pixelcanvas": "pixelcanvas",
    "command.preview.pixelzio": "pixelzio",
    "command.preview.pixelzone": "pixelzone",
    "command.quantize": "quantize",
    "command.quantize.pixelcanvas": "pixelcanvas",
    "command.quantize.pixelzio": "pixelzio",
    "command.quantize.pixelzone": "pixelzone",
    "command.register": "register",
    "command.registerguild": "registerguild",
    "command.repeat": "repeat",
    "command.setdefaultcanvas": "setdefaultcanvas",
    "command.setdefaultcanvas.pixelcanvas": "pixelcanvas",
    "command.setdefaultcanvas.pixelzio": "pixelzio",
    "command.setdefaultcanvas.pixelzone": "pixelzone",
    "command.setprefix": "setprefix",
    "command.suggest": "suggest",
    "command.version": "version",

    # Command signatures
    "signature.alertchannel": "alertchannel <subcommand>",
    "signature.alertchannel.clear": "alertchannel clear",
    "signature.alertchannel.set": "alertchannel set <channel>",
    "signature.autoscan": "autoscan",
    "signature.changelog": "changelog",
    "signature.diff": "diff <subcommand>",
    "signature.diff.pixelcanvas": "diff pixelcanvas <coordinates> (zoom)",
    "signature.diff.pixelzio": "diff pixelzio <coordinates> (zoom)",
    "signature.diff.pixelzone": "diff pixelzone <coordinates> (zoom)",
    "signature.ditherchart": "ditherchart <subcommand>",
    "signature.ditherchart.pixelcanvas": "ditherchart pixelcanvas",
    "signature.ditherchart.pixelzio": "ditherchart pixelzio",
    "signature.ditherchart.pixelzone": "ditherchart pixelzone",
    "signature.github": "github",
    "signature.help": "help",
    "signature.listemotes": "listemotes",
    "signature.ping": "ping",
    "signature.preview": "preview <subcommand>",
    "signature.preview.pixelcanvas": "preview pixelcanvas <coordinates> (zoom)",
    "signature.preview.pixelzio": "preview pixelzio <coordinates> (zoom)",
    "signature.preview.pixelzone": "preview pixelzone <coordinates> (zoom)",
    "signature.quantize": "quantize <subcommand>",
    "signature.quantize.pixelcanvas": "quantize pixelcanvas",
    "signature.quantize.pixelzio": "quantize pixelzio",
    "signature.quantize.pixelzone": "quantize pixelzone",
    "signature.register": "register",
    "signature.registerguild": "registerguild",
    "signature.repeat": "repeat",
    "signature.setdefaultcanvas": "setdefaultcanvas <subcommand>",
    "signature.setdefaultcanvas.pixelcanvas": "setdefaultcanvas pixelcanvas",
    "signature.setdefaultcanvas.pixelzio": "setdefaultcanvas pixelzio",
    "signature.setdefaultcanvas.pixelzone": "setdefaultcanvas pixelzone",
    "signature.setprefix": "setprefix <prefix>",
    "signature.suggest": "suggest <suggestion>",
    "signature.version": "version",
}
