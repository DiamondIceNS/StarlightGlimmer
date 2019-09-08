import itertools
import inspect
import logging
from time import time

import discord
from discord.ext import commands
from discord.ext.commands import BucketType, Command, HelpCommand

import utils
from utils import config, http
from utils.version import VERSION

log = logging.getLogger(__name__)


class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        bot.help_command = GlimmerHelpCommand()
        bot.help_command.cog = self

    @commands.command()
    async def changelog(self, ctx):
        data = await http.get_changelog(VERSION)
        if not data:
            await ctx.send(ctx.s("general.err.cannot_get_changelog"))
            return
        e = discord.Embed(title=data['name'], url=data['url'], color=13594340, description=data['body']) \
            .set_author(name=data['author']['login']) \
            .set_thumbnail(url=data['author']['avatar_url']) \
            .set_footer(text="Released " + data['published_at'])
        await ctx.send(embed=e)

    @commands.command()
    async def github(self, ctx):
        await ctx.send("https://github.com/DiamondIceNS/StarlightGlimmer")

    @commands.command()
    async def invite(self, ctx):
        await ctx.send(config.INVITE)

    @commands.command()
    async def ping(self, ctx):
        ping_start = time()
        ping_msg = await ctx.send(ctx.s("general.ping"))
        ping_time = time() - ping_start
        log.info("(Ping:{0}ms)".format(int(ping_time * 1000)))
        await ping_msg.edit(content=ctx.s("general.pong").format(int(ping_time * 1000)))

    @commands.cooldown(1, 5, BucketType.guild)
    @commands.command()
    async def suggest(self, ctx, *, suggestion: str):
        log.info("Suggestion: {0}".format(suggestion))
        await utils.channel_log(self.bot, "New suggestion from **{0.name}#{0.discriminator}** (ID: `{0.id}`) in guild "
                              "**{1.name}** (ID: `{1.id}`):".format(ctx.author, ctx.guild))
        await utils.channel_log(self.bot, "> `{}`".format(suggestion))
        await ctx.send(ctx.s("general.suggest"))

    @commands.command()
    async def version(self, ctx):
        await ctx.send(ctx.s("general.version").format(VERSION))


class GlimmerHelpCommand(HelpCommand):

    async def send_bot_help(self, mapping):

        out = ["```xl",
               "'{}'".format(self.context.s("general.help_command_list_header")),
               "```"]

        def get_category(command: Command):
            return {
                'General':       '1. General',
                'Canvas':        '2. Canvas',
                'Template':      '3. Template',
                'Faction':       '4. Faction',
                'Animotes':      '5. Fun',
                'Configuration': '6. Animotes'
            }[command.cog_name]

        filtered = await self.filter_commands(self.context.bot.commands, sort=True, key=get_category)

        for cat, cmds in itertools.groupby(filtered, key=get_category):
            cmds = sorted(cmds, key=lambda x: x.name)
            if len(cmds) > 0:
                cog_str = "**{} -**".format(cat)
                for c in cmds:
                    cog_str += " `{}`".format(c.name)
                out.append(cog_str)

        out.extend([
            '',
            self.context.s("general.help_more_info").format(self.clean_prefix)
        ])

        await self.get_destination().send('\n'.join(out))

    async def send_cog_help(self, cog):
        pass  # TODO

    async def send_command_help(self, command):
        dot_name = command.qualified_name.replace(' ', '.')
        out = ["**`{}`** {}".format(command.qualified_name, self.context.s("brief." + dot_name))]

        usage = "**{}:** ".format(self.context.s("bot.usage"))
        sig = self.context.s("signature." + dot_name)
        if isinstance(sig, list):
            usage += " {} ".format(self.context.s("bot.or_all_caps")) \
                .join(["`{}{} {}`".format(self.clean_prefix, command.qualified_name, x) for x in sig])
        elif sig is not None:
            usage += "`{}{} {}`".format(self.clean_prefix, command.qualified_name, sig)
        else:
            usage += "`{}{}`".format(self.clean_prefix, command.qualified_name)
        out.append(usage)

        if len(command.aliases) > 0:
            aliases = "**{}:** ".format(self.context.s("bot.aliases"))
            aliases += ' '.join(["`{}`".format(a) for a in command.aliases])
            out.append(aliases)

        # <long doc> section
        long_doc = self.context.s("help." + dot_name)
        if long_doc:
            out.append("")
            out.append("{}".format(inspect.cleandoc(long_doc)).format(p=self.clean_prefix))

        examples = self.context.s("example." + dot_name)
        if examples:
            out.append("")
            out.append("**{}:**".format(self.context.s("bot.examples")))
            for ex in self.context.s("example." + dot_name):
                out.append("`{}{} {}` {}".format(self.clean_prefix, command.qualified_name, *ex))

        await self.get_destination().send('\n'.join(out))

    async def send_error_message(self, error):
        pass  # TODO

    async def send_group_help(self, group):
        dot_name = group.qualified_name.replace(' ', '.')
        out = ["**`{}`** {}".format(group.qualified_name, self.context.s("brief." + dot_name))]

        usage = "**{}:** ".format(self.context.s("bot.usage"))
        sig = self.context.s("signature." + dot_name)
        if isinstance(sig, list):
            usage += " {} ".format(self.context.s("bot.or_all_caps")) \
                .join(["`{}{} {}`".format(self.clean_prefix, group.qualified_name, x) for x in sig])
        elif sig is not None:
            usage += "`{}{} {}`".format(self.clean_prefix, group.qualified_name, sig)
        else:
            usage += "`{}{}`".format(self.clean_prefix, group.qualified_name)
        out.append(usage)

        if len(group.aliases) > 0:
            aliases = "**{}:** ".format(self.context.s("bot.aliases"))
            aliases += ' '.join(["`{}`".format(a) for a in group.aliases])
            out.append(aliases)

        # <long doc> section
        long_doc = self.context.s("help." + dot_name)
        if long_doc:
            out.append("")
            out.append("{}".format(inspect.cleandoc(long_doc)).format(p=self.clean_prefix))

        filtered = await self.filter_commands(group.commands, sort=True)
        out.append("")
        out.append("**{}:**".format(self.context.s("bot.subcommands")))
        out.append('```xl')
        max_width = max(map(lambda x: len(x.name), filtered))
        for cmd in filtered:
            out.append('{0:<{width}} // {1}'.format(cmd.name, self.context.s('brief.' + cmd.qualified_name.replace(' ', '.')), width=max_width))
        out.append('```')

        examples = self.context.s("example." + dot_name)
        if examples:
            out.append("")
            out.append("**{}:**".format(self.context.s("bot.examples")))
            for ex in self.context.s("example." + dot_name):
                out.append("`{}{} {}` {}".format(self.clean_prefix, group.qualified_name, *ex))

        await self.get_destination().send('\n'.join(out))

