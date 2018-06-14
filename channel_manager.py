
# Channel format
# name : (path, class)
import_modules = (
    {'YouTube Music': ('channels.youtube_music', 'YouTubeClient')},
    {'YesMovies': ('channels.yesmovies', 'YesMoviesChannel')}
)


class ChannelManager:
    def __init__(self, app):
        self._app = app
        self._channels = {}
        self.__load_channels()

    def __load_channels(self):
        chan_id = 1
        for imp_module in import_modules:
            for name, items in imp_module.items():
                path, klassname = items
                module = __import__(path, fromlist=(klassname), level=0)
                _instance = getattr(module, klassname)()
                self._channels[chan_id] = (name, _instance)
                chan_id += 1

    def get_channels(self):
        return 'channels list'
