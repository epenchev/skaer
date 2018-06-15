from aiohttp import web

# Channel format
# name : (path, class)
_CHANELLS = (
    {'YouTube Music': ('channels.youtube_music', 'YouTubeClient')},
    {'YesMovies': ('channels.yesmovies', 'YesMoviesChannel')}
)

# Library format
# name : (path, class)
_LIBRARIES = ()

class AppManager(web.Application):
    def __init__(self):
        super().__init__()
        self._channels = self._load_modules(_CHANELLS)
        self._libraries = self._load_modules(_LIBRARIES)

    def _load_modules(self, import_modules):
        loaded = {}
        module_id = 1
        for imp_module in import_modules:
            for name, items in imp_module.items():
                path, klassname = items
                module = __import__(path, fromlist=(klassname), level=0)
                instance = getattr(module, klassname)()
                loaded[module_id] = (name, instance)
                module_id += 1
        return loaded

    def run(self, listen_port):
        web.run_app(self, port=listen_port)

    def get_channels(self):
        return 'channels list'

    def get_libraries(self):
        return 'libraries list'
