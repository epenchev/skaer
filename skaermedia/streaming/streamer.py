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
from skaermedia.server.path_utils import get_streampath


class Streamer(object):

    def __init__(self):
        pass

    def url(self, item_id):
        """ Extract the stream url for a given item.
            Item is stream item object.
        """

        target_path = os.path.join(get_streampath(), item_id)
        ydl_opts = {
            'format': 'best',
            'outtmpl': target_path,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192', }],
        }
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([item_id])

        host = 'localhost'
        port  = '8844'
        return 'http://%s:s/stream/%s' % (host, port, item.id)
