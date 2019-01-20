import asyncio
import io
import json
from time import time

import aiohttp
import cfscrape
import websockets
from typing import Iterable

from objects import errors, logger
from objects.chunks import BigChunk, ChunkPzi, ChunkPz, PxlsBoard
from objects.config import Config


cfg = Config()
log = logger.Log(__name__)


async def fetch_chunks(chunks: Iterable):
    c = next(iter(chunks))
    if type(c) is BigChunk:
        await _fetch_chunks_pixelcanvas(chunks)
    elif type(c) is ChunkPzi:
        await _fetch_chunks_pixelzio(chunks)
    elif type(c) is ChunkPz:
        await _fetch_chunks_pixelzone(chunks)
    else:
        await _fetch_pxlsspace(chunks)


async def _fetch_chunks_pixelcanvas(bigchunks: Iterable[BigChunk]):
    async with aiohttp.ClientSession() as session:
        for bc in bigchunks:
            await asyncio.sleep(0)
            if not bc.is_in_bounds():
                continue
            data = None
            attempts = 0
            while attempts < 3:
                try:
                    async with session.get(bc.url) as resp:
                        data = await resp.read()
                        if len(data) == 460800:
                            break
                except aiohttp.ClientPayloadError:
                    pass
                data = None
                attempts += 1
            if not data:
                raise errors.HttpCanvasError('pixelcanvas')
            bc.load(data)


async def _fetch_chunks_pixelzio(chunks: Iterable[ChunkPzi]):
    async with cfscrape.create_scraper_async() as session:
        for ch in chunks:
            await asyncio.sleep(0)
            if not ch.is_in_bounds():
                continue
            async with session.get(ch.url) as resp:
                ch.load(await resp.read())


async def _fetch_chunks_pixelzone(chunks: Iterable[ChunkPz]):
    socket_url = "{0}://pixelzone.io/socket.io/?EIO=3&transport={1}"
    sid = None
    chunks = [x for x in chunks if x.is_in_bounds()]
    if len(chunks) == 0:
        return
    async with aiohttp.ClientSession() as session:
        attempts = 0
        while attempts < 3:
            try:
                async with session.get(socket_url.format("http", "polling"), headers={'User-Agent': 'Python/3.6 aiohttp/3.2.0'}) as r:
                    sid = json.loads(str((await r.read())[4:-4], "utf-8"))['sid']
                    break
            except aiohttp.client_exceptions.ClientOSError:
                attempts += 1
    if not sid:
        raise errors.HttpCanvasError('pixelzone')
    async with websockets.connect(socket_url.format("ws", "websocket&sid=") + sid, extra_headers={'User-Agent': 'Python/3.6 aiohttp/3.2.0'}) as ws:
        await ws.send("2probe")
        await ws.recv()
        await ws.send("5")
        await ws.recv()
        await ws.send("42['useAPI', '{}'".format(cfg.pz_api_key))
        try:
            for ch in chunks:
                data = {}
                await ws.send(ch.url)
                async for msg in ws:
                    d = json.loads(msg[msg.find('['):])
                    if type(d) == int:
                        continue
                    if d[0] == "c":
                        data = d[1]
                        break
                ch = next((x for x in chunks if x.x == data['cx'] and x.y == data['cy']))
                ch.load(data['data'])
        except websockets.ConnectionClosed as e:
            raise errors.HttpCanvasError('pixelzone')


async def _fetch_pxlsspace(chunks: Iterable[PxlsBoard]):
    board = next(iter(chunks))
    async with aiohttp.ClientSession() as session:
        async with session.get("http://pxls.space/info") as resp:
            info = json.loads(await resp.read())
        board.set_board_info(info)

        async with session.get("http://pxls.space/boarddata?={0:.0f}".format(time())) as resp:
            board.load(await resp.read())


async def fetch_online_pixelcanvas():
    async with aiohttp.ClientSession() as sess:
        async with sess.get("http://pixelcanvas.io/api/online") as resp:
            if resp.status != 200:
                raise errors.HttpGeneralError
            data = json.loads(await resp.read())
            return data['online']


async def fetch_online_pixelzone():
    socket_url = "{0}://pixelzone.io/socket.io/?EIO=3&transport={1}"
    sid = None
    async with aiohttp.ClientSession() as session:
        attempts = 0
        while attempts < 3:
            try:
                async with session.get(socket_url.format("http", "polling"),
                                       headers={'User-Agent': 'Python/3.6 aiohttp/3.2.0'}) as r:
                    sid = json.loads(str((await r.read())[4:-4], "utf-8"))['sid']
                    break
            except aiohttp.client_exceptions.ClientOSError:
                attempts += 1
    if not sid:
        raise errors.HttpCanvasError('pixelzone')
    async with websockets.connect(socket_url.format("ws", "websocket&sid=") + sid,
                                  extra_headers={'User-Agent': 'Python/3.6 aiohttp/3.2.0'}) as ws:
        await ws.send("2probe")
        await ws.recv()
        await ws.send("5")
        await ws.recv()
        await ws.send("42['useAPI', '{}'".format(cfg.pz_api_key))
        try:
            async for msg in ws:
                d = json.loads(msg[msg.find('['):])
                if type(d) == int:
                    continue
                if d[0] == "g":
                    data = d[1]
                    break
        except websockets.ConnectionClosed as e:
            raise errors.HttpCanvasError('pixelzone')
    return data


async def fetch_online_pxlsspace():
    async with websockets.connect("wss://pxls.space/ws") as ws:
        async for msg in ws:
            d = json.loads(msg)
            if d['type'] == 'users':
                return d['count']


async def get_changelog(version):
    url = "https://api.github.com/repos/DiamondIceNS/StarlightGlimmer/releases"
    async with aiohttp.ClientSession() as sess:
        async with sess.get(url) as resp:
            if resp.status != 200:
                raise errors.HttpGeneralError
            data = json.loads(await resp.read())
            return next((x for x in data if x['tag_name'] == "v{}".format(version)), None)


async def get_template(url):
    async with aiohttp.ClientSession() as sess:
        async with sess.get(url) as resp:
            if resp.status != 200:
                raise errors.TemplateHttpError
            if resp.content_type == "image/jpg" or resp.content_type == "image/jpeg":
                raise errors.NoJpegsError
            if resp.content_type != "image/png":
                raise errors.NotPngError
            return io.BytesIO(await resp.read())
