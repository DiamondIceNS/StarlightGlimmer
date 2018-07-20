import itertools
import inspect

from discord.ext.commands import Command
from discord.ext.commands.formatter import HelpFormatter

from objects.config import Config

cfg = Config()


class GlimmerHelpFormatter(HelpFormatter):
    def __init__(self):
        super().__init__(width=100)

    async def add_localized_subcommands_to_page(self):
        out = ["```xl"]

        def parent(tup):
            return tup[1].qualified_name

        def is_alias(tup):
            return tup[0] in tup[1].aliases

        entries = []
        filtered = await self.filter_command_list()
        data = sorted(filtered, key=parent)
        for parent, subcommands in itertools.groupby(data, key=parent):
            subcommands = sorted(subcommands, key=is_alias)
            entry = " {} ".format(self.context.s("bot.or_all_caps")).join(["'{}'".format(x[0]) for x in subcommands])
            cmd = subcommands[0][1]
            short_doc = self.context.s("brief." + cmd.qualified_name.replace(' ', '.'))
            entries.append((entry, short_doc))

        width = max(map(lambda en: len(en[0]), entries))
        for e in entries:
            out.append('{0:<{width}} // {1}'.format(*e, width=width))

        out.append("")
        out.append(self.context.s("general.help_subcommand").format(self.context.prefix, self.command.qualified_name))
        out.append("```")
        return out

    async def format(self):
        if self.is_bot():
            out = ["```xl",
                   "'{}'".format(self.context.s("general.help_command_list_header")),
                   "```",
                   self.context.s("general.help_more_info").format(self.clean_prefix)
                   ]

            def category(tup):
                return {
                    'General': '1. General',
                    'Canvas': '2. Canvas',
                    'Template': '3. Template',
                    'Faction': '4. Faction',
                    'Animotes': '5. Animotes',
                    'Configuration': '6. Configuration',
                }[tup[1].cog_name]

            filtered = await self.filter_command_list()
            data = sorted(filtered, key=category)
            for category, commands in itertools.groupby(data, key=category):
                commands = sorted(commands)
                if len(commands) > 0:
                    cog_str = "**{} -**".format(category)
                    for name, command in commands:
                        if name not in command.aliases:
                            cog_str += " `{}`".format(name)
                    out.append(cog_str)

            return out

        if isinstance(self.command, Command):
            dot_name = self.command.qualified_name.replace(' ', '.')
            out = ["**`{}`** {}".format(self.command.qualified_name, self.context.s("brief." + dot_name))]

            usage = "**{}:** ".format(self.context.s("bot.usage"))
            sig = self.context.s("signature." + dot_name)
            if isinstance(sig, list):
                usage += " {} ".format(self.context.s("bot.or_all_caps"))\
                    .join(["`{}{} {}`".format(self.clean_prefix, self.command.qualified_name, x) for x in sig])
            elif sig is not None:
                usage += "`{}{} {}`".format(self.clean_prefix, self.command.qualified_name, sig)
            else:
                usage += "`{}{}`".format(self.clean_prefix, self.command.qualified_name)
            out.append(usage)

            if len(self.command.aliases) > 0:
                aliases = "**{}:** ".format(self.context.s("bot.aliases"))
                aliases += ' '.join(["`{}`".format(a) for a in self.command.aliases])
                out.append(aliases)

            # <long doc> section
            long_doc = self.context.s("help." + dot_name)
            if long_doc:
                out.append("")
                out.append("{}".format(inspect.cleandoc(long_doc)).format(p=self.clean_prefix))

            if self.has_subcommands():
                filtered = await self.filter_command_list()
                if filtered:
                    out.append("")
                    out.append("**{}:**".format(self.context.s("bot.subcommands")))
                    out += await self.add_localized_subcommands_to_page()

            examples = self.context.s("example." + dot_name)
            if examples:
                out.append("")
                out.append("**{}:**".format(self.context.s("bot.examples")))
                for ex in self.context.s("example." + dot_name):
                    out.append("`{}{} {}` {}".format(self.clean_prefix, self.command.qualified_name, *ex))

            return out
