import asyncio
import io
import json
import logging
from time import time

import aiohttp
import websockets
from typing import Iterable

from objects.chunks import BigChunk, ChunkPz, PxlsBoard, ChunkPP
from objects.errors import HttpCanvasError, HttpGeneralError, NoJpegsError, NotPngError, TemplateHttpError
from utils import config
from utils.version import VERSION


log = logging.getLogger(__name__)

useragent = {'User-Agent': 'StarlightGlimmer/{} (+https://github.com/DiamondIceNS/StarlightGlimmer)'.format(VERSION), 'Cache-Control': 'no-cache'}


async def fetch_chunks(chunks: Iterable):
    c = next(iter(chunks))
    if type(c) is BigChunk:
        await _fetch_chunks_pixelcanvas(chunks)
    elif type(c) is ChunkPz:
        await _fetch_chunks_pixelzone(chunks)
    elif type(c) is PxlsBoard:
        await _fetch_pxlsspace(chunks)
    else:
        await _fetch_chunks_pixelplanet(chunks)


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
                    async with session.get(bc.url, headers=useragent) as resp:
                        data = await resp.read()
                        if len(data) == 460800:
                            break
                except aiohttp.ClientPayloadError:
                    pass
                data = None
                attempts += 1
            if not data:
                raise HttpCanvasError('pixelcanvas')
            bc.load(data)


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
                async with session.get(socket_url.format("https", "polling"), headers=useragent) as r:
                    sid = json.loads(str((await r.read())[4:-4], "utf-8"))['sid']
                    break
            except aiohttp.client_exceptions.ClientOSError:
                attempts += 1

        if not sid:
            raise HttpCanvasError('pixelzone')

        attempts = 0
        while attempts < 3:
            try:
                await session.post(socket_url.format("https", "polling") + "&sid=" + sid, data='11:42["hello"]',
                                   headers=useragent)
                break
            except aiohttp.client_exceptions.ClientOSError:
                attempts += 1

    async with websockets.connect(socket_url.format("wss", "websocket&sid=") + sid, extra_headers=useragent) as ws:
        try:
            await ws.send("2probe")
            await ws.recv() #3probe response
            await ws.send("5")
            await ws.send("42hello")
            await ws.recv() #welcome response
            await ws.send('42["useAPI", "{}"]'.format(config.PZ_API_KEY))
            await ws.recv() #useAPICallback response
            for ch in chunks:
                await ws.send(ch.url)
                packet = None
                async for msg in ws:
                    if packet is None:
                        if msg[:2] == '45': #binary data response
                            packet = {}
                            data = json.loads(msg[msg.find('-')+1:])[1]
                            packet['cx'] = data['cx']
                            packet['cy'] = data['cy']
                    else:
                        packet['data'] = msg[1:]
                        break
                ch = next((x for x in chunks if x.x == packet['cx'] and x.y == packet['cy']))
                ch.load(packet['data'])
        except websockets.ConnectionClosed as e:
            raise HttpCanvasError('pixelzone')


async def _fetch_pxlsspace(chunks: Iterable[PxlsBoard]):
    board = next(iter(chunks))
    async with aiohttp.ClientSession() as session:
        async with session.get("https://pxls.space/info", headers=useragent) as resp:
            info = json.loads(await resp.read())
        board.set_board_info(info)

        async with session.get("https://pxls.space/boarddata?={0:.0f}".format(time()), headers=useragent) as resp:
            board.load(await resp.read())


async def _fetch_chunks_pixelplanet(bigchunks: Iterable[ChunkPP]):
    async with aiohttp.ClientSession() as session:
        for bc in bigchunks:
            await asyncio.sleep(0)
            if not bc.is_in_bounds():
                continue
            data = None
            attempts = 0
            while attempts < 3:
                try:
                    async with session.get(bc.url, headers=useragent) as resp:
                        data = await resp.read()
                        if len(data) == 65536:
                            break
                except aiohttp.ClientPayloadError:
                    pass
                data = None
                attempts += 1
            if not data:
                raise HttpCanvasError('pixelplanet')
            bc.load(data)


async def fetch_online_pixelcanvas():
    async with aiohttp.ClientSession() as sess:
        async with sess.get("https://pixelcanvas.io/api/online", headers=useragent) as resp:
            if resp.status != 200:
                raise HttpGeneralError
            data = json.loads(await resp.read())
            return data['online']


async def fetch_online_pixelzone():
    socket_url = "{0}://pixelzone.io/socket.io/?EIO=3&transport={1}"
    sid = None
    async with aiohttp.ClientSession() as session:
        attempts = 0
        while attempts < 3:
            try:
                async with session.get(socket_url.format("http", "polling"), headers=useragent) as r:
                    sid = json.loads(str((await r.read())[4:-4], "utf-8"))['sid']
                    break
            except aiohttp.client_exceptions.ClientOSError:
                attempts += 1

        if not sid:
            raise HttpCanvasError('pixelzone')

        attempts = 0
        while attempts < 3:
            try:
                await session.post(socket_url.format("http", "polling") + "&sid=" + sid, data='11:42["hello"]',
                                   headers=useragent)
                break
            except aiohttp.client_exceptions.ClientOSError:
                attempts += 1
    async with websockets.connect(socket_url.format("ws", "websocket&sid=") + sid, extra_headers=useragent) as ws:
        await ws.send("2probe")
        await ws.recv()
        await ws.send("5")
        await ws.recv()
        await ws.send("42['useAPI', '{}'".format(config.PZ_API_KEY))
        try:
            async for msg in ws:
                d = json.loads(msg[msg.find('['):])
                if type(d) == int:
                    continue
                if d[0] == "g":
                    data = d[1]
                    break
        except websockets.ConnectionClosed as e:
            raise HttpCanvasError('pixelzone')
    return data


async def fetch_online_pxlsspace():
    async with websockets.connect("wss://pxls.space/ws", extra_headers=useragent) as ws:
        async for msg in ws:
            d = json.loads(msg)
            if d['type'] == 'users':
                return d['count']


async def fetch_online_pixelplanet():
    async with aiohttp.ClientSession() as sess:
        async with sess.get("https://pixelplanet.fun/api/online", headers=useragent) as resp:
            if resp.status != 200:
                raise HttpGeneralError
            data = json.loads(await resp.read())
            return data['online']


async def get_changelog(version):
    url = "https://api.github.com/repos/DiamondIceNS/StarlightGlimmer/releases"
    async with aiohttp.ClientSession() as sess:
        async with sess.get(url) as resp:
            if resp.status != 200:
                raise HttpGeneralError
            data = json.loads(await resp.read())
            return next((x for x in data if x['tag_name'] == "v{}".format(version)), None)


async def get_template(url, name):
    async with aiohttp.ClientSession() as sess:
        async with sess.get(url) as resp:
            if resp.status != 200:
                raise TemplateHttpError(name)
            if resp.content_type == "image/jpg" or resp.content_type == "image/jpeg":
                raise NoJpegsError
            if resp.content_type != "image/png":
                raise NotPngError
            return io.BytesIO(await resp.read())
