import re
import discord
from discord.ext import commands

import utils.sqlite as sql
from utils.channel_logger import ChannelLogger
from utils.exceptions import NoPermission
from utils.language import getlang
from utils.logger import Log

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
        self.channel_logger = ChannelLogger(bot)
        self.log = Log(__name__)

    async def on_message(self, message):
        if not message.author.bot and sql.is_user_animote_user(message.author.id):
            channel = message.channel
            content = emote_corrector(self, message)
            if content:
                await message.delete()
                await channel.send(content=content)

    @commands.command(aliases=['unregister'])
    async def register(self, ctx):
        if not sql.is_user_animote_user(ctx.author.id):
            sql.add_animote_user(ctx.author.id)
            message = getlang(ctx.guild.id, "animotes.member_opt_in")
        else:
            sql.delete_animote_user(ctx.author.id)
            message = getlang(ctx.guild.id, "animotes.member_opt_out")
        await ctx.message.author.send(content=message)

    @commands.command(aliases=['unregisterserver'])
    @commands.guild_only()
    async def registerguild(self, ctx):
        if not ctx.author.permissions_in(ctx.channel).manage_emojis:
            raise NoPermission
        if not sql.is_server_emojishare_server(ctx.guild.id):
            sql.update_guild(ctx.guild.id, emojishare=1)
            self.log.info("Guild {0.name} (ID: {0.id}) has opted in to emoji sharing.".format(ctx.guild))
            await self.channel_logger.log_to_channel("Guild **{0.name}** (ID: `{0.id}`) has opted in to emoji sharing."
                                                .format(ctx.guild))
            message = getlang(ctx.guild.id, "animotes.guild_opt_in")
        else:
            sql.update_guild(ctx.guild.id, emojishare=0)
            self.log.info("Guild {0.name} (ID: {0.id}) has opted out of emoji sharing.".format(ctx.guild))
            await self.channel_logger.log_to_channel("Guild **{0.name}** (ID: `{0.id}`) has opted out of emoji sharing."
                                                .format(ctx.guild))
            message = getlang(ctx.guild.id, "animotes.guild_opt_out")
        await ctx.send(message)

    @commands.command()
    async def listemotes(self, ctx):
        guilds = []
        blacklist = []
        whitelist = []
        opted_in = sql.is_server_emojishare_server(ctx.guild.id)
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
                if not (e.guild_id in whitelist or sql.is_server_emojishare_server(e.guild_id)):
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
    '''Locate and change any emotes to emote objects'''
    r = re.compile(r'(?<![a<]):[\w~]+:')
    found = r.findall(message.content)
    emotes = []
    for em in found:
        temp = discord.utils.get(self.bot.emojis, name=em[1:-1])
        try:
            if temp.animated:
                if temp.guild_id == message.guild.id:
                    emotes.append((em, str(temp)))
                elif sql.is_server_emojishare_server(message.guild.id)\
                        and sql.is_server_emojishare_server(temp.guild_id):
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
