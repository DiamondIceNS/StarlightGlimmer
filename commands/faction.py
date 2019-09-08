import logging
import io
import re

import discord
from discord.ext import commands
from PIL import Image

from objects.errors import BadArgumentErrorWithMessage, NoSelfPermissionError, UrlError
from utils import canvases, checks, sqlite as sql

log = logging.getLogger(__name__)


class Faction(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @checks.admin_only()
    @commands.command(name="assemble")
    async def assemble(self, ctx, name, alias=""):
        if sql.guild_is_faction(ctx.guild.id):
            await ctx.send(ctx.s("faction.already_faction"))
            return
        name = re.sub("[^\S ]+", "", name)
        if not (6 <= len(name) <= 32):
            raise BadArgumentErrorWithMessage(ctx.s("faction.err.name_length"))
        if sql.guild_get_by_faction_name(name):
            await ctx.send(ctx.s("faction.name_already_exists"))
            return
        alias = re.sub("[^A-Za-z]+", "", alias).lower()
        if alias and not (1 <= len(alias) <= 5):
            raise BadArgumentErrorWithMessage(ctx.s("faction.err.alias_length"))
        if sql.guild_get_by_faction_alias(alias):
            await ctx.send(ctx.s("faction.alias_already_exists"))
            return

        sql.guild_faction_set(ctx.guild.id, name=name, alias=alias)
        await ctx.send(ctx.s("faction.assembled").format(name))

    @checks.admin_only()
    @commands.command(name="disband")
    async def disband(self, ctx):
        if not sql.guild_is_faction(ctx.guild.id):
            await ctx.send(ctx.s("faction.must_be_a_faction"))
            return
        sql.guild_faction_disband(ctx.guild.id)
        await ctx.send(ctx.s("faction.disbanded"))

    @checks.admin_only()
    @commands.group(name="faction")
    async def faction(self, ctx):
        pass

    @faction.group(name="alias")
    async def faction_alias(self, ctx):
        if not sql.guild_is_faction(ctx.guild.id):
            await ctx.send(ctx.s("faction.must_be_a_faction"))
            return
        if not ctx.invoked_subcommand or ctx.invoked_subcommand.name == "alias":
            alias = sql.guild_get_by_id(ctx.guild.id).faction_alias
            if alias:
                await ctx.send(alias)
            else:
                await ctx.send(ctx.s("faction.no_alias"))

    @faction_alias.command(name="clear")
    async def faction_alias_clear(self, ctx):
        sql.guild_faction_clear(ctx.guild.id, alias=True)
        await ctx.send(ctx.s("faction.clear_alias"))

    @faction_alias.command(name="set")
    async def faction_alias_set(self, ctx, new_alias):
        new_alias = re.sub("[^A-Za-z]+", "", new_alias).lower()
        if not (1 <= len(new_alias) <= 5):
            raise BadArgumentErrorWithMessage(ctx.s("faction.err.alias_length"))
        if sql.guild_get_by_faction_alias(new_alias):
            await ctx.send(ctx.s("faction.alias_already_exists"))
            return
        sql.guild_faction_set(ctx.guild.id, alias=new_alias)
        await ctx.send(ctx.s("faction.set_alias").format(new_alias))

    @faction.group(name="color", aliases=["colour"])
    async def faction_color(self, ctx):
        if not sql.guild_is_faction(ctx.guild.id):
            await ctx.send(ctx.s("faction.must_be_a_faction"))
            return
        if not ctx.invoked_subcommand or ctx.invoked_subcommand.name == "color":
            color = sql.guild_get_by_id(ctx.guild.id).faction_color
            img = Image.new('RGB', (32, 32), color)
            with io.BytesIO() as bio:
                img.save(bio, format="PNG")
                bio.seek(0)
                f = discord.File(bio, "color.png")
                await ctx.send('0x{0:06X}'.format(color), file=f)

    @faction_color.command(name="clear")
    async def faction_color_clear(self, ctx):
        sql.guild_faction_clear(ctx.guild.id, color=True)
        await ctx.send(ctx.s("faction.clear_color"))

    @faction_color.command(name="set")
    async def faction_color_set(self, ctx, color: str):
        try:
            color = abs(int(color, 16) % 0xFFFFFF)
        except ValueError:
            await ctx.send(ctx.s("error.invalid_color"))
            return
        sql.guild_faction_set(ctx.guild.id, color=color)
        await ctx.send(ctx.s("faction.set_color"))

    @faction.group(name="desc")
    async def faction_desc(self, ctx):
        if not sql.guild_is_faction(ctx.guild.id):
            await ctx.send(ctx.s("faction.must_be_a_faction"))
            return
        if not ctx.invoked_subcommand or ctx.invoked_subcommand.name == "desc":
            desc = sql.guild_get_by_id(ctx.guild.id).faction_desc
            if desc:
                await ctx.send(desc)
            else:
                await ctx.send(ctx.s("faction.no_description"))

    @faction_desc.command(name="clear")
    async def faction_desc_clear(self, ctx):
        sql.guild_faction_clear(ctx.guild.id, desc=True)
        await ctx.send(ctx.s("faction.clear_description"))

    @faction_desc.command(name="set")
    async def faction_desc_set(self, ctx, *, description):
        description = re.sub("[^\S ]+", "", description)
        if not (len(description) <= 240):
            raise BadArgumentErrorWithMessage(ctx.s("faction.err.description_length"))
        sql.guild_faction_set(ctx.guild.id, desc=description)
        await ctx.send(ctx.s("faction.set_description"))

    @faction.group(name="emblem")
    async def faction_emblem(self, ctx):
        if not sql.guild_is_faction(ctx.guild.id):
            await ctx.send(ctx.s("faction.must_be_a_faction"))
            return
        if not ctx.invoked_subcommand or ctx.invoked_subcommand.name == "emblem":
            emblem = sql.guild_get_by_id(ctx.guild.id).faction_emblem
            if emblem:
                await ctx.send(emblem)
            else:
                await ctx.send(ctx.s("faction.no_emblem"))

    @faction_emblem.command(name="clear")
    async def faction_emblem_clear(self, ctx):
        sql.guild_faction_clear(ctx.guild.id, emblem=True)
        await ctx.send(ctx.s("faction.clear_emblem"))

    @faction_emblem.command(name="set")
    async def faction_emblem_set(self, ctx, emblem_url=None):
        if emblem_url:
            if not re.search('^(?:https?://)cdn\.discordapp\.com/', emblem_url):
                raise UrlError
        elif len(ctx.message.attachments) > 0:
            emblem_url = ctx.message.attachments[0].url

        if not emblem_url:
            return

        sql.guild_faction_set(ctx.guild.id, emblem=emblem_url)
        await ctx.send(ctx.s("faction.set_emblem"))

    @faction.group(name="invite")
    async def faction_invite(self, ctx):
        if not sql.guild_is_faction(ctx.guild.id):
            await ctx.send(ctx.s("faction.must_be_a_faction"))
            return
        if not ctx.invoked_subcommand or ctx.invoked_subcommand.name == "invite":
            invite = sql.guild_get_by_id(ctx.guild.id).faction_invite
            if invite:
                await ctx.send(invite)
            else:
                await ctx.send(ctx.s("faction.no_invite"))

    @faction_invite.command(name="clear")
    async def faction_invite_clear(self, ctx):
        sql.guild_faction_clear(ctx.guild.id, invite=True)
        await ctx.send(ctx.s("faction.clear_invite"))

    @faction_invite.command(name="set")
    async def faction_invite_set(self, ctx, url=None):
        if url:
            try:
                invite = await self.bot.get_invite(url)
            except discord.NotFound:
                await ctx.send(ctx.s("faction.err.invalid_invite"))
                return
            if invite.guild.id != ctx.guild.id:
                await ctx.send(ctx.s("faction.err.invite_not_this_guild"))
                return
            if not re.match(r'(?:https?://)discord\.gg/\w+', url):
                url = "https://discord.gg/" + url
        else:
            if not ctx.channel.permissions_for(ctx.guild.me).create_instant_invite:
                raise NoSelfPermissionError
            invite = await ctx.channel.create_invite(reason="Invite for faction info page")
            url = invite.url
        sql.guild_faction_set(ctx.guild.id, invite=url)
        await ctx.send(ctx.s("faction.set_invite"))

    @faction.group(name="name")
    async def faction_name(self, ctx):
        if not sql.guild_is_faction(ctx.guild.id):
            await ctx.send(ctx.s("faction.must_be_a_faction"))
            return
        if not ctx.invoked_subcommand or ctx.invoked_subcommand.name == "name":
            await ctx.send(sql.guild_get_by_id(ctx.guild.id).faction_name)

    @faction_name.command(name="set")
    async def faction_name_set(self, ctx, new_name):
        new_name = re.sub("[^\S ]+", "", new_name)
        if not (6 <= len(new_name) <= 32):
            raise BadArgumentErrorWithMessage(ctx.s("faction.err.name_length"))
        if sql.guild_get_by_faction_name(new_name):
            await ctx.send(ctx.s("faction.name_already_exists"))
            return
        sql.guild_faction_set(ctx.guild.id, name=new_name)
        await ctx.send(ctx.s("faction.set_name").format(new_name))

    @commands.command(name="factionlist", aliases=['fl'])
    async def factionlist(self, ctx, page: int = 1):
        fs = [x for x in sql.guild_get_all_factions() if x.id not in sql.faction_hides_get_all(ctx.guild.id)]
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
                alias = '"{}"'.format(f.faction_alias) if f.faction_alias else ""
                msg.append("{0:<34}  {1:<5}".format('"{}"'.format(f.faction_name), alias))
            msg.append("")
            msg.append("// " + ctx.s("faction.faction_list_footer_1").format(g))
            msg.append("// " + ctx.s("faction.faction_list_footer_2").format(g))
            msg.append("```")
            await ctx.send('\n'.join(msg))
        else:
            await ctx.send(ctx.s("faction.no_factions"))

    @checks.admin_only()
    @commands.command(name="hide")
    async def hide(self, ctx, other):
        other_fac = sql.guild_get_by_faction_name_or_alias(other)
        if not other_fac:
            await ctx.send(ctx.s("error.faction_not_found"))
            return
        sql.faction_hides_add(ctx.guild.id, other_fac.id)
        await ctx.send(ctx.s("faction.set_hide").format(other_fac.faction_name))

    @commands.command(name="factioninfo", aliases=['fi'])
    async def factioninfo(self, ctx, other=None):
        g = sql.guild_get_by_faction_name_or_alias(other) if other else sql.guild_get_by_id(ctx.guild.id)
        if not g:
            await ctx.send(ctx.s("error.faction_not_found"))
            return
        if not g.faction_name:
            await ctx.send(ctx.s("faction.not_a_faction_yet"))
            return

        templates = sql.template_get_all_public_by_guild_id(g.id)
        canvas_list = set()
        for t in templates:
            canvas_list.add(t.canvas)

        canvases_pretty = []
        for c in canvas_list:
            canvases_pretty.append(canvases.pretty_print[c])
        canvases_pretty.sort()
        canvas_list = '\n'.join(canvases_pretty)

        e = discord.Embed(color=g.faction_color)
        if canvas_list:
            e.add_field(name=ctx.s("bot.canvases"), value='\n'.join(canvases_pretty))
        if g.faction_invite:
            icon_url = self.bot.get_guild(g.id).icon_url
            e.set_author(name=g.faction_name, url=g.faction_invite, icon_url=icon_url)
        else:
            e.set_author(name=g.faction_name)
        e.description = g.faction_desc if g.faction_desc else ""
        if g.faction_alias:
            e.description = "**{}:** {}\n".format(ctx.s("bot.alias"), g.faction_alias) + e.description
        if g.faction_emblem:
            e.set_thumbnail(url=g.faction_emblem)

        await ctx.send(embed=e)

    @checks.admin_only()
    @commands.command(name="unhide")
    async def unhide(self, ctx, other=None):
        if other is None:
            fs = [x for x in sql.guild_get_all_factions() if x.id not in sql.faction_hides_get_all(ctx.guild.id)]
            if len(fs) == 0:
                await ctx.send(ctx.s("faction.no_factions_hidden"))
                return
            out = [
                ctx.s("faction.currently_hidden"),
                "```xl",
                "{0:<34}  {1:<5}".format(ctx.s("bot.name"), ctx.s("bot.alias"))
            ]
            for f in fs:
                alias = '"{}"'.format(f.faction_alias) if f.faction_alias else ""
                out.append("{0:<34}  {1:<5}".format('"{}"'.format(f.faction_name), alias))
            out.append('```')
            await ctx.send('\n'.join(out))
            return
        other_fac = sql.guild_get_by_faction_name_or_alias(other)
        if not other_fac:
            await ctx.send(ctx.s("error.faction_not_found"))
            return
        sql.faction_hides_remove(ctx.guild.id, other_fac.id)
        await ctx.send(ctx.s("faction.clear_hide").format(other_fac.faction_name))
