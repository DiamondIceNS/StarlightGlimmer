import aiohttp
import asyncio
import cfscrape
import discord
import io
import json
import lz4.frame
import time
import websockets
from math import sqrt, pow
from PIL import Image, ImageDraw

from utils import colors, checks
from objects.config import Config
from objects.logger import Log
from utils.lzstring import LZString

cfg = Config()
log = Log(__name__)


# Helper class to store coordinate pairs
class Coords:
    def __init__(self, x, y):
        self.coord = (x, y)

    @property
    def x(self):
        return self.coord[0]

    @property
    def y(self):
        return self.coord[1]

    def __iter__(self):
        yield from self.coord

    def __add__(self, other):
        return Coords(self.coord[0] + other, self.coord[1] + other)

    def __sub__(self, other):
        return Coords(self.coord[0] - other, self.coord[1] - other)

    def __mul__(self, other):
        return Coords(self.coord[0] * other, self.coord[1] * other)

    def __floordiv__(self, other):
        return Coords(self.coord[0] // other, self.coord[1] // other)

    def __mod__(self, other):
        return Coords(self.coord[0] % other, self.coord[1] % other)

    def __repr__(self):
        return "Coord({}, {})".format(*self.coord)


async def diff(ctx, x, y, data, zoom, fetch, palette):
    async with ctx.typing():
        with data:
            template = Image.open(data).convert('RGBA')

        with await fetch(x, y, template.width, template.height) as diff_img:
            with template:
                log.debug("(X:{0} | Y:{1} | Dim:{2}x{3} | Z:{4})".format(x, y, template.width, template.height, zoom))

                if template.width * template.height > 600000:
                    await ctx.send(ctx.get_str("render.large_template"))

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
                content = ctx.get_str("render.diff_bad_color").format(tot - err, tot, err, bad, 100 * (tot - err) / tot)
            else:
                content = ctx.get_str("render.diff").format(tot - err, tot, err, 100 * (tot - err) / tot)

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
            return await ctx.send(ctx.get_str("render.quantize").format(bad_pixels), file=f)


async def gridify(ctx, data, zoom):
    zoom += 1
    with data:
        template = Image.open(data).convert('RGBA')
    with template:
        log.debug("(Dim:{0}x{1} | Zoom:{2})".format(template.width, template.height, zoom))
        template = template.resize((template.width * zoom, template.height * zoom), Image.NEAREST)
        draw = ImageDraw.Draw(template)
        for i in range(1, template.height):
            draw.line((0, i * zoom, template.width, i * zoom), fill=(128, 128, 128, 255))
        for i in range(1, template.width):
            draw.line((i * zoom, 0, i * zoom, template.height), fill=(128, 128, 128, 255))
        del draw

        with io.BytesIO() as bio:
            template.save(bio, format="PNG")
            bio.seek(0)
            f = discord.File(bio, "gridded.png")
            await ctx.send(file=f)


async def fetch_pixelcanvas(x, y, dx, dy):
    tl_chk = Coords(x, y) % 64
    tl_bchk = Coords(x, y) // 64 + 7
    bchks_needed = Coords(dx + tl_chk.x, dy + tl_chk.y) // 960 + 1
    fetched = Image.new('RGB', tuple(bchks_needed * 960), colors.pixelcanvas[1])

    class BigChunk:
        def __init__(self, x, y, data):
            self.x = x
            self.y = y
            self.data = data

    bigchunks = []
    async with aiohttp.ClientSession() as session:
        for iy in range(0, bchks_needed.y * 15, 15):
            if not -15632 <= tl_bchk.y + iy < 15632:  # Ignore bigchunks that are out of bounds
                continue
            for ix in range(0, bchks_needed.x * 15, 15):
                if not -15632 <= tl_bchk.x + ix < 15632:  # Ignore bigchunks that are out of bounds
                    continue
                url = "http://pixelcanvas.io/api/bigchunk/{0}.{1}.bmp".format(tl_bchk.x + ix, tl_bchk.y + iy)
                attempts = 0
                bc_data = None
                while not bc_data and attempts < 3:
                    try:
                        async with session.get(url) as resp:
                            bc_data = BigChunk(tl_bchk.x + ix, tl_bchk.y + iy, io.BytesIO(await resp.read()))
                            bigchunks.append(bc_data)
                    except aiohttp.ClientPayloadError:
                        attempts += 1
                        bc_data = None
                if not bc_data:
                    raise checks.HttpPayloadError('pixelcanvas')

    palette_data = [x for sub in colors.pixelcanvas for x in sub] * 16
    for bc in bigchunks:
        bchk_tlp = Coords(bc.x, bc.y) * 64 - 448
        bchk_off = Coords(bc.x - tl_bchk.x, bc.y - tl_bchk.y) // 15 * 960
        for cy in range(0, 960, 64):
            await asyncio.sleep(0)
            for cx in range(0, 960, 64):
                if not -1000000 <= bchk_tlp.x + cx < 1000000 or not -1000000 <= bchk_tlp.y + cy < 1000000:
                    bc.data.seek(2048, 1)  # Skip out of bounds chunks
                    continue
                try:
                    img = Image.frombuffer('P', (64, 64), bc.data.read(2048), 'raw', 'P;4')
                except ValueError:
                    raise checks.HttpPayloadError("pixelcanvas")
                img.putpalette(palette_data)
                fetched.paste(img, (bchk_off.x + cx, bchk_off.y + cy, bchk_off.x + cx + 64, bchk_off.y + cy + 64))

    return fetched.crop((tl_chk.x, tl_chk.y, tl_chk.x + dx, tl_chk.y + dy))


async def fetch_pixelzio(x, y, dx, dy):
    chk = Coords(x, y) // 500 * 500
    chks_needed = Coords((x + dx) // 500 - x // 500 + 1, (y + dy) // 500 - y // 500 + 1)
    fetched = Image.new('RGB', (500 * chks_needed.x, 500 * chks_needed.y), colors.pixelzio[1])

    async with cfscrape.create_scraper_async() as session:
        for iy in range(0, chks_needed.y * 500, 500):
            if not -6000 <= chk.y + iy < 6000:  # Ignore out of bounds chunks
                continue
            for ix in range(0, chks_needed.x * 500, 500):
                if not -6000 <= chk.x + ix < 6000:  # Ignore out of bounds chunks
                    continue
                url = "http://pixelz.io/api/{0}_{1}/img".format(chk.x + ix, chk.y + iy)
                async with session.get(url) as resp:
                    data = await resp.read()
                    tmp = Image.open(io.BytesIO(data)).convert('RGB')
                    fetched.paste(tmp, (ix, iy, ix + 500, iy + 500))

    return fetched.crop((x % 500, y % 500, (x % 500) + dx, (y % 500) + dy))


async def fetch_pixelzone(x, y, dx, dy):
    x += 4096
    y += 4096
    chk = Coords(x, y) // 512
    chks_needed = Coords((x + dx) // 512 - x // 512 + 1, (y + dy) // 512 - y // 512 + 1)
    fetched = Image.new('RGB', (512 * chks_needed.x, 512 * chks_needed.y), colors.pixelzone[2])

    url = "{0}://pixelzone.io/socket.io/?EIO=3&transport={1}"
    pkts_expected = 0
    async with aiohttp.ClientSession() as session:
        async with session.get(url.format("http", "polling")) as r:
            sid = json.loads(str((await r.read())[4:-4], "utf-8"))['sid']
    async with websockets.connect(url.format("ws", "websocket&sid=") + sid) as ws:
        await ws.send("2probe")
        await ws.recv()
        await ws.send("5")
        await ws.recv()
        for iy in range(chks_needed.y):
            for ix in range(chks_needed.x):
                if 0 <= chk.x + ix < 16 and 0 <= chk.y + iy < 16:
                    await ws.send("42[\"getChunkData\", {{\"cx\": {0}, \"cy\": {1}}}]".format(chk.x + ix, chk.y + iy))
                    pkts_expected = pkts_expected + 1
        chunks = []
        if pkts_expected > 0:
            async for msg in ws:
                d = json.loads(msg[msg.find('['):])
                if d[0] == "chunkData":
                    chunks.append(d[1])
                if len(chunks) == pkts_expected:
                    break

    for data in chunks:
        chk_off = Coords(data['cx'] - chk.x, data['cy'] - chk.y) * 512
        tmp = LZString().decompressFromBase64(data['data'])
        tmp = json.loads("[" + tmp + "]")
        tmp = lz4.frame.decompress(bytes(tmp))
        chunk = Image.new('RGB', (512, 512), (255, 255, 255, 255))
        for py in range(chunk.height):
            await asyncio.sleep(0)
            for px in range(chunk.width):
                i = (py * 512 + px) / 2
                color_id = tmp[int(i)] & 15 if i % 1 != 0 else tmp[int(i)] >> 4
                color = colors.pixelzone[color_id]
                chunk.putpixel((px, py), color)
        fetched.paste(chunk, (chk_off.x, chk_off.y, chk_off.x + 512, chk_off.y + 512))

    return fetched.crop((x % 512, y % 512, (x % 512) + dx, (y % 512) + dy))


async def fetch_pxlsspace(x, y, dx, dy):
    fetched = Image.new('RGB', (dx, dy), colors.pxlsspace[1])

    async with aiohttp.ClientSession() as session:
        # Get board info
        async with session.get("http://pxls.space/info") as resp:
            info = json.loads(await resp.read())

        # Get board data
        async with session.get("http://pxls.space/boarddata?={0:.0f}".format(time.time())) as resp:
            data = io.BytesIO(await resp.read())

    board = Image.frombuffer("P", (info['width'], info['height']), data.read(), 'raw', 'P', 0, 1)
    palette_data = [x for sub in colors.pxlsspace for x in sub]
    board.putpalette(palette_data)
    fetched.paste(board, (-x, -y, board.width - x, board.height - y))

    return fetched
