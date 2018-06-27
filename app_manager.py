from aiohttp import web

# Channel format -> name : (path, class)
_CHANELLS = (
    {'YouTube Music': ('channels.youtube_music', 'YouTubeClient')},
    {'YesMovies': ('channels.yesmovies', 'YesMoviesChannel')}
)

# Library format -> name : (path, class)
_LIBRARIES = ()

class AppManager(web.Application):
    def __init__(self):
        super().__init__()
        self._channels = self._load_modules(_CHANELLS, self._verify_channel)
        self._libraries = self._load_modules(_LIBRARIES, self._verify_library)

    def _load_modules(self, import_modules, verfier):
        loaded = {}
        module_id = 1
        for imp_module in import_modules:
            for name, items in imp_module.items():
                path, klassname = items
                module = __import__(path, fromlist=(klassname), level=0)
                try:
                    instance = getattr(module, klassname)(self)
                    verfier((name, instance))
                    loaded[module_id] = (name, instance)
                    module_id += 1
                except (AttributeError, TypeError) as err:
                    print('Warning: module [%s] failed verification, %s' % (name, str(err)))
        return loaded

    def _verify_channel(self, chan_entry):
        name, chan_obj = chan_entry
        chan_obj.get_info()
        if not hasattr(chan_obj, 'get_info'):
            raise AttributeError
        if not hasattr(chan_obj, 'get_items'):
            raise AttributeError

    def _verify_library(self, library_entry):
        name, library_obj = library_entry
        library_obj.get_info()

    def run(self, listen_port):
        web.run_app(self, port=listen_port)

    def get_channel_info(self, chan_id):
        if chan_id in self._channels:
            instance = self._channels[chan_id][1]
            return instance.get_info()
        print('Warning: no channel with this id : [%s]' % chan_id)
        return None

    async def get_channel_items(self, chan_id):
        if chan_id in self._channels:
            instance = self._channels[chan_id][1]
            return await instance.get_items()
        print('Warning: no channel with this id : [%s]' % chan_id)
        return None

    def get_channels(self):
        return { chan_id : chan_attrs[0]
                 for chan_id, chan_attrs in self._channels.items() }

    def get_channel_item(self, chan_id, item_id):
        if chan_id in self._channels:
            instance = self._channels[chan_id][1]
            return instance.get_item(item_id)
        print('Warning: no channel with this id : [%s]' % chan_id)
        return None

    def get_libraries(self):
        return { lib_id: lib_attrs[0]
                 for lib_id, lib_attrs in self._libraries.items() }
