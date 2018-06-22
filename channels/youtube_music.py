import requests

class YouTubeClient(object):
    def __init__(self, app):
        self._app = app
        self._api_key = 'AIzaSyBbaFOsbZ-kmMM969-Tdil5-sPO16UozaA'
        self._language = 'en'  #'bg'
        self._region = 'BG'
        self._max_results = 2
        self._category_id = self._get_music_category_id()

    def get_info(self):
        return {'description' : 'Youtube music application that streams only audio',
                'image'       : '../ui/YouTube_Music.png'}

    def _perform_v3_get_request(self, headers=None, path=None, params=None):
        req_params = {'key': self._api_key}
        if params:
            req_params.update(params)

        req_headers = {
            'Host': 'www.googleapis.com',
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0',
            'Accept-Encoding': 'gzip, deflate' }

        url = 'https://www.googleapis.com/youtube/v3/%s' % path.strip('/')

        if headers:
            req_headers.update(headers)

        r = requests.get(url, params=req_params, headers=req_headers)
        if r.headers.get('content-type', '').startswith('application/json'):
            return r.json()
        else:
            return r.content.decode('utf-8')

    def _get_music_category_id(self):
        params = {'part': 'snippet',
                  'regionCode': self._region,
                  'hl': 'en'}
        json_result = self._perform_v3_get_request(path='videoCategories', params=params)
        for item in json_result['items']:
            if item['snippet']['title'].startswith('Music'):
                category_id = int(item['id'])
                break
        return category_id


    def get_popular_music_videos(self, page_token=''):
        params = {'part': 'snippet',
                  'maxResults': str(self._max_results),
                  'regionCode': self._region,
                  'hl': self._language,
                  'videoCategoryId': self._category_id,
                  'chart': 'mostPopular'}
        if page_token:
            params['pageToken'] = page_token
        res = self._perform_v3_get_request(path='videos', params=params)
        print(len(res['items']))
        for item in res['items']:
            print('%s:%s' % (item['id'], item['snippet']['title']))
            print(item['snippet']['thumbnails'])


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
        return self._perform_v3_get_request(path='videos', params=params)


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
        return self._perform_v3_get_request(path='search', params=params, quota_optimized=False)

if __name__ == '__main__':
    client = YouTubeClient()
    res = client.get_popular_music_videos()
    #print(res)

    
