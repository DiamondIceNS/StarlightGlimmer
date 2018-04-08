import discord
from discord.ext import commands
import re

from utils.channel_logger import ChannelLogger
from utils.logger import Log
from utils.exceptions import NoPermission
import utils.sqlite as sql

#    Cog to reformat messages to allow for animated emotes, regardless of nitro status.
#    Copyright (C) 2017 Valentijn <ev1l0rd>
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
        """Toggle your opt-in status to allow this bot to replace custom emoji on your behalf.

        If you opt-in to this feature, any messages you send that contain emoji that I can see will be deleted
        and replaced with an identical message from the bot with that emoji properly rendered. Bots do not require
        a Nitro account to access cross-server or animated emoji, so you can use this to crudely work around that
        restriction if you do not have Nitro yourself. It's the poor man's Nitro!

        If your server has been opted in to emoji sharing, you can use this feature to steal any emoji from any server
        this bot happens to be in, provided that other server has also opted in.

        Use unregister to opt out after opting in.

        This feature will malfunction if you have Nitro and you use your own animated emoji in the same message. Trying
        to use a Twitch integration server emoji in the same message will probably also break this feature.

        This feature requires me having the Manage Messages permission."""
        if not sql.is_user_animote_user(ctx.author.id):
            sql.add_animote_user(ctx.author.id)
            message = "Successfully opted in to animated emote conversion."
        else:
            sql.delete_animote_user(ctx.author.id)
            message = "Successfully opted out of animated emote conversion."
        await ctx.message.author.send(content=message)

    @commands.command(aliases=['unregisterserver'])
    @commands.guild_only()
    async def registerserver(self, ctx):
        """Toggle the server's opt-in status to emoji sharing.

        Opting in to emoji sharing gives you access to all the emoji I can see in every other server I am in, as long
        as those servers have also opted in to emoji sharing. This also means that opting in gives those servers access
        to YOUR emoji as well. You do not need to opt in to this feature to enable animated emoji replacement for emoji
        unique to this server.

        WARNING: Opting in to this feature will let other servers see all your custom emoji as well as your server's
        name and, by extension, your server's ID. If you do not want to share your server's presence with others, DO
        NOT opt in to this feature!

        This command can only be used by members with the Manage Emojis permission."""
        if not ctx.author.permissions_in(ctx.channel).manage_emojis:
            raise NoPermission
        if not sql.is_server_emojishare_server(ctx.guild.id):
            sql.update_guild(ctx.guild.id, emojishare=1)
            self.log.info("Guild {0.name} (ID: {0.id}) has opted in to emoji sharing.".format(ctx.guild))
            await self.channel_logger.log_to_channel("Guild **{0.name}** (ID: `{0.id}`) has opted in to emoji sharing."
                                                .format(ctx.guild))
            message = "Successfully opted server in to emoji sharing."
        else:
            sql.update_guild(ctx.guild.id, emojishare=0)
            self.log.info("Guild {0.name} (ID: {0.id}) has opted out of emoji sharing.".format(ctx.guild))
            await self.channel_logger.log_to_channel("Guild **{0.name}** (ID: `{0.id}`) has opted out of emoji sharing."
                                                .format(ctx.guild))
            message = "Successfully opted server out of emoji sharing."
        await ctx.send(message)

    @commands.command()
    async def listemotes(self, ctx):
        """Lists out all of the animated emotes that I know about"""
        guilds = []
        blacklist = []
        whitelist = []
        opted_in = sql.is_server_emojishare_server(ctx.guild.id)
        for e in self.bot.emojis:
            if e.guild_id != ctx.guild.id and not opted_in or e.guild_id in blacklist:
                continue
            if not (e.guild_id in whitelist or sql.is_server_emojishare_server(e.guild_id)):
                blacklist.append(e.guild_id)
                continue
            if e.guild_id not in whitelist:
                whitelist.append(e.guild_id)
            if not any(x['id'] for x in guilds if x['id'] == e.guild_id):
                guild = next(x for x in self.bot.guilds if x.id == e.guild_id)
                guilds.append({'id': e.guild_id, 'name': guild.name, 'emojis': [], 'animojis': []})
            pos = next(i for i, x in enumerate(guilds) if x['id'] == e.guild_id)
            if e.animated:
                guilds[pos]['animojis'].append(str(e))
            else:
                guilds[pos]['emojis'].append(str(e))

        for g in guilds:
            msg = "**{0}**:".format(g['name'])
            if len(g['emojis']) > 0:
                msg += "\n"
                for e in g['emojis']:
                    msg += e
            if len(g['animojis']) > 0:
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
            if temp.guild_id == message.guild.id:
                emotes.append((em, str(temp)))
            elif sql.is_server_emojishare_server(message.guild.id) and sql.is_server_emojishare_server(temp.guild_id):
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
