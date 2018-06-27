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

    async def get_channel(self, request):
        info = self._app.get_channel_info(int(request.match_info['id']))
        return web.json_response(info)

    async def get_channel_items(self, request):
        items = await self._app.get_channel_items(int(request.match_info['id']))
        return web.json_response(items)

    async def get_channel_item(self, request):
        item = self._app.get_channel_item(request.match_info['id'], request.match_info['item'])
        return web.json_response(item)

    def setup_routes(self):
        self._app.router.add_get('/', self.handle_view)
        self._app.router.add_get('/ui', self.handle_view)
        self._app.router.add_get('/channels', self.handle_channels)
        self._app.router.add_get('/libraries', self.handle_libraries)
        self._app.router.add_get(r'/channels/{id}', self.get_channel)
        self._app.router.add_get(r'/channels/{id}/items', self.get_channel_items)
        self._app.router.add_get(r'/channels/{id}/{item}', self.get_channel_item)
        # Disabled for now, but will be part of the future api
        '''
        self._app.router.add_get('/users')
        self._app.router.add_get(r'/users/{id}')
        self._app.router.add_get(r'/channels/play/{id}/{item}')
        self._app.router.add_get(r'/libraries/{id}')
        self._app.router.add_get(r'/libraries/scan/{id}')
        self._app.router.add_get(r'/libraries/{id}/{item}')
        self._app.router.add_get(r'/libraries/play/{id}/{item}')
        self._app.router.add_get(r'/devices')
        self._app.router.add_get(r'/devices/{id}')
        '''

