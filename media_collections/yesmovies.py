
class YesMoviesChannel(object):
    def __init__(self, app):
        self._app = app

    def get_info(self):
        return { 'description' : 'YesMovies streamer for watchig movies',
                 'cover_image'       : 'images/yes-movies.jpg',
                 'category'         : 'Video' }
