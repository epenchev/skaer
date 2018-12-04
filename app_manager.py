import os
import sys
import os.path
from aiohttp import web

# Collection format -> name : (path, class, category, cover image)
COLLECTION_MODULES = (
    {'YouTube Music': ('media_collections.youtube_music', 'YouTubeClient')},
    {'YesMovies': ('media_collections.yesmovies', 'YesMoviesChannel')}
)

class AppManager(web.Application):
    def __init__(self):
        super().__init__()
        self._collections = self._load_media_collections(COLLECTION_MODULES)
        self.setup_api_routes()
        path = os.path.realpath(os.path.abspath(__file__))
        sys.path.insert(0, os.path.dirname(os.path.dirname(path)))


    def _load_media_collections(self, collections):
        """ Load media collections on the fly """
        loaded = {}
        module_id = 1
        for col in collections:
            for name, items in col.items():
                path, klassname = items
                module = __import__(path, fromlist=(klassname), level=0)
                try:
                    instance = getattr(module, klassname)(self)
                    loaded[module_id] = (name, instance)
                    module_id += 1
                except (AttributeError, TypeError) as err:
                    print('Warning: module [%s] failed verification, %s' % (name, str(err)))
        return loaded

    def run(self, listen_port):
        web.run_app(self, port=listen_port)

    def get_collection_info(self, col_id):
        if col_id in self._collections:
            instance = self._collections[col_id][1]
            return instance.get_info()
        print('Warning: no collection with this id : [%s]' % col_id)
        return None


    async def get_collection_items(self, col_id):
        if col_id in self._collections:
            instance = self._collections[col_id][1]
            return await instance.get_items()
        print('Warning: no collection with this id : [%s]' % col_id)
        return None

    def get_collections(self):
        return { col_id : col_attrs[0]
                 for col_id, col_attrs in self._collections.items() }

    def get_collection_item(self, col_id, item_id):
        if col_id in self._collections:
            instance = self._collections[col_id][1]
            return instance.get_item(item_id)
        print('Warning: no collection with this id : [%s]' % col_id)
        return None

    async def handle_get_all_collections(self, request):
        col_out = []
        collections = self.get_collections()
        for col_id, col_name in collections.items():
            info = self.get_collection_info(col_id)
            col_out.append({
                    'id' : col_id,
                    'name' : col_name,
                    'cover_image' : info['cover_image'],
                    'category' : info['category']
                    }
            )
        return web.json_response(col_out)

    async def handle_redirect_ui(self, request):
        location = request.app.router['ui'].url_for(filename='index.html')
        raise web.HTTPFound(location=location)

    async def handle_get_collection(self, request):
        return web.json_response(self.get_collection_info(int(request.match_info['id'])))

    async def handle_get_collection_items(self, request):
        return web.json_response(self.get_collection_items(int(request.match_info['id'])))

    async def handle_get_collection_item(self, request):
        item = self.get_collection_item(request.match_info['id'], request.match_info['item'])
        return web.json_response(item)

    def setup_api_routes(self):
        # User interface
        self.router.add_get(r'/', self.handle_redirect_ui)
        self.router.add_static(r'/ui', 'ui/', name='ui')
        # Media Collections API
        self.router.add_get(r'/collections', self.handle_get_all_collections)
        self.router.add_get(r'/collections/{id}', self.handle_get_collection)
        self.router.add_get(r'/collections/{id}/items', self.handle_get_collection_items)
        self.router.add_get(r'/collections/{id}/items/{item_id}', self.handle_get_collection_item)
        # self.router.add_get(r'/collections/{id}/play/{item_id}', self.handle_play_collection_item)
