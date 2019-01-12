import requests


class YouTubeMusicProvider(object):
    def __init__(self):
        self._api_key = 'AIzaSyBbaFOsbZ-kmMM969-Tdil5-sPO16UozaA'
        self._language = 'en'  #'bg'
        self._region = 'BG'
        self._max_results = 10
        self.req_headers = {
            'Host': 'www.googleapis.com',
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0',
            'Accept-Encoding': 'gzip, deflate'
        }
        self.api_url = 'https://www.googleapis.com/youtube/v3/'


    def get_info(self):
        return { 'name'        : 'YouTube Music',
                 'description' : 'Media provider to fetch music from youtube',
                 'cover_image' : 'images/y-music.jpeg',
                 'category'    : 'Music' }

    def entries(self):
        pass

    def perform_v3_get_request(self, headers=None, path=None, params=None):
        req_params = {'key': self._api_key}
        if params:
            req_params.update(params)
        req_headers = self.req_headers
        url = self.api_url + path.strip('/')
        if headers:
            req_headers.update(headers)
        r = requests.get(url, params=req_params, headers=req_headers)
        assert r.status_code == requests.codes.ok
        if r.headers.get('content-type', '').startswith('application/json'):
            return r.json()
        else:
            return r.content.decode('utf-8')

    def get_music_category_id(self):
        params = {'part': 'snippet',
                  'regionCode': self._region,
                  'hl': 'en'}
        json_result = self.perform_v3_get_request(path='videoCategories', params=params)
        for item in json_result['items']:
            if item['snippet']['title'].startswith('Music'):
                category_id = int(item['id'])
                break
        return category_id


    def get_popular_music_videos(self, page_token=None, max_results=None):
        """
        Returns a list of the most popular music videos for that region.
        :param page_token: fetch a concrete page
        :max_results: max results to return
        :return:
        """
        category_id = self.get_music_category_id()
        if max_results:
            maxres = max_results
        else:
            maxres = self._max_results

        params = {'part': 'snippet',
                  'maxResults': str(maxres),
                  'regionCode': self._region,
                  'hl': self._language,
                  'videoCategoryId': category_id,
                  'chart': 'mostPopular'}
        if page_token:
            params['pageToken'] = page_token
        res = self.perform_v3_get_request(path='videos', params=params)
        if 'nextPageToken' in res:
            next_page = res['nextPageToken']
        else:
            next_page = None

        channel_items = {}
        for item in res['items']:
            channel_items[item['id']] = ( item['snippet']['title'],
                                          item['snippet']['thumbnails']['medium']['url'] )
        return channel_items, res['pageInfo']['totalResults'], next_page


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


    def search(self, q, search_type=['video', 'channel', 'playlist'], channel_id='',
               order='relevance', safe_search='moderate', page_token=''):
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

