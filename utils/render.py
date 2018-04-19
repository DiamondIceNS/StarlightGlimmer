import aiohttp
import discord
import io
import json
import lz4.frame
import os
from math import sqrt, pow
from PIL import Image
from socketIO_client import SocketIO
from time import time

from utils.config import Config
from utils.colors import *
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


# Pixelzone requires a unique architecture due to its use of Socket.io
class SIOConn:
    def __init__(self):
        self.socket = SocketIO('http://pixelzone.io')
        self.socket.on('chunkData', self.on_chunkdata)
        self.chk = None
        self.fetched = None
        self.callbacks = 0

    def fetch(self, x, y, dx, dy):
        tlp = Coords(x + 4096, y + 4096)
        ch_off = Coords(tlp.x % 512, tlp.y % 512)
        ext = Coords((tlp.x + dx) // 512 - tlp.x // 512 + 1, (tlp.y + dy) // 512 - tlp.y // 512 + 1)
        self.chk = Coords(tlp.x // 512, tlp.y // 512)
        self.fetched = Image.new('RGB', (512 * ext.x, 512 * ext.y))

        for iy in range(ext.y):
            for ix in range(ext.x):
                self.socket.emit('getChunkData', {"cx": self.chk.x + ix, "cy": self.chk.y + iy})

        expected_callbacks = ext.x * ext.y
        while self.callbacks < expected_callbacks:
            self.socket.wait(seconds=1)
        self.socket.disconnect()

        self.fetched = self.fetched.crop((ch_off.x, ch_off.y, ch_off.x + dx, ch_off.y + dy))

    def on_chunkdata(self, data):
        chk_abs = Coords(data['cx'], data['cy'])
        chk_rel = Coords(chk_abs.x - self.chk.x, chk_abs.y - self.chk.y)
        tmp = LZString().decompressFromBase64(data['data'])
        tmp = json.loads("[" + tmp + "]")
        tmp = lz4.frame.decompress(bytes(tmp))
        chunk = Image.new('RGB', (512, 512), (255, 255, 255, 255))
        for py in range(chunk.height):
            for px in range(chunk.width):
                i = (py * 512 + px) / 2
                color_id = tmp[int(i)] & 15 if i % 1 == 0 else tmp[int(i)] >> 4
                color = pzone_colors[color_id]
                chunk.putpixel((px, py), color)
        self.fetched.paste(chunk, (chk_rel.x * 512, chk_rel.y * 512, (chk_rel.x + 1) * 512, (chk_rel.y + 1) * 512))
        self.callbacks += 1

    async def preview(self, ctx, x, y, zoom):
        async with ctx.typing():
            log.debug("X:{0} | Y:{1} | Zoom:{2}".format(x, y, zoom))

            self.fetch(x - cfg.preview_w // 2, y - cfg.preview_h // 2, cfg.preview_w, cfg.preview_h)

            if zoom > 1:
                self.fetched = self.fetched.resize(tuple(zoom * x for x in self.fetched.size), Image.NEAREST)
                tlp_z = Coords(self.fetched.width // 2 - cfg.preview_w // 2,
                               self.fetched.height // 2 - cfg.preview_h // 2)
                self.fetched = self.fetched.crop((tlp_z.x, tlp_z.y, tlp_z.x + cfg.preview_w, tlp_z.y + cfg.preview_h))

            preview_filename = 'preview_{0}.png'.format(int(time()))
            with open(preview_filename, 'wb') as f:
                self.fetched.save(f, 'png')
            f = discord.File(preview_filename, "preview.png")
            await ctx.channel.send(file=f)
            os.remove(preview_filename)

    async def diff(self, ctx, x, y, att, zoom):
        async with ctx.typing():
            self.fetch(x, y, att.width, att.height)

            template_filename = 'template_{0}.png'.format(int(time()))
            with open(template_filename, 'wb') as f:
                await att.save(f)
            template = Image.open(template_filename).convert('RGBA')
            os.remove(template_filename)

            log.debug("X:{0} | Y:{1} | Dim: {2}x{3} | Zoom: {4}".format(x, y, template.width, template.height, zoom))

            if template.width * template.height > 1000000:
                await ctx.channel.send(getlang(ctx.guild.id, "render.large_template"))

            tot = 0  # Total non-transparent pixels in template
            err = 0  # Number of errors
            bad = 0  # Number of pixels in the template that are not in the Pixelcanvas color palette

            diff_img = Image.new('RGB', (att.width, att.height), (255, 255, 255))
            for py in range(diff_img.height):
                for px in range(diff_img.width):
                    tp = template.getpixel((px, py))
                    dp = self.fetched.getpixel((px, py))
                    if tp[3] is not 0:
                        # All non-transparent pixels count to the total
                        tot += 1
                    if 0 < tp[3] < 255 or (tp[3] is 255 and tp[:3] not in pzone_colors):
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

            diff_filename = 'diff_{0}.png'.format(int(time()))
            with open(diff_filename, 'wb') as f:
                diff_img.save(f, 'png')
            f = discord.File(diff_filename, "diff.png")
            if bad > 0:
                content = getlang(ctx.guild.id, "render.diff_bad_color") \
                    .format(tot - err, tot, err, bad, 100 * (tot - err) / tot)
            else:
                content = getlang(ctx.guild.id, "render.diff").format(tot - err, tot, err, 100 * (tot - err) / tot)
            await ctx.channel.send(content=content, file=f)
            os.remove(diff_filename)


async def diff(ctx, x, y, att, zoom, fetch, colors):
    async with ctx.typing():
        template_filename = 'template_{0}.png'.format(int(time()))
        with open(template_filename, 'wb') as f:
            await att.save(f)
        template = Image.open(template_filename).convert('RGBA')
        os.remove(template_filename)

        log.debug("X:{0} | Y:{1} | Dim: {2}x{3} | Zoom: {4}".format(x, y, template.width, template.height, zoom))

        if template.width * template.height > 1000000:
            await ctx.channel.send(getlang(ctx.guild.id, "render.large_template"))

        diff_img = await fetch(x, y, template.width, template.height)

        tot = 0  # Total non-transparent pixels in template
        err = 0  # Number of errors
        bad = 0  # Number of pixels in the template that are not in the color palette

        for py in range(template.height):
            for px in range(template.width):
                tp = template.getpixel((px, py))
                dp = diff_img.getpixel((px, py))
                if tp[3] is not 0:
                    # All non-transparent pixels count to the total
                    tot += 1
                if 0 < tp[3] < 255 or (tp[3] is 255 and tp[:3] not in colors):
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

        diff_filename = 'diff_{0}.png'.format(int(time()))
        with open(diff_filename, 'wb') as f:
            diff_img.save(f, 'png')
        f = discord.File(diff_filename, "diff.png")
        if bad > 0:
            content = getlang(ctx.guild.id, "render.diff_bad_color")\
                .format(tot - err, tot, err, bad, 100 * (tot - err) / tot)
        else:
            content = getlang(ctx.guild.id, "render.diff").format(tot - err, tot, err, 100 * (tot - err) / tot)
        await ctx.channel.send(content=content, file=f)
        os.remove(diff_filename)


async def preview(ctx, x, y, zoom, fetch):
    async with ctx.typing():
        log.debug("X:{0} | Y:{1} | Zoom:{2}".format(x, y, zoom))

        preview_img = await fetch(x - cfg.preview_w // 2, y - cfg.preview_h // 2, cfg.preview_w, cfg.preview_h)

        if zoom > 1:
            preview_img = preview_img.resize(tuple(zoom * x for x in preview_img.size), Image.NEAREST)
            tlp_z = Coords(preview_img.width // 2 - cfg.preview_w // 2, preview_img.height // 2 - cfg.preview_h // 2)
            preview_img = preview_img.crop((tlp_z.x, tlp_z.y, tlp_z.x + cfg.preview_w, tlp_z.y + cfg.preview_h))

        preview_filename = 'preview_{0}.png'.format(int(time()))
        with open(preview_filename, 'wb') as f:
            preview_img.save(f, 'png')
        f = discord.File(preview_filename, "preview.png")
        await ctx.channel.send(file=f)
        os.remove(preview_filename)


async def quantize(ctx, att, colors):
    template_filename = 'template_{0}.png'.format(int(time()))
    with open(template_filename, 'wb') as f:
        await att.save(f)
    template = Image.open(template_filename).convert('RGBA')
    os.remove(template_filename)

    log.debug("Dim: {0}x{1}".format(template.width, template.height))

    bad_pixels = template.height * template.width
    for py in range(template.height):
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
            for c in colors:
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

    quantized_filename = 'cq_{0}.png'.format(int(time()))
    with open(quantized_filename, 'wb') as f:
        template.save(f, 'png')
    f = discord.File(quantized_filename, att.filename)
    await ctx.channel.send(getlang(ctx.guild.id, "render.quantize").format(bad_pixels), file=f)
    os.remove(quantized_filename)


async def fetch_pixelcanvas(x, y, dx, dy):
    fetched = Image.new('RGB', (dx, dy), (255, 255, 255))
    ch_off = Coords(x % 64, y % 64)
    bc = Coords(x // 64 + 7, y // 64 + 7)
    bc_ext = Coords((dx + ch_off.x) // 960 + 1, (dy + ch_off.y) // 960 + 1)

    async with aiohttp.ClientSession() as session:
        for iy in range(0, bc_ext.y * 15, 15):
            for ix in range(0, bc_ext.x * 15, 15):
                url = "http://pixelcanvas.io/api/bigchunk/{0}.{1}.bmp".format(bc.x + ix, bc.y + iy)
                headers = {"Accept-Encoding": "gzip"}
                async with session.get(url, headers=headers) as resp:
                    data = await resp.read()

    def pixel_to_data_index():
        scan = Coords(ch_off.x + px, ch_off.y + py)
        return (921600 * bc_ext.x * (scan.y // 960)  # Skips rows of big chunks
                + 921600 * (scan.x // 960)           # Skips single big chunks in a row
                + 4096 * 15 * (scan.y // 64)         # Skips rows of chunks in the big chunk
                + 4096 * ((scan.x % 960) // 64)      # Skips single chunk in the row
                + 64 * (scan.y % 64)                 # Skips rows of pixels in the chunk
                + (scan.x % 64)                      # Skips single pixels in the row
                ) / 2                                # Pixels come packed in pairs

    for py in range(dy):
        for px in range(dx):
            i = pixel_to_data_index()
            color_id = data[int(i)] & 15 if i % 1 != 0 else data[int(i)] >> 4
            color = pc_colors[color_id] + (255,)
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
