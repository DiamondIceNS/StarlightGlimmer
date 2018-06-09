import itertools
import inspect
from discord.ext.commands import Command
from discord.ext.commands.formatter import HelpFormatter, Paginator

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
            entry = ' OR '.join(["'{}'".format(x[0]) for x in subcommands])
            cmd = subcommands[0][1]
            short_doc = self.context.get("brief." + cmd.qualified_name.replace(' ', '.'))
            entries.append((entry, short_doc))

        width = max(map(lambda en: len(en[0]), entries))
        for e in entries:
            out.append('{0:<{width}} // {1}'.format(*e, width=width))

        out.append(
            "\n# Use '{}help {} (subcommand)' to view more info about a subcommand".format(self.context.prefix,
                                                                                           self.command.qualified_name))
        out.append("```")
        return out

    async def format(self):
        if self.is_bot():
            out = ["```xl\n'Commands List'\n```",
                   "Use `{}help [command]` to get help about a specific command.\n".format(self.clean_prefix)]

            def category(tup):
                return {
                    'General': '1. General',
                    'Canvas': '2. Canvas',
                    'Template': '3. Template',
                    'Animotes': '4. Animotes',
                    'Configuration': '5. Configuration',
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
            out = ["**`{}`** {}".format(self.command.qualified_name, self.context.get("brief." + dot_name))]

            usage = "**Usage:** "
            sig = self.context.get("signature." + dot_name)
            if isinstance(sig, list):
                usage += ' OR '.join(["`{}{} {}`".format(self.clean_prefix, self.command.qualified_name, x) for x in sig])
            elif sig is not None:
                usage += "`{}{} {}`".format(self.clean_prefix, self.command.qualified_name, sig)
            else:
                usage += "`{}{}`".format(self.clean_prefix, self.command.qualified_name)
            out.append(usage)

            if len(self.command.aliases) > 0:
                aliases = "**Aliases:** "
                aliases += ' '.join(["`{}`".format(a) for a in self.command.aliases])
                out.append(aliases)

            # <long doc> section
            long_doc = self.context.get("help." + dot_name)
            if long_doc:
                out.append("\n{}".format(inspect.cleandoc(long_doc)).format(p=self.clean_prefix))

            if not self.has_subcommands():
                return out

            filtered = await self.filter_command_list()
            if filtered:
                out.append("\n**Subcommands:**")
                out += await self.add_localized_subcommands_to_page()

            examples = self.context.get("example." + dot_name)
            if examples:
                out.append("\n**Examples:**")
                for ex in self.context.get("example." + dot_name):
                    out.append("`{}{} {}` {}".format(self.clean_prefix, self.command.qualified_name, *ex))

            return out
