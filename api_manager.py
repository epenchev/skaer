from aiohttp import web


class ApiManager:
    def __init__(self, app):
        self._app = app

    async def handle_libraries(self, request):
        libraries = self._app.get_libraries()
        return web.json_response(libraries)

    async def handle_channels(self, request):
        channels = self._app.get_channels()
        return web.json_response(channels)

    async def handle_view(self, request):
        response_text = self._app.get_channels()
        return web.Response(text=response_text)

    def setup_routes(self):
        self._app.router.add_get('/', self.handle_view)
        self._app.router.add_get('/ui', self.handle_view)
        self._app.router.add_get('/channels', self.handle_channels)
        self._app.router.add_get('/libraries', self.handle_libraries)
        # Disabled for now, but will be part of the future api
        '''
        self._app.router.add_get('/users')
        self._app.router.add_get(r'/users/{id}')
        self._app.router.add_get(r'/channels/{id}')
        self._app.router.add_get(r'/channels/{id}/{item}')
        self._app.router.add_get(r'/channels/play/{id}/{item}')
        self._app.router.add_get(r'/libraries/{id}')
        self._app.router.add_get(r'/libraries/scan/{id}')
        self._app.router.add_get(r'/libraries/{id}/{item}')
        self._app.router.add_get(r'/libraries/play/{id}/{item}')
        self._app.router.add_get(r'/devices')
        self._app.router.add_get(r'/devices/{id}')
        '''

