import aiohttp
import asyncio
import discord
import io
import json
import lz4.frame
import websockets
import time
from math import sqrt, pow
from PIL import Image

import utils.colors as colors
from utils.config import Config
from utils.logger import Log
from utils.language import getlang
from utils.lzstring import LZString

cfg = Config()
log = Log(__name__)


# Helper class to store coordinate pairs
class Coords:
    def __init__(self, x, y):
        self.x = x
        self.y = y


async def diff(ctx, x, y, att, zoom, fetch, palette):
    async with ctx.typing():
        with io.BytesIO() as bio:
            await att.save(bio)
            template = Image.open(bio).convert('RGBA')

        log.debug("(X:{0} | Y:{1} | Dim:{2}x{3} | Zoom:{4})".format(x, y, template.width, template.height, zoom))

        if template.width * template.height > 600000:
            await ctx.send(getlang(ctx.guild.id, "render.large_template"))

        diff_img = await fetch(x, y, template.width, template.height)

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
            content = getlang(ctx.guild.id, "render.diff_bad_color")\
                .format(tot - err, tot, err, bad, 100 * (tot - err) / tot)
        else:
            content = getlang(ctx.guild.id, "render.diff").format(tot - err, tot, err, 100 * (tot - err) / tot)

        with io.BytesIO() as bio:
            diff_img.save(bio, format="PNG")
            bio.seek(0)
            f = discord.File(bio, "diff.png")
            await ctx.send(content=content, file=f)


async def preview(ctx, x, y, zoom, fetch):
    async with ctx.typing():
        log.debug("(X:{0} | Y:{1} | Zoom:{2})".format(x, y, zoom))

        preview_img = await fetch(x - cfg.preview_w // 2, y - cfg.preview_h // 2, cfg.preview_w, cfg.preview_h)

        if zoom > 1:
            preview_img = preview_img.resize(tuple(zoom * x for x in preview_img.size), Image.NEAREST)
            tlp_z = Coords(preview_img.width // 2 - cfg.preview_w // 2, preview_img.height // 2 - cfg.preview_h // 2)
            preview_img = preview_img.crop((tlp_z.x, tlp_z.y, tlp_z.x + cfg.preview_w, tlp_z.y + cfg.preview_h))

        with io.BytesIO() as bio:
            preview_img.save(bio, format="PNG")
            bio.seek(0)
            f = discord.File(bio, "preview.png")
            await ctx.send(file=f)


async def quantize(ctx, att, palette):
    with io.BytesIO() as bio:
        await att.save(bio)
        template = Image.open(bio).convert('RGBA')

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
        await ctx.send(getlang(ctx.guild.id, "render.quantize").format(bad_pixels), file=f)


async def gridify(ctx, att, zoom):
    with io.BytesIO() as bio:
        await att.save(bio)
        template = Image.open(bio).convert('RGBA')

    log.debug("(Dim:{0}x{1} | Zoom:{2})".format(template.width, template.height, zoom))

    grid_img = Image.new('RGBA', (template.width * (zoom + 1) - 1, template.height * (zoom + 1) - 1))
    for iy in range(template.height):
        await asyncio.sleep(0)
        for ix in range(template.width):
            for ziy in range(zoom):
                for zix in range(zoom):
                    grid_img.putpixel((ix * (zoom + 1) + zix, iy * (zoom + 1) + ziy), template.getpixel((ix, iy)))

    for iy in range(template.height - 1):
        for ix in range(grid_img.width):
            grid_img.putpixel((ix, (iy + 1) * (zoom + 1) - 1), (128, 128, 128, 255))
    for ix in range(template.width - 1):
        for iy in range(grid_img.height):
            grid_img.putpixel(((ix + 1) * (zoom + 1) - 1, iy), (128, 128, 128, 255))

    with io.BytesIO() as bio:
        grid_img.save(bio, format="PNG")
        bio.seek(0)
        f = discord.File(bio, "gridded.png")
        await ctx.send(file=f)


async def fetch_pixelcanvas(x, y, dx, dy):
    fetched = Image.new('RGB', (dx, dy), (255, 255, 255))
    ch_off = Coords(x % 64, y % 64)
    bc = Coords(x // 64 + 7, y // 64 + 7)
    bc_ext = Coords((dx + ch_off.x) // 960 + 1, (dy + ch_off.y) // 960 + 1)

    data = bytes()
    async with aiohttp.ClientSession() as session:
        for iy in range(0, bc_ext.y * 15, 15):
            for ix in range(0, bc_ext.x * 15, 15):
                url = "http://pixelcanvas.io/api/bigchunk/{0}.{1}.bmp".format(bc.x + ix, bc.y + iy)
                headers = {"Accept-Encoding": "gzip"}
                async with session.get(url, headers=headers) as resp:
                    data += await resp.read()

    def pixel_to_data_index():
        scan = Coords(ch_off.x + px, ch_off.y + py)
        return (921600 * (bc_ext.x-1) * (scan.y // 960)  # Skips rows of big chunks
                + 921600 * (scan.x // 960)           # Skips single big chunks in a row
                + 4096 * 15 * (scan.y // 64)         # Skips rows of chunks in the big chunk
                + 4096 * ((scan.x % 960) // 64)      # Skips single chunk in the row
                + 64 * (scan.y % 64)                 # Skips rows of pixels in the chunk
                + (scan.x % 64)                      # Skips single pixels in the row
                ) / 2                                # Pixels come packed in pairs

    for py in range(dy):
        await asyncio.sleep(0)
        for px in range(dx):
            i = pixel_to_data_index()
            color_id = data[int(i)] & 15 if i % 1 != 0 else data[int(i)] >> 4
            color = colors.pixelcanvas[color_id] + (255,)
            fetched.putpixel((px, py), color)

    return fetched


async def fetch_pixelzio(x, y, dx, dy):
    chk = Coords((x // 500) * 500, (y // 500) * 500)
    ext = Coords((x + dx) // 500 - x // 500 + 1, (y + dy) // 500 - y // 500 + 1)
    fetched = Image.new('RGB', (500 * ext.x, 500 * ext.y))

    async with aiohttp.ClientSession() as session:
        for iy in range(0, ext.y * 500, 500):
            for ix in range(0, ext.x * 500, 500):
                url = "http://pixelz.io/api/{0}_{1}/img".format(chk.x + ix, chk.y + iy)
                headers = {"Accept-Encoding": "gzip"}
                async with session.get(url, headers=headers) as resp:
                    data = await resp.read()
                    tmp = Image.open(io.BytesIO(data)).convert('RGB')
                    fetched.paste(tmp, (ix, iy, ix + 500, iy + 500))

    return fetched.crop((x % 500, y % 500, (x % 500) + dx, (y % 500) + dy))


async def fetch_pixelzone(x, y, dx, dy):
    x = x + 4096
    y = y + 4096
    ext = Coords((x + dx) // 512 - x // 512 + 1, (y + dy) // 512 - y // 512 + 1)
    chk = Coords(x // 512, y // 512)
    fetched = Image.new('RGB', (512 * ext.x, 512 * ext.y))

    url = "{0}://pixelzone.io/socket.io/?EIO=3&transport={1}"
    pkts_expected = 0
    async with aiohttp.ClientSession() as session:
        async with session.get(url.format("http", "polling")) as r:
            sid = json.loads(str((await r.read())[5:], "utf-8"))['sid']
    async with websockets.connect(url.format("ws", "websocket&sid=") + sid) as ws:
        await ws.send("2probe")
        await ws.recv()
        await ws.send("5")
        await ws.recv()
        for iy in range(ext.y):
            for ix in range(ext.x):
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
        chk_abs = Coords(data['cx'], data['cy'])
        chk_rel = Coords(chk_abs.x - chk.x, chk_abs.y - chk.y)
        tmp = LZString().decompressFromBase64(data['data'])
        tmp = json.loads("[" + tmp + "]")
        tmp = lz4.frame.decompress(bytes(tmp))
        chunk = Image.new('RGB', (512, 512), (255, 255, 255, 255))
        for py in range(chunk.height):
            await asyncio.sleep(0)
            for px in range(chunk.width):
                i = (py * 512 + px) / 2
                color_id = tmp[int(i)] & 15 if i % 1 == 0 else tmp[int(i)] >> 4
                color = colors.pixelzone[color_id]
                chunk.putpixel((px, py), color)
        fetched.paste(chunk, (chk_rel.x * 512, chk_rel.y * 512, (chk_rel.x + 1) * 512, (chk_rel.y + 1) * 512))

    return fetched.crop((x % 512, y % 512, (x % 512) + dx, (y % 512) + dy))


async def fetch_pxlsspace(x, y, dx, dy):
    fetched = Image.new('RGB', (dx, dy), colors.pxlsspace[1])

    async with aiohttp.ClientSession() as session:
        url = "http://pxls.space/boarddata?={0:.0f}".format(time.time())
        headers = {"Accept-Encoding": "gzip"}
        async with session.get(url, headers=headers) as resp:
            data = await resp.read()

    for py in range(dy):
        await asyncio.sleep(0)
        for px in range(dx):
            if 1280 <= px+x or px+x < 0 or 720 <= py+y or py+y < 0:
                continue
            i = 1280 * (py+y) + (px+x)
            color_id = data[i]
            color = colors.pxlsspace[color_id]
            fetched.putpixel((px, py), color)

    return fetched
