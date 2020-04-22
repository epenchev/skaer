import requests


class YesMoviesApp(object):
    def __init__(self):
        self.info = { 
            'name'        : 'YesMovies',
            'path'        : 'yesmovies',
            'description' : 'YesMovies skaer app',
            'cover_image' : 'http://localhost:8080/res/images/yes-movies.jpg',
            'category'    : 'Video' 
        }

    def entries(self):
        """ Return all entries (videos) """
        return []

    def register_api_routes(self, router):
        router.connect('GET', 'yesmovies/info', self.get_info)


