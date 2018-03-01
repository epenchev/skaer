from aiohttp import web
import asyncio
import os, sys, time
from multiprocessing import Process, Pipe


class OutProtocol(asyncio.SubprocessProtocol):
    def __init__(self, exit_future):
        self.exit_future = exit_future
        self.output = bytearray()

    def pipe_data_received(self, fd, data):
        self.output.extend(data)

    def process_exited(self):
        self.exit_future.set_result(True)


def do_writing(writer):
    path = '/mnt/c/Users/Emil_Penchev/Downloads/Books'
    # path = 'C:\\Users\\Emil_Penchev\\Downloads\\Books'
    for root, dirs, files in os.walk(path):
        for f in files:
            writer.send(f)
            time.sleep(1)
        break
    writer.close()



class MediaController:
    def __init__(self, loop):
        self._loop = loop
        self._scan_in_progress = False
        self._scan_result = list()

    def get_media_lib(self):
        return self._media_lib

    async def stream_media(self, request):
        return web.Response(text="Hello, world")


    async def scan_library(self, request):
        if not self._scan_in_progress:
            self._scan_in_progress = True
            scan_proc = asyncio.create_subprocess_exec(sys.executable, 'scan_lib.py',
                                                       stdout=asyncio.subprocess.PIPE)
            proc_hand = await scan_proc
            while True:
                data = await proc_hand.stdout.readline()
                if not data:
                    break
                entry = data.decode('ascii').strip()
                if entry == 'bye':
                    break
                print(entry)
                self._scan_result.append(entry)

        lib_output = '\n'.join(self._scan_result)
        proc_hand.kill()
        return web.Response(text=lib_output)

    '''
    async def scan_library(self, request):
        if not self._scan_in_progress:
            self._scan_in_progress = True
            parent_conn, child_conn = Pipe()
            p = Process(target=do_writing, args=(child_conn,))
            p.start()
            reader = asyncio.StreamReader()
            read_protocol = asyncio.StreamReaderProtocol(reader)
            read_transport, _ = await loop.connect_read_pipe(
                lambda: read_protocol, os.fdopen(parent_conn.fileno()))
            while not reader.at_eof():
                some_bytes = await reader.read(10)
                print("here's what we got:", some_bytes.decode('ascii'))
                self._scan_result.append(str(some_bytes))

        lib_output = '\n'.join(self._scan_result)
        return web.Response(text=lib_output)
    '''



if __name__ == '__main__':
    loop = None
    if sys.platform == 'win32':
        loop = asyncio.ProactorEventLoop()
        asyncio.set_event_loop(loop)
    else:
        loop = asyncio.get_event_loop()

    mc = MediaController(loop=loop)
    app = web.Application(loop=loop)
    app.router.add_static('/videos', '/mnt/c/Users/Emil_Penchev/Videos',
                          show_index=True)
    app.router.add_get('/scan', mc.scan_library)
    web.run_app(app, port=8888)
