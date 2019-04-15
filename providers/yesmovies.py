import requests


class YesMoviesProvider(object):
    def __init__(self):
        pass

    def get_info(self):
        return { 'name'        : 'YesMovies',
                 'description' : 'YesMovies media provider',
                 'cover_image' : 'http://localhost:8080/res/images/yes-movies.jpg',
                 'category'    : 'Video' }

    def entries(self):
        """ Return all entries (videos) """
        return ([], 0, None)

