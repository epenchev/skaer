from aiohttp import web


class ApiManager:
    def __init__(self, app):
        self._app = app
        self._chmngr = self._app['channels']
        self._libmngr = self._app['libraries']

    async def handle_libraries(self, request):
        response_text = self._libmngr.get_libraries()
        return web.Response(text=response_text)

    async def handle_channels(self, request):
        response_text = self._chmngr.get_channels()
        return web.Response(text=response_text)

    async def handle_view(self, request):
        response_text = self._chmngr.get_channels()
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

