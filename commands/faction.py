import re

import discord
from discord.ext import commands

from objects import errors
from objects.logger import Log
from objects.config import Config
from utils import canvases, checks, sqlite as sql

log = Log(__name__)
cfg = Config()


class Faction:  # TODO: Add brief, help, and signature strings to lang files
    def __init__(self, bot):
        self.bot = bot

    @commands.group(name="faction", invoke_without_command=True, aliases=['f'])
    async def faction(self, ctx, page: int=1):
        fs = sql.guild_get_all_factions()
        if len(fs) > 0:
            pages = 1 + len(fs) // 10
            page = min(max(page, 1), pages)
            g = sql.guild_get_prefix_by_id(ctx.guild.id)

            msg = [
                "**{}** - {} {}/{}".format(ctx.s("faction.list_header"), ctx.s("bot.page"), page, pages),
                "```xl",
                "{0:<34}  {1:<5}".format(ctx.s("bot.name"), ctx.s("bot.alias"))
            ]
            for f in fs[(page - 1) * 10:page * 10]:
                alias = '"{}"'.format(f['faction_alias']) if f['faction_alias'] else ""
                msg.append("{0:<34}  {1:<5}".format('"{}"'.format(f['faction_name']), alias))
            msg.append("")
            msg.append(ctx.s("faction.faction_list_footer_1").format(g))
            msg.append(ctx.s("faction.faction_list_footer_2").format(g))
            msg.append("```")
            await ctx.send('\n'.join(msg))
        else:
            await ctx.send(ctx.s("faction.no_factions"))

    @checks.admin_only()
    @faction.command(name="create")
    async def faction_create(self, ctx, name, alias=None):
        if sql.guild_is_faction(ctx.guild.id):
            await ctx.send(ctx.s("faction.already_faction"))
            return
        name = re.sub("[^\S ]+", "", name)
        if not (6 <= len(name) <= 32):
            raise commands.BadArgument  # TODO: Tell out of range
        alias = re.sub("[^A-Za-z]+", "", alias)
        if alias and not (1 <= len(alias) <= 5):
            raise commands.BadArgument  # TODO: Tell out of range

        sql.guild_faction_set(ctx.guild.id, name=name, alias=alias)
        await ctx.send(ctx.s("faction.created").format(name))

    @checks.admin_only()
    @faction.command(name="disband")
    async def faction_disband(self, ctx):
        if not sql.guild_is_faction(ctx.guild.id):
            await ctx.send(ctx.s("faction.must_be_a_faction"))
            return
        sql.guild_faction_set(ctx.guild.id, name=None, alias=None, emblem=None, invite=None)
        await ctx.send(ctx.s("faction.disbanded"))

    @faction.command(name="info")
    async def faction_info(self, ctx, other=None):
        faction = sql.guild_get_by_faction_name_or_alias(other) if other else sql.guild_get_by_id(ctx.guild.id)
        if not faction:
            await ctx.send(ctx.s("faction.not_found"))
            return
        if not faction['faction_name']:
            await ctx.send(ctx.s("faction.not_a_faction_yet"))
            return

        templates = sql.template_get_all_public_by_guild_id(faction['id'])
        canvas_list = set()
        for t in templates:
            canvas_list.add(t.canvas)

        canvases_pretty = []
        for c in canvas_list:
            canvases_pretty.append(canvases.pretty_print[c])
        canvases_pretty.sort()

        e = discord.Embed(color=faction['faction_color']) \
            .add_field(name=ctx.s("bot.canvases"), value='\n'.join(canvases_pretty))
        if faction['faction_invite']:
            icon_url = self.bot.get_guild(faction['id']).icon_url
            e.set_author(name=faction['faction_name'], url=faction['faction_invite'], icon_url=icon_url)
        else:
            e.set_author(name=faction['faction_name'])
        if faction['faction_desc']:
            e.description = faction['faction_desc']
        if faction['faction_alias']:
            e.description += "\n**{}:** {}".format(ctx.s("bot.alias"), faction['faction_alias'])
        if faction['faction_emblem']:
            e.set_thumbnail(url=faction['faction_emblem'])

        await ctx.send(embed=e)

    @checks.admin_only()
    @faction.command(name="hide")
    async def faction_hide(self, ctx, other):
        if not sql.guild_is_faction(ctx.guild.id):
            await ctx.send(ctx.s("faction.must_be_a_faction"))
            return
        other_fac = sql.guild_get_by_faction_name_or_alias(other)
        if not other_fac:
            await ctx.send(ctx.s("faction.not_found"))
            return
        if sql.is_blocked(ctx.guild.id, other_fac['id']):
            await ctx.send(ctx.s("faction.already_hidden"))
            return
        sql.faction_block_add(ctx.guild.id, other_fac['id'])
        await ctx.send(ctx.s("faction.set_hide").format(other_fac['faction_name']))

    @checks.admin_only()
    @faction.command(name="unhide")
    async def faction_unhide(self, ctx, other):
        if not sql.guild_is_faction(ctx.guild.id):
            await ctx.send(ctx.s("faction.must_be_a_faction"))
            return
        other_fac = sql.guild_get_by_faction_name_or_alias(other)
        if not other_fac:
            await ctx.send(ctx.s("faction.not_found"))
            return
        if not sql.is_blocked(ctx.guild.id, other_fac['id']):
            await ctx.send("That faction has not been hidden.")  # TODO: Localize
            return
        sql.faction_block_remove(ctx.guild.id, other_fac['id'])
        await ctx.send(ctx.s("faction.clear_hide").format(other_fac['faction_name']))

    @checks.admin_only()
    @faction.group(name="set")
    async def faction_set(self, ctx):
        if not sql.guild_is_faction(ctx.guild.id):
            await ctx.send(ctx.s("faction.must_be_a_faction"))
            return

    @faction_set.command(name="name")
    async def faction_set_name(self, ctx, new_name):
        new_name = re.sub("[^\S ]+", "", new_name)
        if not (6 <= len(new_name) <= 32):
            raise commands.BadArgument  # TODO: Tell to long
        if sql.guild_get_by_faction_name(new_name):
            await ctx.send(ctx.s("faction.name_already_exists"))
            return
        sql.guild_faction_set(ctx.guild.id, name=new_name)
        await ctx.send(ctx.s("faction.set_name").format(new_name))

    @faction_set.command(name="desc")
    async def faction_set_desc(self, ctx, *, description):
        description = re.sub("[^\S ]+", "", description)
        if not (len(description) <= 240):
            raise commands.BadArgument  # TODO: Tell to long
        sql.guild_faction_set(ctx.guild.id, desc=description)
        await ctx.send(ctx.s("faction.set_description"))

    @faction_set.command(name="color", aliases=['colour'])
    async def faction_set_color(self, ctx, color: str):
        try:
            color = int(color, 0)
        except ValueError:
            await ctx.send(ctx.s("error.invalid_color"))
            return
        color = abs(color % 16777215)
        sql.guild_faction_set(ctx.guild.id, color=color)
        await ctx.send(ctx.s("faction.set_color"))

    @faction_set.command(name="alias")
    async def faction_set_alias(self, ctx, new_alias):
        new_alias = re.sub("[^A-Za-z]+", "", new_alias)
        if not (1 <= len(new_alias) <= 5):
            raise commands.BadArgument  # TODO: Tell too long
        if sql.guild_get_by_faction_alias(new_alias):
            await ctx.send(ctx.s("faction.alias_already_exists"))
            return
        sql.guild_faction_set(ctx.guild.id, alias=new_alias)
        await ctx.send(ctx.s("faction.set_alias").format(new_alias))

    @faction_set.command(name="emblem")
    async def faction_set_emblem(self, ctx, emblem_url=None):
        if emblem_url:
            if not re.search('^(?:https?://)cdn\.discordapp\.com/', emblem_url):
                raise errors.UrlError
        elif len(ctx.message.attachments) > 0:
            emblem_url = ctx.message.attachments[0].url

        if not emblem_url:
            return

        sql.guild_faction_set(ctx.guild.id, emblem=emblem_url)
        await ctx.send(ctx.s("faction.set_emblem"))

    @faction_set.command(name="invite")
    async def faction_set_invite(self, ctx):
        if not ctx.channel.permissions_for(ctx.guild.me).create_instant_invite:
            raise Exception  # TODO: I do not have permission to do that
        invite = await ctx.channel.create_invite(reason="Invite for faction info page")
        sql.guild_faction_set(ctx.guild.id, invite=invite.url)
        await ctx.send(ctx.s("faction.set_invite"))

    @checks.admin_only()
    @faction.group(name="clear")
    async def faction_clear(self, ctx):
        if not sql.guild_is_faction(ctx.guild.id):
            await ctx.send(ctx.s("faction.must_be_a_faction"))
            return

    @faction_clear.command(name="alias")
    async def faction_clear_alias(self, ctx):
        sql.guild_faction_clear(ctx.guild.id, alias=True)
        await ctx.send(ctx.s("faction.clear_alias"))

    @faction_clear.command(name="desc")
    async def faction_clear_desc(self, ctx):
        sql.guild_faction_clear(ctx.guild.id, desc=True)
        await ctx.send(ctx.s("faction.clear_description"))

    @faction_clear.command(name="color", aliases=['colour'])
    async def faction_clear_color(self, ctx):
        sql.guild_faction_clear(ctx.guild.id, color=True)
        await ctx.send(ctx.s("faction.clear_color"))

    @faction_clear.command(name="emblem")
    async def faction_clear_emblem(self, ctx):
        sql.guild_faction_clear(ctx.guild.id, emblem=True)
        await ctx.send(ctx.s("faction.clear_emblem"))

    @faction_clear.command(name="invite")
    async def faction_clear_invite(self, ctx):
        url = sql.guild_get_by_id(ctx.guild.id)['faction_invite']
        sql.guild_faction_clear(ctx.guild.id, invite=True)

        try:
            await self.bot.delete_invite(url)
            await ctx.send(ctx.s("faction.clear_invite"))
        except discord.Forbidden:
            await ctx.send(ctx.s("faction.clear_invite_cannot_delete"))
        except discord.NotFound:
            await ctx.send(ctx.s("faction.clear_invite"))


def setup(bot):
    bot.add_cog(Faction(bot))
