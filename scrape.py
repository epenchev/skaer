import re
import json
import socket

try:
    import http.cookiejar as compat_cookiejar
except ImportError:  # Python 2
    import cookielib as compat_cookiejar

try:
    import urllib.request as compat_urllib_request
except ImportError:  # Python 2
    import urllib2 as compat_urllib_request

try:
    import http.client as compat_http_client
except ImportError:  # Python 2
    import httplib as compat_http_client

#import urllib2
#from cookielib import CookieJar


class Scraper:
    def __init__(self):
        self._cookiejar = compat_cookiejar.CookieJar()
        self._opener = compat_urllib_request.build_opener(
            compat_urllib_request.HTTPCookieProcessor(self._cookiejar))
        self._genres = dict()
        self._movies = dict()
        #self._base_url = 'https://yesmovies.to/'
        self._base_url = 'https://yesmovies.to/movie/filter/movies.html'
        self._headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0',
            'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-us,en;q=0.5',
        }
        self._genre_expr = re.compile(r'<a href=\"(\S+/genre/\S+)\" title=\"(\S+)\"')
        self._movie_entry_expr = re.compile(r'<a href=\S+ class=\"ml-mask\" title=\"(.+)\"\s+data-url=\"(\S+)\">\s.+\s.+<.+\s+data-original=\"(\S+)\"')
        self._next_page_expr = re.compile(r'<li class=\"next\"><a href=\"(\S+)\"')
        self._links = [self._base_url]

    def _urlopen(self, url, data=None):
        try:
            req = compat_urllib_request.Request(url, data, self._headers)
            response = self._opener.open(req)
            data = response.read()
            response.close()
            return data
        except (compat_urllib_request.URLError, compat_http_client.HTTPException, socket.error) as err:
            print('Got error from urlopen() %s' % err)
        return None

    def fetch(self):
        while len(self._links):
            root_url = self._links.pop(0)
            data = self._urlopen(root_url)
            if data:
                self.parse_links(root_url, data.decode('utf-8'))

        print('Summary, got {} movies'.format(len(self._movies)))
        #print(self._movies.keys())

    def parse_links(self, root, data):
        if root == self._base_url:
            self.extract_genres(data)
        elif root.find('genre') != -1:
            self.extract_movies(data)
        elif root.find('movie_info') != -1:
            self.extract_info(data)

    def extract_genres(self, data):
        for r in re.finditer(self._genre_expr, data):
            genre_name, genre_url = r.group(2), r.group(1)
            self._genres[genre_name] = genre_url
            self._links.append(genre_url)

    def extract_movies(self, data):
        movid_expr = re.compile(r'(\d+)\.html')
        for r in re.finditer(self._movie_entry_expr, data):
            info_url = self._base_url + r.group(2)
            found = re.search(movid_expr, info_url)
            if found:
                self._movies[r.group(1)] = {
                    'movid' : found.group(1),
                    'info_url' : info_url,
                    'img_url' : r.group(3),
                }
                #self._links.append(info_url)

        found_next = re.search(self._next_page_expr, data)
        if found_next:
            print('adding ' + found_next.group(1))
            self._links.append(found_next.group(1))

    def extract_info(self, data):
        pass


if __name__ == '__main__':
    s = Scraper()
    s.fetch()
