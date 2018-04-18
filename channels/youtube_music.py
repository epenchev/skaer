import json
import socket
import gzip
import http.cookiejar
import urllib.request
import urllib.parse
import http.client

class YouTubeClient(object):
    def __init__(self):
        self._api_key = 'AIzaSyBbaFOsbZ-kmMM969-Tdil5-sPO16UozaA'
        self._cookiejar = http.cookiejar.CookieJar()
        self._opener = urllib.request.build_opener(
            urllib.request.HTTPCookieProcessor(self._cookiejar))
        self._language = 'bg'
        self._region = 'BG'
        self._max_results = 10

    def perform_v3_get_request(self, headers=None, path=None, params=None):
        req_params = {'key': self._api_key}
        if params:
            req_params.update(params)

        req_headers = {
            'Host': 'www.googleapis.com',
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0',
            'Accept-Encoding': 'gzip, deflate',
            #'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-us,en;q=0.5',
            'Connection': 'keep-alive'
        }

        result = None
        req_url = 'https://www.googleapis.com/youtube/v3/%s?%s' % \
            (path.strip('/'), urllib.parse.urlencode(req_params))

        if headers:
            req_headers.update(headers)

        # TODO get from server environment
        # context.log_debug('[data] v3 request: |{0}| path: |{1}| params: |{2}| post_data: |{3}|'.format(method, path, params, post_data))

        try:
            # TODO use requests module as its support Accept-Encoding': 'gzip, deflate' header
            req = urllib.request.Request(req_url, headers=req_headers)
            response = self._opener.open(req)

            if response.getheader('Content-Encoding', '') == 'gzip':
                data = gzip.decompress(response.read()).decode('utf-8')
            else:
                data = response.read().decode('utf-8')

            if response.getheader('content-type', '').startswith('application/json'):
                result = json.loads(data)
            else:
                result = data

            response.close()
        except (urllib.request.URLError, http.client.HTTPException, socket.error):
            # context.log_error([data] v3 request: |{0}| path: |{1}| params: |{2}| post_data: |{3}| error))
            pass
        except json.JSONDecodeError as json_err:
            # context.log_error([data] v3 request: |{0}| path: |{1}| params: |{2}| post_data: |{3}| json_err.msg))
            pass
        return result


    def get_popular_videos(self, page_token=''):
        params = {'part': 'snippet',
                  'maxResults': str(self._max_results),
                  'regionCode': self._region,
                  'hl': self._language,
                  'videoCategoryId': 10,
                  'chart': 'mostPopular'}
        if page_token:
            params['pageToken'] = page_token
        return self.perform_v3_get_request(path='videos', params=params)


    def get_video_categories(self):
        params = {'part': 'snippet',
                  'regionCode': self._region,
                  'hl': 'en' }
        return self.perform_v3_get_request(path='videoCategories', params=params)


    def get_videos(self, video_id):
        """
        Returns a list of videos that match the API request parameters
        :param video_id: list of video ids
        :return:
        """
        if isinstance(video_id, list):
            video_id = ','.join(video_id)
        params = {'part': 'snippet,contentDetails',
                  'id': video_id}
        return self.perform_v3_get_request(path='videos', params=params)


    def search(self, q, search_type=['video', 'channel', 'playlist'], channel_id='', order='relevance', safe_search='moderate', page_token=''):
        """
        Returns a collection of search results that match the query parameters specified in the API request. By default,
        a search result set identifies matching video, channel, and playlist resources, but you can also configure
        queries to only retrieve a specific type of resource.
        :param q:
        :param search_type: acceptable values are: 'video' | 'channel' | 'playlist'
        :param channel_id: limit search to channel id
        :param order: one of: 'date', 'rating', 'relevance', 'title', 'videoCount', 'viewCount'
        :param safe_search: one of: 'moderate', 'none', 'strict'
        :param page_token: can be ''
        :return:
        """
        # prepare search type
        if not search_type:
            search_type = ''
        if isinstance(search_type, list):
            search_type = ','.join(search_type)

        # prepare page token
        if not page_token:
            page_token = ''

        # prepare params
        params = {'q': q,
                  'part': 'snippet',
                  'regionCode': self._region,
                  'hl': self._language,
                  'relevanceLanguage': self._language,
                  'maxResults': str(self._max_results)}
        if search_type:
            params['type'] = search_type
        if channel_id:
            params['channelId'] = channel_id
        if order:
            params['order'] = order
        if safe_search:
            params['safeSearch'] = safe_search
        if page_token:
            params['pageToken'] = page_token

        video_only_params = ['eventType', 'videoCaption', 'videoCategoryId', 'videoDefinition',
                             'videoDimension', 'videoDuration', 'videoEmbeddable', 'videoLicense',
                             'videoSyndicated', 'videoType', 'relatedToVideoId', 'forMine']
        for key in video_only_params:
            if params.get(key) is not None:
                params['type'] = 'video'
                break

        return self.perform_v3_get_request(path='search', params=params, quota_optimized=False)


# Simple example remove after test
def parse_simple_json():
    data ='{'\
    '"kind": "youtube#videoCategory",'\
    '"etag": "etag",'\
    '"id": "string",'\
    '"snippet": {'\
        '"channelId": "UCBR8-60-B28hp2BmDPdntcQ",'\
        '"title": "string",'\
        '"assignable": "boolean"'\
        '}'\
    '}'
    json_data = json.loads(data)
    print(json_data['snippet']['assignable'])

if __name__ == '__main__':
    #parse_simple_json()
    client = YouTubeClient()
    print(client.get_video_categories())

    
