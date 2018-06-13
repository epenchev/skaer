from aiohttp import web


class WebServer:
    def __init__(self, listen_port):
        self._listen_port = listen_port
        self.app = web.Application()

    def run(self):
        web.run_app(self.app, port=self._listen_port)
