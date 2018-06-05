import asyncio
import itertools
import inspect
from discord.ext.commands import Command
from discord.ext.commands.formatter import HelpFormatter, Paginator

from objects.config import Config

cfg = Config()


class GlimmerHelpFormatter(HelpFormatter):
    def __init__(self):
        super().__init__(width=100)
        self._paginator = None

    def get_localized_ending_note(self):
        command_name = self.context.invoked_with
        return self.context.get_str("bot.help_ending_note").format(self.clean_prefix, command_name)

    def add_localized_subcommands_to_page(self, max_width, commands):
        for name, command in commands:
            if name in command.aliases:
                # skip aliases
                continue

            short_doc = self.context.get_str("brief." + command.qualified_name.replace(' ', '.'))
            entry = '  {0:<{width}} - {1}'.format(name, short_doc, width=max_width)
            shortened = self.shorten(entry)
            self._paginator.add_line(shortened)

    @asyncio.coroutine
    def format(self):
        self._paginator = Paginator()

        if self.is_bot():
            self._paginator.add_line(inspect.cleandoc(self.context.get_str("bot.description").format(cfg.name)),
                                     empty=True)
        elif self.is_cog():
            pass  # TODO: HELP!!
        elif isinstance(self.command, Command):
            self._paginator.add_line(self.context.get_str("brief." + self.command.qualified_name.replace(' ', '.')),
                                     empty=True)

            # TODO: Translate signatures
            # <signature portion>
            signature = self.context.get_str("signature." + self.command.qualified_name.replace(' ', '.'))
            self._paginator.add_line(signature, empty=True)

            # <long doc> section
            long_doc = self.context.get_str("help." + self.command.qualified_name.replace(' ', '.'))
            if long_doc:
                self._paginator.add_line(inspect.cleandoc(long_doc), empty=True)

            # end it here if it's just a regular command
            if not self.has_subcommands():
                self._paginator.close_page()
                return self._paginator.pages

        max_width = self.max_name_size

        def category(tup):
            cog = tup[1].cog_name
            # we insert the zero width space there to give it approximate
            # last place sorting position.
            return cog + ':' if cog is not None else '\u200bNo Category:'

        filtered = yield from self.filter_command_list()
        if self.is_bot():
            data = sorted(filtered, key=category)
            for category, commands in itertools.groupby(data, key=category):
                # there simply is no prettier way of doing this.
                commands = sorted(commands)
                if len(commands) > 0:
                    self._paginator.add_line(category)

                self.add_localized_subcommands_to_page(max_width, commands)
        else:
            filtered = sorted(filtered)
            if filtered:
                self._paginator.add_line('Commands:')
                self.add_localized_subcommands_to_page(max_width, filtered)

        # add the ending note
        self._paginator.add_line()
        ending_note = self.get_localized_ending_note()
        self._paginator.add_line(ending_note)

        return self._paginator.pages
