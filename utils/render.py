import aiohttp
import discord
import os
from PIL import Image
from time import time

from utils.logger import Log
from utils.config import Config

cfg = Config()
log = Log(__name__)
main_url = 'http://pixelcanvas.io/api/bigchunk/'
exp_url = 'http://experimental.pixelcanvas.io/api/bigchunk/'
colors = [
    (255, 255, 255),  # White
    (228, 228, 228),  # Light Grey
    (136, 136, 136),  # Dark Grey
    ( 34,  34,  34),  # Black
    (255, 167, 209),  # Pink
    (229,   0,   0),  # Red
    (229, 149,   0),  # Orange
    (160, 106,  66),  # Brown
    (229, 217,   0),  # Yellow
    (148, 224,  68),  # Light Green
    (  2, 190,   1),  # Green
    (  0, 211, 221),  # Cyan
    (  0, 131, 199),  # Teal
    (  0,   0, 234),  # Blue
    (207, 110, 228),  # Light Purple
    (130,   0, 128)   # Purple
]


# Helper class to store coordinate pairs
class Coords:
    def __init__(self, x, y):
        self.x = x
        self.y = y


async def preview(ctx, x, y, zoom, is_experimental):
    log.debug("Preview invoked by {0.name}#{0.discriminator} (ID: {0.id}) in {1.name} (ID: {1.id})"
              .format(ctx.author, ctx.guild))

    log.debug("X:{0} | Y:{1} | Zoom:{2} | IsExp: {3}".format(x, y, zoom, is_experimental))

    # Coordinates of the template's top-left pixel with respect to the canvas
    tlp = Coords(x - int(cfg.preview_w // 2), y - int(cfg.preview_h // 2))
    # Offset of tlp from the top-left pixel of the chunk it is in
    ch_off = Coords(tlp.x % 64, tlp.y % 64)
    # Chunk coordinates of the big chunk that has tlp in its top left chunk
    bc = Coords(int(tlp.x // 64) + 7, int(tlp.y // 64) + 7)
    # Offset between tlp and the top-left pixel of where the preview should render from due to zooming
    z_off = Coords((cfg.preview_w / 2) * (1 - 1 / zoom), (cfg.preview_h / 2) * (1 - 1 / zoom))

    async with aiohttp.ClientSession() as session:
        url = main_url if not is_experimental else exp_url
        async with session.get("{0}{1}.{2}.bmp".format(url, bc.x, bc.y)) as resp:
            data = await resp.read()

    # The second and fourth loops will repeat rows and columns to simulate magnification if zoom > 1
    preview_img = Image.new('RGBA', (cfg.preview_w, cfg.preview_h), (255, 255, 255, 255))
    for py in range(preview_img.height // zoom):
        for ry in range(zoom):
            for px in range(preview_img.width // zoom):
                for rx in range(zoom):
                    pixel = Coords(px * zoom + rx, py * zoom + ry)
                    i = __get_pixel_offset(ch_off, py, px, z_off)
                    color_id = data[int(i)] & 15 if i % 1 != 0 else data[int(i)] >> 4
                    color = colors[color_id] + (255,)
                    preview_img.putpixel((pixel.x, pixel.y), color)

    preview_filename = 'preview_{0}.png'.format(int(time()))
    with open(preview_filename, 'wb') as f:
        preview_img.save(f, 'png')
    f = discord.File(preview_filename, "preview.png")
    await ctx.channel.send(file=f)
    os.remove(preview_filename)


async def diff(ctx, top_left_x, top_left_y, att, is_experimental):
    log.debug("Preview invoked by {0.name}#{0.discriminator} (ID: {0.id}) in {1.name} (ID: {1.id})"
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
        url = main_url if not is_experimental else exp_url
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
            i = __get_pixel_offset(ch_off, py, px, bc_ext=bc_ext)
            color_id = data[int(i)] & 15 if i % 1 != 0 else data[int(i)] >> 4
            color = colors[color_id]

            tp = template.getpixel((px, py))
            if tp[3] is not 0:
                # All non-transparent pixels count to the total
                tot += 1
            if 0 < tp[3] < 255 or (tp[3] is 255 and tp[:3] not in colors):
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


def __get_pixel_offset(ch_off, y, x, z_off=Coords(0, 0), bc_ext=Coords(1, 1)):
    scan = Coords(ch_off.x + z_off.x + x, ch_off.y + z_off.y + y)
    return (921600 * bc_ext.x * (scan.y // 960)  # Skips rows of big chunks
            + 921600 * (scan.x // 960)           # Skips single big chunks in a row
            + 4096 * 15 * (scan.y // 64)         # Skips rows of chunks in the big chunk
            + 4096 * ((scan.x % 960) // 64)      # Skips single chunk in the row
            + 64 * (scan.y % 64)                 # Skips rows of pixels in the chunk
            + (scan.x % 64)                      # Skips single pixels in the row
            ) / 2                                # Pixels come packed in pairs
