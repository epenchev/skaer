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


import json
import cherrypy
from server import media


class HttpHandler(object):
    """ Handling all HTTP requests for static resources and REST API calls. """
    def __init__(self, config):
        self._media = media.MediaManager()
        self._config = config

    @cherrypy.expose
    def index(self):
        """ Serves / resource. """
        if cherrypy.request.path_info == '/':
            raise cherrypy.HTTPRedirect('/res', 302)

    @cherrypy.expose
    def providers_list(self):
        """ Return a list with all media providers and provider details
            (name, description ..) 
        """
        providers = []
        for provid, prov in self._media.providers_map.items():
            providers.append(dict(prov.get_info(), id=provid)) 
        return json.dumps(providers)

    @cherrypy.expose
    def provider_entries(self, provid):
        """ Get all entries (PlayLists, PlayItems) for a given media provider. """
        if 'provid' in cherrypy.request.params:
            provid = int(provid)
        else:
            raise cherrypy.HTTPError(404)

        if provid not in self._media.providers_map:
            raise cherrypy.HTTPError(404)
        entries = []
        elist, total_res, page_token = self._media.providers_map[provid].entries()
        for details in elist:
            entries.append(dict(details, provid=provid))
        return json.dumps(entries)

