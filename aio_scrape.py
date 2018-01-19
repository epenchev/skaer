import re
import aiohttp
import asyncio
import threading
from timeit import default_timer as timer


class Scraper:
    def __init__(self, loop):
        self._genres = dict()
        self._movies = dict()
        self._loop = loop
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

    async def _urlopen(self, client, url):
        async with client.get(url) as resp:
            assert resp.status == 200
            return await resp.text()

    async def fetch(self):
        async with aiohttp.ClientSession(headers=self._headers, loop=self._loop) as client:
            while len(self._links):
                root_url = self._links.pop(0)
                data = await self._urlopen(client, root_url)
                if data:
                    self.parse_links(root_url, data)

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
    loop = asyncio.get_event_loop()
    s = Scraper(loop)

    start  = timer()
    loop.run_until_complete(s.fetch())
    print('Completed in %.2f sec.' % (timer() - start))
    print('Summary, got {} movies'.format(len(s._movies)))
