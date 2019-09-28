import logging
import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageOps

from objects import Coords
from objects.chunks import BigChunk, ChunkPz, PxlsBoard
from utils import colors, http, config

log = logging.getLogger(__name__)


async def calculate_size(data):
    template = Image.open(data).convert('RGBA')
    alpha = Image.new('RGBA', template.size, (0, 0, 0, 0))
    white = Image.new('RGBA', template.size, (255, 255, 255, 255))
    white = Image.composite(white, alpha, template)
    return int(np.array(white).any(axis=-1).sum())


async def diff(x, y, data, zoom, fetch, palette):
    with data:
        template = Image.open(data).convert('RGBA')

    with template:
        log.info("(X:{0} | Y:{1} | Dim:{2}x{3} | Z:{4})".format(x, y, template.width, template.height, zoom))
        diff_img = await fetch(x, y, template.width, template.height)

        black = Image.new('1', template.size, 0)
        white = Image.new('1', template.size, 1)
        mask = Image.composite(white, black, template)
        template = template.convert('RGB')

        def lut(i):
            return 255 if i > 0 else 0

        with ImageChops.difference(template, diff_img) as error_mask:
            error_mask = error_mask.point(lut).convert('L').point(lut).convert('1')
            error_mask = Image.composite(error_mask, black, mask)

        with ImageChops.difference(template, _quantize(template, palette)) as bad_mask:
            bad_mask = bad_mask.point(lut).convert('L').point(lut).convert('1')
            bad_mask = Image.composite(bad_mask, black, mask)

        tot = np.array(mask).sum()
        err = np.array(error_mask).sum()
        bad = np.array(bad_mask).sum()
        top15 = np.argwhere(np.array(error_mask))[:15].tolist()

        error_list = []
        for p in top15:
            p.reverse()  # NumPy is backwards
            try:
                t_color = palette.index(template.getpixel(tuple(p)))
            except ValueError:
                t_color = -1
            try:
                f_color = palette.index(diff_img.getpixel(tuple(p)))
            except ValueError:
                f_color = -1
            error_list.append((*p, f_color, t_color))

        diff_img = diff_img.convert('L').convert('RGB')
        diff_img = Image.composite(Image.new('RGB', template.size, (255, 0, 0)), diff_img, error_mask)
        diff_img = Image.composite(Image.new('RGB', template.size, (0, 0, 255)), diff_img, bad_mask)

    if zoom > 1:
        diff_img = diff_img.resize(tuple(zoom * x for x in diff_img.size), Image.NEAREST)

    return diff_img, tot, err, bad, error_list


async def preview(x, y, zoom, fetch):
    log.info("(X:{0} | Y:{1} | Zoom:{2})".format(x, y, zoom))

    dim = Coords(config.PREVIEW_W, config.PREVIEW_H)
    if zoom < -1:
        dim *= abs(zoom)

    preview_img = await fetch(x - dim.x // 2, y - dim.y // 2, *dim)
    if zoom > 1:
        preview_img = preview_img.resize(tuple(zoom * x for x in preview_img.size), Image.NEAREST)
        tlp = Coords(preview_img.width // 2 - config.PREVIEW_W // 2, preview_img.height // 2 - config.PREVIEW_H // 2)
        preview_img = preview_img.crop((*tlp, tlp.x + config.PREVIEW_W, tlp.y + config.PREVIEW_H))

    if config.INVERT:
        preview_img = ImageOps.invert(preview_img)

    return preview_img


async def preview_template(t, zoom, fetch):
    log.info("(X:{0} | Y:{1} | Dim:{2}x{3} | Zoom:{4})".format(t.x, t.y, t.width, t.height, zoom))

    dim = Coords(t.width, t.height)
    if zoom < -1:
        dim *= abs(zoom)

    c = Coords(*t.center())

    preview_img = await fetch(c.x - dim.x // 2, c.y - dim.y // 2, *dim)
    if zoom > 1:
        preview_img = preview_img.resize(tuple(zoom * x for x in preview_img.size), Image.NEAREST)
        tlp = Coords(preview_img.width // 2 - config.PREVIEW_W // 2, preview_img.height // 2 - config.PREVIEW_H // 2)
        preview_img = preview_img.crop((*tlp, tlp.x + config.PREVIEW_W, tlp.y + config.PREVIEW_H))

    return preview_img


async def quantize(data, palette):
    with data:
        template = Image.open(data).convert('RGBA')

    log.info("(Dim:{0}x{1})".format(template.width, template.height))

    black = Image.new('1', template.size, 0)
    white = Image.new('1', template.size, 1)
    mask = Image.composite(white, black, template)
    template = template.convert('RGB')
    q = _quantize(template, palette)

    def lut(i):
        return 255 if i > 0 else 0

    with ImageChops.difference(template, q) as d:
        d = d.point(lut).convert('L').point(lut).convert('1')
        d = Image.composite(d, black, mask)
        bad_pixels = np.array(d).sum()

    alpha = Image.new('RGBA', template.size, (0, 0, 0, 0))
    q = Image.composite(q.convert('RGBA'), alpha, mask)

    return q, bad_pixels


async def gridify(data, color, zoom):
    color = (color >> 16 & 255, color >> 8 & 255, color & 255, 255)
    zoom += 1
    with data:
        template = Image.open(data).convert('RGBA')
        log.info("(Dim:{0}x{1} | Zoom:{2})".format(template.width, template.height, zoom))
        template = template.resize((template.width * zoom, template.height * zoom), Image.NEAREST)
        draw = ImageDraw.Draw(template)
        for i in range(1, template.height):
            draw.line((0, i * zoom, template.width, i * zoom), fill=color)
        for i in range(1, template.width):
            draw.line((i * zoom, 0, i * zoom, template.height), fill=color)
        del draw
        return template


def zoom(data, zoom):
    with data:
        template = Image.open(data).convert('RGBA')
        log.info("(Dim:{0}x{1} | Zoom:{2})".format(template.width, template.height, zoom))
        template = template.resize((template.width * zoom, template.height * zoom), Image.NEAREST)
        return template


async def fetch_pixelcanvas(x, y, dx, dy):
    bigchunks, shape = BigChunk.get_intersecting(x, y, dx, dy)
    fetched = Image.new('RGB', tuple([960 * x for x in shape]), colors.pixelcanvas[1])

    await http.fetch_chunks(bigchunks)

    for i, bc in enumerate(bigchunks):
        if bc.is_in_bounds():
            fetched.paste(bc.image, ((i % shape[0]) * 960, (i // shape[0]) * 960))

    x, y = x - (x + 448) // 960 * 960 + 448, y - (y + 448) // 960 * 960 + 448
    return fetched.crop((x, y, x + dx, y + dy))


async def fetch_pixelzone(x, y, dx, dy):
    chunks, shape = ChunkPz.get_intersecting(x, y, dx, dy)
    fetched = Image.new('RGB', tuple([512 * x for x in shape]), colors.pixelzone[2])

    await http.fetch_chunks(chunks)

    for i, ch in enumerate(chunks):
        if ch.is_in_bounds():
            fetched.paste(ch.image, ((i % shape[0]) * 512, (i // shape[0]) * 512))

    return fetched.crop((x % 512, y % 512, (x % 512) + dx, (y % 512) + dy))


async def fetch_pxlsspace(x, y, dx, dy):
    board = PxlsBoard()
    fetched = Image.new('RGB', (dx, dy), colors.pxlsspace[1])
    await http.fetch_chunks([board])
    fetched.paste(board.image, (-x, -y, board.width - x, board.height - y))
    return fetched


def _quantize(t: Image, palette) -> Image:
    with Image.new('P', (1, 1)) as palette_img:
        p = [x for sub in palette for x in sub] + [0] * (768 - 3 * len(palette))
        palette_img.putpalette(p)
        palette_img.load()
        im = t.im.convert('P', 0, palette_img.im)
        return t._new(im).convert('RGB')
