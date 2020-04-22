import os
import json
import youtube_dl
import cherrypy
import requests

import server_config
from apps.youtube_objects import YoutubeObjects, YoutubeObjectError 
from apps.youtube_api import YoutubeDataApi


class YouTubeApp(object):
    """ Youtube streaming application. """

    def __init__(self):
        self.info = {
            'name'        : 'YouTube',
            'path'        : '/youtube',
            'description' : 'App to serve content from Youtube',
            'cover_image' : 'http://localhost:8080/res/images/y-music.jpeg',
        }

        app_config = {
            'api_url' : 'https://www.googleapis.com/youtube/v3/',
            'api_key' : 'AIzaSyC5tw2VneJ1QhPQMTpqGL6yTxsQF2scI4A',
            'lang' : 'en',
            'region': 'BG',
            'max_results': 40
        }

        self.dsn = server_config.load()['db.dsn']
        self.yt_objects = YoutubeObjects(self.dsn, app_config)
        self.data_api = YoutubeDataApi(self.yt_objects.config())

    @cherrypy.expose
    def playlists(self, lid=None):
        """
        List, add and delete youtube playlists.
        Add playlist with POST request and json payload { url: ... }.
        Del playlists with DELETE request and param id=(id of the playlist).
        :return a json output with all the playlists and details:

        """
        try:
            if cherrypy.request.method == 'GET':
                ids = self.yt_objects.playlists()
                if len(ids):
                    return json.dumps(self.data_api.playlists(ids)).encode('utf8')
            elif cherrypy.request.method == 'POST':
                body = cherrypy.request.body.read()
                url = json.loads(body)['url']
                self.yt_objects.add_playlist(url)
                #cherrypy.response.status = '204 No Content'
            elif cherrypy.request.method == 'DELETE':
                if lid.isalnum():
                    self.yt_objects.del_playlist(lid)
                else:
                    raise cherrypy.HTTPError(400, message='InvalidList')
        except YoutubeObjectError as err:
            raise cherrypy.HTTPError(400, message=err.errdetail)

    @cherrypy.expose
    def playlistItems(self, lid, pagetoken=None):
        """
        Retrieve all of the playlist items.
        :param lid: unique id of the playlist.
        :param pagetoken: token to access a given result page with items.
        :return items and next page token if available:

        """
        # Don't care if playlist is in the DB so not checking.
        items, next_pagetoken = self.data_api.playlist_items(lid, pagetoken)
        return json.dumps({'pagetoken': next_pagetoken, 'items': items}).encode('utf8')

    @cherrypy.expose
    def search(self, q):
        """
        Search for any playlists or video.
        :param q search query can be any word or sentence:

        """
        res = self.data_api.search(q)
        return json.dumps(res).encode('utf8')

    @cherrypy.expose
    def channels(self):
        """
        List, add and delete youtube playlists.
        """
        pass

    @cherrypy.expose
    def play(self, v, mode):
        """ 
        Stream youtube video/audio.
        :param v: id of the video to stream.
        :param mode: audio or video for the full multimedia.

        """
        if mode not in ('video', 'audio'):
            raise cherrypy.HTTPError(400, message='Invalid media mode')

        with youtube_dl.YoutubeDL({'quiet': True}) as ydl:
            json_out = ydl.extract_info(v, download=False)

        if mode == 'audio':
            streams = [f for f in json_out['formats'] if 'audio only' in f['format']]
            best_audio = sorted(streams, key=lambda audio: audio['abr'])[0]
            stream_url =  best_audio['url']
            ext = best_audio['ext']
        elif mode == 'video':
            streams = [f for f in json_out['formats'] if f['vcodec'] != 'none' and f['acodec'] != 'none']
            stream_url = streams[0]['url']
            ext = streams[0]['ext']
        # Fetch youtube source stream
        resp = requests.get(stream_url, stream=True)
        if resp.status_code != requests.codes.ok:
            resp.raise_for_status()

        cherrypy.response.headers.update({'Content-Type': '{}/{}'.format(mode, ext)})
        def content(resp):
            for chunk in resp.iter_content(chunk_size=10240):
                yield chunk
            resp.close()
        return content(resp)
    play._cp_config = {'response.stream': True}
 
    @cherrypy.expose
    def download(self, v, mode):
        """
        Download youtube video.
        :param v: id of the video to download.
        :param mode: audio or video for the full multimedia.

        """
        if mode not in ('video', 'audio'):
            raise cherrypy.HTTPError(400, message='Invalid media mode')

        with youtube_dl.YoutubeDL({'quiet': True}) as ydl:
            json_out = ydl.extract_info(v, download=False)

        video_streams = None
        if mode == 'audio':
            filename = json_out['title'] + '.webm'
        else:
            video_streams = [f for f in json_out['formats'] if f['vcodec'] != 'none' and f['acodec'] != 'none']
            filename = json_out['title'] + '.' + video_streams[0]['ext']

        cherrypy.response.headers.update({'Content-Type': 'application/octet-stream',
                                          'Content-Disposition': 'attachment; filename=\"{}\"'.format(filename)})       
        if mode == 'audio':
            ydl_opts = {
                'quiet': True,
                'outtmpl': '/tmp/%(title)s.%(ext)s',
                'format': 'bestaudio/best',
                'extractaudio' : True,
                'audioformat' : 'webm',
            }
            # Youtube has set a bandwith throttling on the audio streams,
            # so it's faster to download the full multimedia localy and extract the audio.
            filepath = os.path.join('/tmp', filename)
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                ydl.download([v])
                if not os.path.exists(filepath):
                    raise cherrypy.HTTPError(404, message='Target file not found')
            def content(path):
                with open(path, 'rb') as fl:
                    while True:
                        chunk = fl.read(10240)
                        if not chunk:
                            break
                        yield chunk
                os.unlink(path) 
            return content(filepath)
        else:
            # Just restream video, not downloading multimedia localy.
            resp = requests.get(video_streams[0]['url'], stream=True)
            if resp.status_code != requests.codes.ok:
                resp.raise_for_status()
            def content(resp):
                for chunk in resp.iter_content(chunk_size=10240):
                    yield chunk
                resp.close()
            return content(resp)
    download._cp_config = {'response.stream': True}


