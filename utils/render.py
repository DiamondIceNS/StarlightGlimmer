import asyncio
import discord
import io
import numpy as np
from math import sqrt, pow
from PIL import Image, ImageDraw

from utils import colors, http
from objects.chunks import BigChunk, ChunkPz, ChunkPzi, PxlsBoard
from objects.config import Config
from objects.coords import Coords
from objects.logger import Log
from objects.template import Template

cfg = Config()
log = Log(__name__)


async def calculate_size(template):  # TODO: UGLY!!!
    if type(template) is Template:
        template = Image.open(await http.get_template(template.url)).convert("RGBA")
    alpha = Image.new('RGBA', template.size, (0, 0, 0, 0))
    white = Image.new('RGBA', template.size, (255, 255, 255, 255))
    white = Image.composite(white, alpha, template)
    return int(np.array(white).any(axis=-1).sum())


async def diff(ctx, x, y, data, zoom, fetch, palette):
    async with ctx.typing():
        with data:
            template = Image.open(data).convert('RGBA')

        with await fetch(x, y, template.width, template.height) as diff_img:
            with template:
                log.debug("(X:{0} | Y:{1} | Dim:{2}x{3} | Z:{4})".format(x, y, template.width, template.height, zoom))

                if template.width * template.height > 600000:
                    await ctx.send(ctx.get("render.large_template"))

                tot = 0  # Total non-transparent pixels in template
                err = 0  # Number of errors
                bad = 0  # Number of pixels in the template that are not in the color palette

                for py in range(template.height):
                    await asyncio.sleep(0)
                    for px in range(template.width):
                        tp = template.getpixel((px, py))
                        dp = diff_img.getpixel((px, py))
                        if tp[3] is not 0:
                            # All non-transparent pixels count to the total
                            tot += 1
                        if 0 < tp[3] < 255 or (tp[3] is 255 and tp[:3] not in palette):
                            # All non-opaque and non-transparent pixels, and opaque pixels of bad colors, are bad
                            pixel = (0, 0, 255, 255)
                            err += 1
                            bad += 1
                        elif tp[3] is 255 and (tp[0] is not dp[0] or tp[1] is not dp[1] or tp[2] is not dp[2]):
                            # All pixels that are valid and opaque but do not match the canvas are wrong
                            pixel = (255, 0, 0, 255)
                            err += 1
                        else:
                            # Render all correct/irrelevant pixels in greyscale
                            avg = round(dp[0] * 0.3 + dp[1] * 0.52 + dp[2] * 0.18)
                            pixel = (avg, avg, avg, 255)

                        diff_img.putpixel((px, py), pixel)

            if zoom > 1:
                diff_img = diff_img.resize(tuple(zoom * x for x in diff_img.size), Image.NEAREST)
            if bad > 0:
                content = ctx.get("render.diff_bad_color").format(tot - err, tot, err, bad, 100 * (tot - err) / tot)
            else:
                content = ctx.get("render.diff").format(tot - err, tot, err, 100 * (tot - err) / tot)

            with io.BytesIO() as bio:
                diff_img.save(bio, format="PNG")
                bio.seek(0)
                f = discord.File(bio, "diff.png")
                await ctx.send(content=content, file=f)


async def preview(ctx, x, y, zoom, fetch):
    async with ctx.typing():
        log.debug("(X:{0} | Y:{1} | Zoom:{2})".format(x, y, zoom))

        dim = Coords(cfg.preview_w, cfg.preview_h)
        if zoom < -1:
            dim *= abs(zoom)

        with await fetch(x - dim.x // 2, y - dim.y // 2, *dim) as preview_img:
            if zoom > 1:
                preview_img = preview_img.resize(tuple(zoom * x for x in preview_img.size), Image.NEAREST)
                tlp = Coords(preview_img.width // 2 - cfg.preview_w // 2, preview_img.height // 2 - cfg.preview_h // 2)
                preview_img = preview_img.crop((*tlp, tlp.x + cfg.preview_w, tlp.y + cfg.preview_h))

            with io.BytesIO() as bio:
                preview_img.save(bio, format="PNG")
                bio.seek(0)
                f = discord.File(bio, "preview.png")
                await ctx.send(file=f)


async def quantize(ctx, data, palette):
    with data:
        template = Image.open(data).convert('RGBA')

    with template:
        log.debug("(Dim:{0}x{1})".format(template.width, template.height))
        bad_pixels = template.height * template.width
        for py in range(template.height):
            await asyncio.sleep(0)
            for px in range(template.width):
                pix = template.getpixel((px, py))

                if pix[3] == 0:  # Ignore fully transparent pixels
                    bad_pixels -= 1
                    continue
                if pix[3] < 30:  # Make barely visible pixels transparent
                    template.putpixel((px, py), (0, 0, 0, 0))
                    continue

                dist = 450
                best_fit = (0, 0, 0)
                for c in palette:
                    if pix[:3] == c:  # If pixel matches exactly, break
                        best_fit = c
                        if pix[3] == 255:  # Pixel is only not bad if it's fully opaque
                            bad_pixels -= 1
                        break
                    tmp = sqrt(pow(pix[0]-c[0], 2) + pow(pix[1]-c[1], 2) + pow(pix[2]-c[2], 2))
                    if tmp < dist:
                        dist = tmp
                        best_fit = c
                template.putpixel((px, py), best_fit + (255,))

        with io.BytesIO() as bio:
            template.save(bio, format="PNG")
            bio.seek(0)
            f = discord.File(bio, "template.png")
            return await ctx.send(ctx.get("render.quantize").format(bad_pixels), file=f)


async def gridify(ctx, data, color, zoom):
    color = (color >> 16 & 255, color >> 8 & 255, color & 255, 255)
    zoom += 1
    with data:
        template = Image.open(data).convert('RGBA')
    with template:
        log.debug("(Dim:{0}x{1} | Zoom:{2})".format(template.width, template.height, zoom))
        template = template.resize((template.width * zoom, template.height * zoom), Image.NEAREST)
        draw = ImageDraw.Draw(template)
        for i in range(1, template.height):
            draw.line((0, i * zoom, template.width, i * zoom), fill=color)
        for i in range(1, template.width):
            draw.line((i * zoom, 0, i * zoom, template.height), fill=color)
        del draw

        with io.BytesIO() as bio:
            template.save(bio, format="PNG")
            bio.seek(0)
            f = discord.File(bio, "gridded.png")
            await ctx.send(file=f)


async def fetch_pixelcanvas(x, y, dx, dy):
    bigchunks, shape = BigChunk.get_intersecting(x, y, dx, dy)
    fetched = Image.new('RGB', tuple([960 * x for x in shape]), colors.pixelcanvas[1])

    await http.fetch_chunks_pixelcanvas(bigchunks)

    for i, bc in enumerate(bigchunks):
        fetched.paste(bc.image, ((i % shape[0]) * 960, (i // shape[0]) * 960))

    x, y = x - (x + 448) // 960 * 960 + 448, y - (y + 448) // 960 * 960 + 448
    return fetched.crop((x, y, x + dx, y + dy))


async def fetch_pixelzio(x, y, dx, dy):
    chunks, shape = ChunkPzi.get_intersecting(x, y, dx, dy)
    fetched = Image.new('RGB', tuple([500 * x for x in shape]), colors.pixelzio[1])

    await http.fetch_chunks_pixelzio(chunks)

    for i, ch in enumerate(chunks):
        fetched.paste(ch.image, ((i % shape[0]) * 500, (i // shape[0]) * 500))

    return fetched.crop((x % 500, y % 500, (x % 500) + dx, (y % 500) + dy))


async def fetch_pixelzone(x, y, dx, dy):
    chunks, shape = ChunkPz.get_intersecting(x, y, dx, dy)
    fetched = Image.new('RGB', tuple([512 * x for x in shape]), colors.pixelzone[2])

    await http.fetch_chunks_pixelzone(chunks)

    for i, ch in enumerate(chunks):
        fetched.paste(ch.image, ((i % shape[0]) * 512, (i // shape[0]) * 512))

    return fetched.crop((x % 512, y % 512, (x % 512) + dx, (y % 512) + dy))


async def fetch_pxlsspace(x, y, dx, dy):
    board = PxlsBoard()
    fetched = Image.new('RGB', (dx, dy), colors.pxlsspace[1])
    await http.fetch_pxlsspace(board)
    fetched.paste(board.image, (-x, -y, board.width - x, board.height - y))
    return fetched
