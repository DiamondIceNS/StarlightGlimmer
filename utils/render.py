import aiohttp
import discord
import os
import io
from PIL import Image
from time import time

from utils.logger import Log
from utils.config import Config
from utils.constants import *

cfg = Config()
log = Log(__name__)


# Helper class to store coordinate pairs
class Coords:
    def __init__(self, x, y):
        self.x = x
        self.y = y


async def pixelcanvasio_preview(ctx, x, y, zoom, is_experimental):
    async with ctx.typing():
        log.debug("Pixelcanvas preview invoked by {0.name}#{0.discriminator} (ID: {0.id}) in {1.name} (ID: {1.id})"
                  .format(ctx.author, ctx.guild))

        log.debug("X:{0} | Y:{1} | Zoom:{2} | IsExp: {3}".format(x, y, zoom, is_experimental))

        # Coordinates of the template's top-left pixel with respect to the canvas
        tlp = Coords(x - int(cfg.preview_w // 2), y - int(cfg.preview_h // 2))
        # Offset of tlp from the top-left pixel of the chunk it is in
        ch_off = Coords(tlp.x % 64, tlp.y % 64)
        # Chunk coordinates of the big chunk that has tlp in its top left chunk
        bc = Coords(int(tlp.x // 64) + 7, int(tlp.y // 64) + 7)
        # Offset between tlp and the top-left pixel of where the preview should render from due to zooming
        # z_off = Coords((cfg.preview_w / 2) * (1 - 1 / zoom), (cfg.preview_h / 2) * (1 - 1 / zoom))

        async with aiohttp.ClientSession() as session:
            url = pc_url_main if not is_experimental else pc_url_exp
            async with session.get("{0}{1}.{2}.bmp".format(url, bc.x, bc.y)) as resp:
                data = await resp.read()

        # The second and fourth loops will repeat rows and columns to simulate magnification if zoom > 1
        preview_img = Image.new('RGBA', (cfg.preview_w, cfg.preview_h), (255, 255, 255, 255))
        for py in range(preview_img.height):
            for px in range(preview_img.width):
                i = __get_pixelcanvas_pixel_offset(ch_off, py, px)
                color_id = data[int(i)] & 15 if i % 1 != 0 else data[int(i)] >> 4
                color = pc_colors[color_id] + (255,)
                preview_img.putpixel((px, py), color)

        if zoom > 1:
            preview_img = preview_img.resize(tuple(zoom*x for x in preview_img.size), Image.NEAREST)
            tlp_z = Coords(preview_img.width//2-cfg.preview_w//2, preview_img.height//2-cfg.preview_h//2)
            preview_img = preview_img.crop((tlp_z.x, tlp_z.y, tlp_z.x+cfg.preview_w, tlp_z.y+cfg.preview_h))

        preview_filename = 'preview_{0}.png'.format(int(time()))
        with open(preview_filename, 'wb') as f:
            preview_img.save(f, 'png')
        f = discord.File(preview_filename, "preview.png")
        await ctx.channel.send(file=f)
        os.remove(preview_filename)


async def pixelcanvasio_diff(ctx, top_left_x, top_left_y, att, is_experimental):
    async with ctx.typing():
        log.debug("Pixelcanvas diff invoked by {0.name}#{0.discriminator} (ID: {0.id}) in {1.name} (ID: {1.id})"
                  .format(ctx.author, ctx.guild))

        template_filename = 'template_{0}.png'.format(int(time()))
        with open(template_filename, 'wb') as f:
            await att.save(f)
        template = Image.open(template_filename).convert('RGBA')
        os.remove(template_filename)

        log.debug("X:{0} | Y:{1} | Dim: {2}x{3} | IsExp: {4}"
                  .format(top_left_x, top_left_y, template.width, template.height, is_experimental))

        # Coordinates of the template's top-left pixel with respect to the canvas
        tlp = Coords(top_left_x, top_left_y)
        # Offset of tlp from the top-left pixel of the chunk it is in
        ch_off = Coords(tlp.x % 64, tlp.y % 64)
        # Chunk coordinates of the big chunk that has tlp in its top left chunk
        bc = Coords(int(tlp.x // 64) + 7, int(tlp.y // 64) + 7)
        # Number of extra big chunks spanned by the image after the initial top-left one
        bc_ext = Coords(int((template.width + ch_off.x) // 960), int((template.height + ch_off.y) // 960))

        if bc_ext.x > 0 or bc_ext.y > 0:
            await ctx.channel.send("(Processing large template, this might take a few seconds...)")

        async with aiohttp.ClientSession() as session:
            url = pc_url_main if not is_experimental else pc_url_exp
            data = bytes()
            for bcy in range(bc_ext.y + 1):
                for bcx in range(bc_ext.x + 1):
                    async with session.get("{0}{1}.{2}.bmp".format(url, bc.x + 15 * bcx, bc.y + 15 * bcy)) as resp:
                        data += await resp.read()

        tot = 0  # Total non-transparent pixels in template
        err = 0  # Number of errors
        bad = 0  # Number of pixels in the template that are not in the Pixelcanvas color palette

        diff_img = Image.new('RGBA', (template.width, template.height), (255, 255, 255, 255))
        for py in range(diff_img.height):
            for px in range(diff_img.width):
                i = __get_pixelcanvas_pixel_offset(ch_off, py, px, bc_ext=bc_ext)
                color_id = data[int(i)] & 15 if i % 1 != 0 else data[int(i)] >> 4
                color = pc_colors[color_id]

                tp = template.getpixel((px, py))
                if tp[3] is not 0:
                    # All non-transparent pixels count to the total
                    tot += 1
                if 0 < tp[3] < 255 or (tp[3] is 255 and tp[:3] not in pc_colors):
                    # All non-opaque and non-transparent pixels, and opaque pixels of bad colors, are bad
                    pixel = (0, 0, 255, 255)
                    err += 1
                    bad += 1
                elif tp[3] is 255 and (tp[0] is not color[0] or tp[1] is not color[1] or tp[2] is not color[2]):
                    # All pixels that are valid and opaque but do not match the canvas are wrong
                    pixel = (255, 0, 0, 255)
                    err += 1
                else:
                    # Render all correct/irrelevant pixels in greyscale
                    avg = round(color[0] * 0.3 + color[1] * 0.52 + color[2] * 0.18)
                    pixel = (avg, avg, avg, 255)

                diff_img.putpixel((px, py), pixel)
                # if bad/tot > 0.75:
                #     return

        diff_filename = 'diff_{0}.png'.format(int(time()))
        with open(diff_filename, 'wb') as f:
            diff_img.save(f, 'png')
        f = discord.File(diff_filename, "diff.png")
        if bad > 0:
            content = "{0}/{1} | {2} errors | {3} bad color | {4:.2f}% complete"\
                .format(tot - err, tot, err, bad, 100 * (tot - err) / tot)
        else:
            content = "{0}/{1} | {2} errors | {3:.2f}% complete".format(tot - err, tot, err, 100 * (tot - err) / tot)
        await ctx.channel.send(content=content, file=f)
        os.remove(diff_filename)


def __get_pixelcanvas_pixel_offset(ch_off, y, x, bc_ext=Coords(1, 1)):
    scan = Coords(ch_off.x + x, ch_off.y + y)
    return (921600 * bc_ext.x * (scan.y // 960)  # Skips rows of big chunks
            + 921600 * (scan.x // 960)           # Skips single big chunks in a row
            + 4096 * 15 * (scan.y // 64)         # Skips rows of chunks in the big chunk
            + 4096 * ((scan.x % 960) // 64)      # Skips single chunk in the row
            + 64 * (scan.y % 64)                 # Skips rows of pixels in the chunk
            + (scan.x % 64)                      # Skips single pixels in the row
            ) / 2                                # Pixels come packed in pairs


async def pixelzio_preview(ctx, x, y, zoom):
    async with ctx.typing():
        # Coordinates of the template's top-left pixel with respect to the canvas
        tlp = Coords(x - int(cfg.preview_w // 2), y - int(cfg.preview_h // 2))
        extension = Coords((tlp.x + cfg.preview_w) // 500 - tlp.x // 500, (tlp.y + cfg.preview_h) // 500 - tlp.y // 500)

        async with aiohttp.ClientSession() as session:
            uncropped_preview = Image.new('RGB', (500*(extension.x+1), 500*(extension.y+1)))
            for iy in range(extension.y + 1):
                for ix in range(extension.x + 1):
                    async with session.get("{0}{1}_{2}/img".format(pixelz_url, (tlp.x // 500 + ix) * 500,
                                                                   (tlp.y // 500 + iy) * 500)) as resp:
                        data = await resp.read()
                        tmp = Image.open(io.BytesIO(data)).convert('RGB')
                        uncropped_preview.paste(tmp, (ix*500, iy*500, (ix*500)+500, (iy*500)+500))

        preview = uncropped_preview.crop((tlp.x % 500, tlp.y % 500, (tlp.x % 500) + cfg.preview_w,
                                          (tlp.y % 500) + cfg.preview_h))
        if zoom > 1:
            preview = preview.resize(tuple(zoom*x for x in preview.size), Image.NEAREST)
            tlp_z = Coords(preview.width//2-cfg.preview_w//2, preview.height//2-cfg.preview_h//2)
            preview = preview.crop((tlp_z.x, tlp_z.y, tlp_z.x+cfg.preview_w, tlp_z.y+cfg.preview_h))

        preview_filename = 'preview_{0}.png'.format(int(time()))
        with open(preview_filename, 'wb') as f:
            preview.save(f, 'png')
        f = discord.File(preview_filename, "preview.png")
        await ctx.channel.send(file=f)
        os.remove(preview_filename)


async def pixelzio_diff(ctx, top_left_x, top_left_y, att):
    async with ctx.typing():
        log.debug("Pixelz.io preview invoked by {0.name}#{0.discriminator} (ID: {0.id}) in {1.name} (ID: {1.id})"
                  .format(ctx.author, ctx.guild))

        template_filename = 'template_{0}.png'.format(int(time()))
        with open(template_filename, 'wb') as f:
            await att.save(f)
        template = Image.open(template_filename).convert('RGBA')
        os.remove(template_filename)

        log.debug("X:{0} | Y:{1} | Dim: {2}x{3}"
                  .format(top_left_x, top_left_y, template.width, template.height))

        # Coordinates of the template's top-left pixel with respect to the canvas
        tlp = Coords(top_left_x, top_left_y)
        # # Number of extra big chunks spanned by the image after the initial top-left one
        bc_ext = Coords((tlp.x + template.width) // 500 - tlp.x // 500, (tlp.y + template.height) // 500 - tlp.y // 500)

        if bc_ext.x > 1 or bc_ext.y > 1:
            await ctx.channel.send("(Processing large template, this might take a few seconds...)")

        async with aiohttp.ClientSession() as session:
            uncropped_preview = Image.new('RGB', (500*(bc_ext.x+1), 500*(bc_ext.y+1)))
            for iy in range(bc_ext.y + 1):
                for ix in range(bc_ext.x + 1):
                    async with session.get("{0}{1}_{2}/img".format(pixelz_url, (tlp.x // 500 + ix) * 500,
                                                                   (tlp.y // 500 + iy) * 500)) as resp:
                        data = await resp.read()
                        tmp = Image.open(io.BytesIO(data)).convert('RGB')
                        uncropped_preview.paste(tmp, (ix*500, iy*500, (ix*500)+500, (iy*500)+500))

        tot = 0  # Total non-transparent pixels in template
        err = 0  # Number of errors
        bad = 0  # Number of pixels in the template that are not in the Pixelcanvas color palette

        tlp_off = Coords(tlp.x % 500, tlp.y % 500)
        diff_img = Image.new('RGBA', (template.width, template.height), (255, 255, 255, 255))
        for py in range(diff_img.height):
            for px in range(diff_img.width):
                tp = template.getpixel((px, py))
                cp = uncropped_preview.getpixel((px + tlp_off.x, py + tlp_off.y))
                if tp[3] is not 0:
                    # All non-transparent pixels count to the total
                    tot += 1
                if 0 < tp[3] < 255 or (tp[3] is 255 and tp[:3] not in pixelz_colors):
                    # All non-opaque and non-transparent pixels, and opaque pixels of bad colors, are bad
                    pixel = (0, 0, 255, 255)
                    err += 1
                    bad += 1
                elif tp[3] is 255 and (tp[0] is not cp[0] or tp[1] is not cp[1] or tp[2] is not cp[2]):
                    # All pixels that are valid and opaque but do not match the canvas are wrong
                    pixel = (255, 0, 0, 255)
                    err += 1
                else:
                    # Render all correct/irrelevant pixels in greyscale
                    avg = round(cp[0] * 0.3 + cp[1] * 0.52 + cp[2] * 0.18)
                    pixel = (avg, avg, avg, 255)

                diff_img.putpixel((px, py), pixel)
                # if bad/tot > 0.75:
                #     return

        diff_filename = 'diff_{0}.png'.format(int(time()))
        with open(diff_filename, 'wb') as f:
            diff_img.save(f, 'png')
        f = discord.File(diff_filename, "diff.png")
        if bad > 0:
            content = "{0}/{1} | {2} errors | {3} bad color | {4:.2f}% complete"\
                .format(tot - err, tot, err, bad, 100 * (tot - err) / tot)
        else:
            content = "{0}/{1} | {2} errors | {3:.2f}% complete".format(tot - err, tot, err, 100 * (tot - err) / tot)
        await ctx.channel.send(content=content, file=f)
        os.remove(diff_filename)
