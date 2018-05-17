import utils.sqlite as sql
from discord.utils import get as dget

canvas_list = {
    'pixelcanvas': "Pixelcanvas.io",
    'pc': "Pixelcanvas.io",
    'pixelzio': "Pixelz.io",
    'pzi': "Pixelz.io",
    'pixelzone': "Pixelzone.io",
    'pz': "Pixelzone.io",
    'pxlsspace': "Pxls.space",
    'ps': "Pxls.space"
}


async def use_default_canvas(ctx, bot, cmd):
    default_canvas = sql.select_guild_by_id(ctx.guild.id)['default_canvas']
    ctx.command = dget(dget(bot.commands, name=cmd).commands, name=default_canvas)
    if ctx.command is not None:
        await bot.invoke(ctx)
