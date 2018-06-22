import asyncio
import discord
import io
import numpy as np
from math import sqrt, pow
from PIL import Image, ImageChops, ImageDraw

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
    def get_mask(t: Image) -> Image:
        with Image.new('1', t.size, 0) as black:
            with Image.new('1', t.size, 1) as white:
                return Image.composite(white, black, t)

    def get_errors(t: Image, f: Image, mask: Image) -> Image:
        with ImageChops.difference(t, f) as diff:
            with diff.point(lambda x: 255 if x > 0 else 0).convert('L').point(
                    lambda x: 255 if x > 0 else 0).convert('1') as diff:
                with Image.new('1', t.size, 0) as black:
                    return Image.composite(diff, black, mask)

    def get_bad_color(t: Image, mask: Image) -> Image:
        with get_errors(t, _quantize(t, palette), mask) as diff:
            with Image.new('1', t.size, 0) as black:
                return Image.composite(diff, black, mask)

    async with ctx.typing():
        with data:
            template = Image.open(data).convert('RGBA')

        with await fetch(x, y, template.width, template.height) as diff_img:
            with template:
                log.debug("(X:{0} | Y:{1} | Dim:{2}x{3} | Z:{4})".format(x, y, template.width, template.height, zoom))

                mask = get_mask(template)
                template = template.convert('RGB')

                tot = np.array(mask).sum()
                e = get_errors(template, diff_img, mask)
                err = np.array(e).sum()
                b = get_bad_color(template, mask)
                bad = np.array(b).sum()

                diff_img = diff_img.convert('L').convert('RGB')
                diff_img = Image.composite(Image.new('RGB', template.size, (255, 0, 0)), diff_img, e)
                diff_img = Image.composite(Image.new('RGB', template.size, (0, 0, 255)), diff_img, b)

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


def _quantize(t: Image, palette) -> Image:
    with Image.new('P', (1, 1)) as palette_img:
        p = [x for sub in palette for x in sub] * (768 // (3 * len(palette)))
        palette_img.putpalette(p)
        palette_img.load()
        im = t.im.convert('P', 0, palette_img.im)
        return t._new(im).convert('RGB')
