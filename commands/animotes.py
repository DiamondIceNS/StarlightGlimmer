import re
import discord
from discord.ext import commands

from utils import checks, sqlite as sql
from objects.channel_logger import ChannelLogger
from objects.logger import Log


#    Cog to reformat messages to allow for animated emotes, regardless of nitro status
#    and sharing those emotes with other servers with opt-in policy.
#    Copyright (C) 2017-2018 Valentijn <ev1l0rd> and DiamondIceNS
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.


class Animotes:
    def __init__(self, bot):
        self.bot = bot
        self.ch_log = ChannelLogger(bot)
        self.log = Log(__name__)

    async def on_message(self, message):
        if not message.author.bot and sql.animotes_users_is_registered(message.author.id):
            channel = message.channel
            content = emote_corrector(self, message)
            if content:
                await message.delete()
                await channel.send(content=content)

    @commands.command()
    async def register(self, ctx):
        sql.animotes_users_add(ctx.author.id)
        await ctx.send(ctx.get_str("animotes.member_opt_in"))

    @commands.command()
    async def unregister(self, ctx):
        sql.animotes_users_delete(ctx.author.id)
        await ctx.send(ctx.get_str("animotes.member_opt_out"))

    @checks.admin_only()
    @commands.guild_only()
    @commands.command()
    async def registerguild(self, ctx):
        sql.guild_update(ctx.guild.id, emojishare=1)
        await self.ch_log.log("Guild **{0.name}** (ID: `{0.id}`) has opted in to emoji sharing.".format(ctx.guild))
        await ctx.send(ctx.get_str("animotes.guild_opt_in"))

    @checks.admin_only()
    @commands.guild_only()
    @commands.command()
    async def unregisterguild(self, ctx):
        sql.guild_update(ctx.guild.id, emojishare=0)
        await self.ch_log.log("Guild **{0.name}** (ID: `{0.id}`) has opted out of emoji sharing.".format(ctx.guild))
        await ctx.send(ctx.get_str("animotes.guild_opt_out"))

    @commands.guild_only()
    @commands.command()
    async def listemotes(self, ctx):
        # TODO: WHY IS THIS NEVER CONSISTENT???
        guilds = []
        blacklist = []
        whitelist = []
        opted_in = sql.guild_is_emojishare(ctx.guild.id)
        whitelist.append(ctx.guild.id)  # Emoji from this server are allowed automatically
        for e in self.bot.emojis:
            if e.animated:
                # No emoji from blacklisted servers
                if e.guild_id in blacklist:
                    continue
                # Do not list cross-server emoji if this server has not opted in
                if e.guild_id != ctx.guild.id and not opted_in:
                    continue
                # Blacklist servers that have not themselves opted in
                if not (e.guild_id in whitelist or sql.guild_is_emojishare(e.guild_id)):
                    blacklist.append(e.guild_id)
                    continue
                # If passed all checks, ensure this server is whitelisted so we can skip future opt-in checks
                if e.guild_id not in whitelist:
                    whitelist.append(e.guild_id)
                if not any(x['id'] for x in guilds if x['id'] == e.guild_id):
                    guild = next(x for x in self.bot.guilds if x.id == e.guild_id)
                    guilds.append({'id': e.guild_id, 'name': guild.name, 'animojis': []})
                pos = next(i for i, x in enumerate(guilds) if x['id'] == e.guild_id)
                guilds[pos]['animojis'].append(str(e))

        for g in guilds:
            msg = "**{0}**:".format(g['name'])
            msg += "\n"
            for e in g['animojis']:
                msg += e
            await ctx.send(msg)


def emote_corrector(self, message):
    r = re.compile(r'(?<![a<]):[\w~]+:')
    found = r.findall(message.content)
    emotes = []
    for em in found:
        temp = discord.utils.get(self.bot.emojis, name=em[1:-1])
        try:
            if temp.animated:
                if temp.guild_id == message.guild.id:
                    emotes.append((em, str(temp)))
                elif sql.guild_is_emojishare(message.guild.id) \
                        and sql.guild_is_emojishare(temp.guild_id):
                    emotes.append((em, str(temp)))
        except AttributeError:
            pass  # We only care about catching this, not doing anything with it

    if emotes:
        temp = message.content
        for em in set(emotes):
            temp = temp.replace(*em)
    else:
        return None

    escape = re.compile(r':*<\w?:\w+:\w+>')
    # This escapes all colons that come before an emoji;
    # thanks to Discord shenanigans, this is needed.
    for esc in set(escape.findall(temp)):
        temp_esc = esc.split('<')
        esc_s = '{}<{}'.format(temp_esc[0].replace(':', '\:'), temp_esc[1])
        temp = temp.replace(esc, esc_s)

    temp = '**<{}>** '.format(message.author.name) + temp

    return temp


def setup(bot):
    bot.add_cog(Animotes(bot))
