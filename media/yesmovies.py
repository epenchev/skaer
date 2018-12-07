
class YesMoviesMedia(object):

    def __init__(self, app):
        self._app = app

    def get_info(self):
        return { 'description' : 'YesMovies media source',
                 'cover_image' : 'images/yes-movies.jpg',
                 'category'    : 'Video' }
