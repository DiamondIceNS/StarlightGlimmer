import re
import io
import hashlib
import discord
import aiohttp
import asyncio
from PIL import Image
from discord.ext import commands
from discord.ext.commands import BucketType
from utils.language import getlang

import utils.sqlite as sql
from utils.canvases import use_default_canvas, canvas_list
from utils.logger import Log

log = Log(__name__)


class Template:
    def __init__(self, bot):
        self.bot = bot

    @commands.group(name='templates', aliases=['t'])
    @commands.cooldown(1, 5, BucketType.guild)
    async def templates(self, ctx):
        pass

    @templates.group(name='add', invoke_without_subcommand=True)
    @commands.cooldown(1, 5, BucketType.guild)
    async def add(self, ctx):
        await use_default_canvas(ctx, self.bot, "templates.add")

    @staticmethod
    async def select_url(ctx, input_url=None):
        if len(ctx.message.attachments) > 0:
            return ctx.message.attachments[0].filename
        if input_url is not None:
            if re.search('^(?:https?://)cdn\.discordapp\.com/', input_url) is not None:
                return input_url
            await ctx.send("I can only accept Discord attachment URLs.")  # TODO: localize string

    @staticmethod
    async def hash_template(ctx, input_url):
        try:
            async with aiohttp.ClientSession() as sess:
                async with sess.get(input_url) as resp:
                    if resp.status != 200:
                        print("Response not OK")  # TODO
                        return
                    if resp.content_type == "image/jpg" or resp.content_type == "image/jpeg":
                        try:
                            f = discord.File("assets/disdain_for_jpegs.gif", "disdain_for_jpegs.gif")
                            await ctx.send(getlang(ctx.guild.id, "bot.error.jpeg"), file=f)
                        except IOError:
                            await ctx.send(getlang(ctx.guild.id, "bot.error.jpeg"))
                        return
                    if resp.content_type != "image/png":
                        await ctx.send(getlang(ctx.guild.id, "bot.error.no_png"))
                        return
                    data = await resp.read()
                    m = hashlib.md5()
                    with io.BytesIO(data) as bio:
                        Image.open(bio)
                        m.update(bio.getvalue())
                    return m.hexdigest()
        except aiohttp.client_exceptions.InvalidURL:
            print("Not a URL.")  # TODO
        except IOError:
            await ctx.send(getlang(ctx.guild.id, "bot.error.bad_png")
                           .format(sql.get_guild_prefix(ctx.guild.id), getlang(ctx.guild.id, "command.quantize")))

    async def wait_for_confirm(self, ctx, query_msg):
        sql.add_menu_lock(ctx.channel.id, ctx.author.id)

        def check(m):
            return ctx.channel.id == m.channel.id and ctx.author.id == m.author.id

        try:
            resp_msg = await self.bot.wait_for('message', timeout=60.0, check=check)
            while not (resp_msg.content == "0" or resp_msg.content == "1"):
                await ctx.send("That is not a valid option. Please try again.")  # TODO: localize string
                resp_msg = await self.bot.wait_for('message', timeout=60.0, check=check)
        except asyncio.TimeoutError:
            await query_msg.edit(content="Command timed out.")  # TODO: localize string
            return False
        finally:
            sql.remove_menu_lock(ctx.channel.id, ctx.author.id)
        return resp_msg.content == "1"

    async def add_template(self, ctx, canvas, name, x, y, url):
        url = await self.select_url(ctx, url)
        if url is None:
            return
        md5 = await self.hash_template(ctx, url)
        if md5 is None:
            return

        t = sql.get_template_by_name(ctx.guild.id, name)
        ts = sql.get_templates_by_hash(ctx.guild.id, md5)
        if t is not None:
            query_msg = await ctx.send("A template with the name '{0}' already exists for {1} at ({2}, {3}). Replace it?\n  `0` - No\n  `1` - Yes".format(t.name, canvas_list[t.canvas], t.x, t.y))  # TODO: localize string
            if await self.wait_for_confirm(ctx, query_msg):
                if ts is not None and len(ts) > 0:
                    m = "The following templates already match this image:\n```"
                    maxlength = max(map(lambda c: len(t.name), ts))
                    for t in ts:
                        m = m + "{0:<{width}} {1:<15} ({2}, {3})\n".format(t.name, canvas_list[t.canvas], t.x, t.y, width=maxlength)
                    m = m + "```\nCreate a new template anyway?\n  `0` - No\n  `1` - Yes"  # TODO: localize string
                    query_msg = await ctx.send(m)
                    if await self.wait_for_confirm(ctx, query_msg):
                        sql.update_template(ctx.guild.id, name, x, y, canvas, url, md5, ctx.author.id)
                        await ctx.send("Template '{0}' updated!".format(name))  # TODO: localize string
            return
        elif ts is not None:
            m = "The following templates already match this image:\n```"
            maxlength = max(map(lambda c: len(t.name), ts))
            for t in ts:
                m = m + "{0:<{width}} {1:<15} ({2}, {3})\n".format(t.name, canvas_list[t.canvas], t.x, t.y,
                                                                   width=maxlength)
            m = m + "```\nCreate a new template anyway?\n  `0` - No\n  `1` - Yes"  # TODO: localize string
            query_msg = await ctx.send(m)
            if not await self.wait_for_confirm(ctx, query_msg):
                return
        sql.add_template(ctx.guild.id, name, x, y, canvas, url, md5, ctx.author.id)
        await ctx.send("Template '{0}' added!".format(name))  # TODO: localize string

    @add.command()
    @commands.cooldown(1, 5, BucketType.guild)
    async def pixelcanvas(self, ctx, name, x, y, url=None):
        await self.add_template(ctx, "pixelcanvas", name, x, y, url)


def setup(bot):
    bot.add_cog(Template(bot))
