import numpy as np
from PIL import Image, ImageChops, ImageDraw

from objects.chunks import BigChunk, ChunkPz, ChunkPzi, PxlsBoard
from objects.config import Config
from objects.coords import Coords
from objects.logger import Log
from utils import colors, http

cfg = Config()
log = Log(__name__)


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
        diff_img = await fetch(x, y, template.width, template.height)
        log.debug("(X:{0} | Y:{1} | Dim:{2}x{3} | Z:{4})".format(x, y, template.width, template.height, zoom))

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
            error_list.append((*p, t_color, f_color))

        diff_img = diff_img.convert('L').convert('RGB')
        diff_img = Image.composite(Image.new('RGB', template.size, (255, 0, 0)), diff_img, error_mask)
        diff_img = Image.composite(Image.new('RGB', template.size, (0, 0, 255)), diff_img, bad_mask)

    if zoom > 1:
        diff_img = diff_img.resize(tuple(zoom * x for x in diff_img.size), Image.NEAREST)

    return diff_img, tot, err, bad, error_list


async def preview(x, y, zoom, fetch):
    log.debug("(X:{0} | Y:{1} | Zoom:{2})".format(x, y, zoom))

    dim = Coords(cfg.preview_w, cfg.preview_h)
    if zoom < -1:
        dim *= abs(zoom)

    preview_img = await fetch(x - dim.x // 2, y - dim.y // 2, *dim)
    if zoom > 1:
        preview_img = preview_img.resize(tuple(zoom * x for x in preview_img.size), Image.NEAREST)
        tlp = Coords(preview_img.width // 2 - cfg.preview_w // 2, preview_img.height // 2 - cfg.preview_h // 2)
        preview_img = preview_img.crop((*tlp, tlp.x + cfg.preview_w, tlp.y + cfg.preview_h))

    return preview_img


async def quantize(data, palette):
    # TODO: Transparency broken
    with data:
        template = Image.open(data).convert('RGBA')

    log.debug("(Dim:{0}x{1})".format(template.width, template.height))

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

    return template, bad_pixels


async def gridify(data, color, zoom):
    color = (color >> 16 & 255, color >> 8 & 255, color & 255, 255)
    zoom += 1
    with data:
        template = Image.open(data).convert('RGBA')
        log.debug("(Dim:{0}x{1} | Zoom:{2})".format(template.width, template.height, zoom))
        template = template.resize((template.width * zoom, template.height * zoom), Image.NEAREST)
        draw = ImageDraw.Draw(template)
        for i in range(1, template.height):
            draw.line((0, i * zoom, template.width, i * zoom), fill=color)
        for i in range(1, template.width):
            draw.line((i * zoom, 0, i * zoom, template.height), fill=color)
        del draw
        return template


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
