import asyncio
from collections import deque
import io
import json
import logging
from time import time

import aiohttp
import websockets
from typing import Iterable

from objects.chunks import BigChunk, ChunkPz, PxlsBoard
from objects.errors import HttpCanvasError, HttpGeneralError, NoJpegsError, NotPngError, TemplateHttpError
from utils import config
from utils.version import VERSION


log = logging.getLogger(__name__)

useragent = {
    'User-Agent': 'StarlightGlimmer/{} (+https://github.com/DiamondIceNS/StarlightGlimmer)'.format(VERSION),
    'Cache-Control': 'no-cache'
}
pz_rate_limiter = None


async def fetch_chunks(chunks: Iterable):
    c = next(iter(chunks))
    if type(c) is BigChunk:
        await _fetch_chunks_pixelcanvas(chunks)
    elif type(c) is ChunkPz:
        await _fetch_chunks_pixelzone(chunks)
    elif type(c) is PxlsBoard:
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
    global pz_rate_limiter
    if pz_rate_limiter is None:
        pz_rate_limiter = RateLimitingSemaphore(2, 0.4, asyncio.get_event_loop())
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
            async for msg in ws:
                if msg == '3probe':
                    break
            await ws.send("5")
            await ws.send("42hello")
            async for msg in ws:
                if msg[4:11] == 'welcome':
                    break
            await ws.send('42["useAPI", "{}"]'.format(config.PZ_API_KEY))
            async for msg in ws:
                if msg[4:18] == 'useAPICallback':
                    break
            async with pz_rate_limiter:
                for ch in chunks:
                    await ws.send(ch.url)
                    packet = None
                    async for msg in ws:
                        if packet is None:
                            if msg[:2] == '45':
                                packet = {}
                                data = json.loads(msg[msg.find('-')+1:])[1]
                                packet['cx'] = data['cx']
                                packet['cy'] = data['cy']
                        else:
                            packet['data'] = msg[1:]
                            break
                    ch = next((x for x in chunks if x.x == packet['cx'] and x.y == packet['cy']))
                    ch.load(packet['data'])
        except websockets.ConnectionClosed:
            raise HttpCanvasError('pixelzone')


async def _fetch_pxlsspace(chunks: Iterable[PxlsBoard]):
    board = next(iter(chunks))
    async with aiohttp.ClientSession() as session:
        async with session.get("https://pxls.space/info", headers=useragent) as resp:
            info = json.loads(await resp.read())
        board.set_board_info(info)

        async with session.get("https://pxls.space/boarddata?={0:.0f}".format(time()), headers=useragent) as resp:
            board.load(await resp.read())


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
        await ws.send("2probe")
        async for msg in ws:
            if msg == '3probe':
                break
        await ws.send("5")
        await ws.send("42hello")
        async for msg in ws:
            if msg[4:11] == 'welcome':
                break
        try:
            async for msg in ws:
                if msg[4:17] == 'playerCounter':
                    d = json.loads(msg[2:])
                    data = d[1]
                    break
        except websockets.ConnectionClosed:
            raise HttpCanvasError('pixelzone')
    return data


async def fetch_online_pxlsspace():
    async with websockets.connect("wss://pxls.space/ws", extra_headers=useragent) as ws:
        async for msg in ws:
            d = json.loads(msg)
            if d['type'] == 'users':
                return d['count']


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


# https://stackoverflow.com/a/46255794
class RateLimitingSemaphore:
    def __init__(self, max_reqs, interval, loop):
        self.loop = loop
        self.max_reqs = max_reqs
        self.interval = interval / max_reqs
        self.queued_calls = 0
        self.call_times = deque()

    async def __aenter__(self):
        self.queued_calls += 1
        while True:
            cur_rate = 0
            if len(self.call_times) == self.max_reqs:
                cur_rate = self.max_reqs / (self.loop.time() - self.call_times[0])
            if cur_rate < self.max_reqs:
                break
            elapsed_time = self.loop.time() - self.call_times[-1]
            await asyncio.sleep(self.queued_calls * self.interval - elapsed_time)
        self.queued_calls -= 1

        if len(self.call_times) == self.max_reqs:
            self.call_times.popleft()
        self.call_times.append(self.loop.time())

    async def __aexit__(self, exc_type, exc, tb):
        pass
