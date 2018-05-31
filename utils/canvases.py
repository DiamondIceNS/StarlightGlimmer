import utils.sqlite as sql
from discord.utils import get as dget
from utils import render

pretty_print = {
    'pixelcanvas': "Pixelcanvas.io",
    'pc': "Pixelcanvas.io",
    'pixelzio': "Pixelz.io",
    'pzi': "Pixelz.io",
    'pixelzone': "Pixelzone.io",
    'pz': "Pixelzone.io",
    'pxlsspace': "Pxls.space",
    'ps': "Pxls.space"
}

url_templates = {
    'pixelcanvas': "https://pixelcanvas.io/@{0},{1}",
    'pixelzio': "https://pixelz.io/@{0},{1}",
    'pixelzone': "http://pixelzone.io/?p={0},{1}",
    'pxlsspace': "https://pxls.space/#x={0}&y={1}"
}

fetchers = {
    'pixelcanvas': render.fetch_pixelcanvas,
    'pixelzio': render.fetch_pixelzio,
    'pixelzone': render.fetch_pixelzone,
    'pxlsspace': render.fetch_pxlsspace
}


async def invoke_default(ctx, bot, cmd: str):
    default_canvas = sql.select_guild_by_id(ctx.guild.id)['default_canvas']
    cmds = cmd.split('.')
    ctx.command = dget(bot.commands, name=cmds[0])
    if len(cmds) > 1:
        ctx.view.index = 0
        ctx.view.preview = 0
        ctx.view.get_word()
        for c in cmds[1:]:
            ctx.command = dget(ctx.command.commands, name=c)
            ctx.view.skip_ws()
            ctx.view.get_word()
    ctx.command = dget(ctx.command.commands, name=default_canvas)
    if ctx.command is not None:
        await bot.invoke(ctx)
