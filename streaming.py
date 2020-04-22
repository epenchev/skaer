#
# skaer media streamer
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


import cherrypy
import requests
import db_utils
import contextlib
import uuid


class Streamer(object):
    """ Stream various media sources. """

    _obj_instance = None

    @staticmethod
    def instance():
        if not Streamer._obj_instance:
            Streamer._obj_instance = Streamer()
        return Streamer._obj_instance

    def __init__(self):
        self._init_db()

    def _init_db(self):
        self._db = db_utils.Sqlite("file::memory:?cache=shared", in_mem=True)
        self._db.execute("CREATE TABLE urlmap(_id varchar(32), url varchar(255))")

    def attach_url(self, url):
        """ 
        Map a streaming url to a unique reference id.

        """
        _id = str(uuid.uuid3(uuid.NAMESPACE_URL, url).hex)
        self._db.execute("INSERT INTO urlmap VALUES(?, ?)", (_id, url))
        return _id

    def detach_url(self, _id):
        self._db.execute("DELETE FROM urlmap where _id=?", (_id,))

    def get_url(self, _id):
        result = self._db.execute("SELECT url FROM urlmap where _id=?", (_id,))
        url = result[0][0]
        return url

    @cherrypy.expose
    def index(self, **kwargs):
        range_header = None
        if 'Range' in cherrypy.request.headers:
            range_header = {'Range' : cherrypy.request.headers['Range']}

        stream_url = self.get_url(kwargs['id'])
        resp = requests.get(stream_url, headers=range_header, stream=True)
        if resp.status_code != requests.codes.ok:
            resp.raise_for_status()

        # If not in download mode trasmit media streaming headers.
        if not kwargs.get('download', False):
            cherrypy.response.headers.update(resp.headers)
        else:
            cherrypy.response.headers.update({'Content-Type': 'application/octet-stream',
                                              'Content-Disposition': 'attachment; filename=\"test.mp3\"'}) 
        def content(resp):
            for chunk in resp.iter_content(chunk_size=8192):
                yield chunk
            resp.close()
            # TODO detach url when done

        return content(resp)
    index._cp_config = {'response.stream': True}
  
    @cherrypy.expose
    def download(self):
        pass

