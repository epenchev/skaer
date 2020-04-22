import requests


class YoutubeDataApi(object):
    """ Youtube data api access bridge. """

    def __init__(self, api_config):
        self._api_key =  api_config['api_key']
        self._api_endpoint = api_config['api_url']
        self._lang = api_config['lang']
        self._region = api_config['region']
        self._max_results = api_config['max_results']
        
        self._req_headers = {
            'Host': 'www.googleapis.com',
            'User-Agent': 'Mozilla/5.0 Firefox/66.0',
            'Accept-Encoding': 'gzip, deflate'
        }

    def v3_get_request(self, headers=None, path=None, params=None):
        req_params = { 'key': self._api_key }
        if params:
            req_params.update(params)

        req_headers = self._req_headers
        url = self._api_endpoint + path.strip('/')
        if headers:
            req_headers.update(headers)

        response = requests.get(url, params=req_params, headers=req_headers)
        if response.status_code != requests.codes.ok:
            response.raise_for_status()
        if response.headers.get('content-type', '').startswith('application/json'):
            return response.json()
        else:
            return response.content.decode('utf-8')

    def playlists(self, ids):
        """ 
        Retrieve one or more playlists by their unique IDs.

        """
        result = self.v3_get_request(path='playlists',
                                     params={
                                        'part': 'snippet',
                                        'id': ','.join(ids),
                                        'maxResults': str(self._max_results), 
                                        'hl': self._lang
                                     })
        playlists = []
        res_count = result['pageInfo']['totalResults']
        for res in result['items']:
            playlists.append({
                'id': res['id'],
                'title': res['snippet']['title'],
                'thumb': res['snippet']['thumbnails']['medium']['url'],
            })
        return playlists

    def playlist_items(self, list_id, pagetoken=None):
        """
        Return all items associated with this playlist id.

        """
        items = []
        params = {
           'part': 'contentDetails',
           'maxResults': str(self._max_results),
           'playlistId': list_id
        }
        if pagetoken:
            params['pageToken'] = pagetoken

        result = self.v3_get_request(path='playlistItems', params=params)
        items = self.videos([video['contentDetails']['videoId'] for video in result['items']])
        return items, result.get('nextPageToken', None)

    def search(self, q, search_type=['video', 'channel', 'playlist'],
               channel_id='', order='relevance', safe_search='moderate',
               page_token=''):
        """
        Returns a collection of search results that match the query parameters.
        By default, a search result set identifies matching 
        video, channel, and playlist resources.
        One can also configure queries to only retrieve a specific type of resource.
        :param q: search string.
        :param search_type: acceptable values: 'video' | 'channel' | 'playlist'.
        :param channel_id: limit search to channel id
        :param order: one of: 'date', 'rating', 'relevance',
                              'title', 'videoCount', 'viewCount'
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
        params = {
            'q': q,
            'part': 'snippet',
            'regionCode': self._region,
            'hl': self._lang,
            'relevanceLanguage': self._lang,
            'maxResults': str(self._max_results)
        }
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

        video_only_params = [
            'eventType', 'videoCaption', 'videoCategoryId', 'videoDefinition',
            'videoDimension', 'videoDuration', 'videoEmbeddable', 'videoLicense',
            'videoSyndicated', 'videoType', 'relatedToVideoId', 'forMine'
        ]
        for key in video_only_params:
            if params.get(key) is not None:
                params['type'] = 'video'
                break
        res = self.v3_get_request(path='search', params=params)
        return res

    def videos(self, video_ids):
        """
        Returns a list of videos and the information about each video.

        """
        params = {
            'part': 'snippet,contentDetails',
            'regionCode': self._region,
            'hl': self._lang,
            'id': ','.join(video_ids)
        }

        result = self.v3_get_request(path='videos', params=params)
        items = []
        for item in result['items']:
            video = {
                'id': item['id'],
                'title': item['snippet']['title'],
                'thumbnail': item['snippet']['thumbnails']['medium']['url'],
                'duration': item['contentDetails']['duration']
            }
            items.append(video)
        return items

    def _get_music_category_id(self):
        params = {
            'part': 'snippet',
            'regionCode': self._region,
            'hl': 'en'
        }
        json_result = self._v3_get_request(path='videoCategories', params=params)
        for item in json_result['items']:
            if item['snippet']['title'].startswith('Music'):
                category_id = int(item['id'])
                break
        return category_id

    def _get_popular_music_videos(self, page_token=None, max_results=None):
        """
        Returns a list of the most popular music videos for that region.
        :param page_token: fetch a concrete page
        :max_results: max results to return
        :return play items, total results, next page token:

        """
        category_id = self._get_music_category_id()
        if max_results:
            maxres = max_results
        else:
            maxres = self._max_results

        params = {
            'part': 'snippet',
            'maxResults': str(maxres),
            'regionCode': self._region,
            'hl': self._language,
            'videoCategoryId': category_id,
            'chart': 'mostPopular'
        }
        if page_token:
            params['pageToken'] = page_token
        res = self._v3_get_request(path='videos', params=params)
        if 'nextPageToken' in res:
            next_page = res['nextPageToken']
        else:
            next_page = None

        return res['items'], res['pageInfo']['totalResults'], next_page


