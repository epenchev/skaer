#!/usr/bin/env python3
#
# Skaer media server
# Copyright (c) 2019 Emil Penchev
#
# Project page:
#   http://skaermedia.org
#
# licensed under GNU GPL version 3 (or later)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>
#


import os
import youtube_dl
import requests
from base64 import b64encode
from skaermedia.server.path_utils import get_streampath


class Streamer(object):

    def __init__(self):
        pass

    def url(self, item_id, provider=None):
        """ Extract the stream url for a given item_id. """

        streamid = str(b64encode(item_id.encode()), 'utf-8')
        if provider:
            target_url = provider.playback_url(item_id)
            self.download_file(target_url, os.path.join(get_streampath(), streamid))
        host = 'localhost'
        port  = '8844'
        return 'http://%s:%s/stream/%s' % (host, port, streamid)

    def download_audio(self):
        ydl_opts = {
            'format': 'best',
            'outtmpl': '/tmp/%(id)s.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192', }],
        }
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download(['https://www.youtube.com/watch?v=%s' % item_id])
        return 'file:/' + os.path.join('/tmp', item_id + '.mp3')

    def download_file(self, url, dstpath, credentials=None):
        """
        Download a file from HTTP url.
        :param url: The source HTTP URL.
        :param dstpath: Destination path to store the downloaded file,
                        if path dosen't exists it will be created.
        :param credentials: A tuple in the form (user, password)
                            if url requires authentication.
        :return:
        """
        kwargs = { 'stream': True }
        if credentials:
            user, password = credentials
            kwargs['auth'] = (user, password)

        with requests.get(url, **kwargs) as r:
            if r.status_code != requests.codes.ok:
                r.raise_for_status()
            os.makedirs(os.path.split(dstpath)[0], exist_ok=True)
            if r.headers['content-type'] in ('text/plain', 'applicaton/xml', 'text/html'):
                openmode = 'w'
            else:
                openmode = 'wb'
            with open(dstpath, openmode) as f:
                if openmode.endswith('b'):
                    for chunk in r.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                else:
                    f.write(r.text)
