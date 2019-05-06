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
import providers

class HttpHandler(object):
    """ Handling all HTTP requests for static resources 
        and REST API calls.
    """

    def __init__(self, config):
        self.handlers = {
            'providers': self.api_providers,
            'providerItems': self.api_provider_items,
             #'collections' : self.api_collections,
             #'playlists': self.api_playlists,
             #'search': self.api_search,
             #'collectionItems': self.api_collection_items,
             #'playlistItems': self.api_playlist_items,
        }
        self._config = config

    @cherrypy.expose
    def index(self):
        """ Serves / resource. """
        if cherrypy.request.path_info == '/':
            raise cherrypy.HTTPRedirect('/res', 302)

    @cherrypy.expose
    def api(self, *args, **kwargs):
        """ Calls the appropriate api function handler from the handlers
            dict, if available otherwise error is returned.

        """
        action = args[0] if args else ''
        if not action in self.handlers:
            raise cherrypy.HTTPError(404)
        handler = self.handlers[action]
        cherrypy.response.headers['Access-Control-Allow-Origin'] = '*'
        return handler(**kwargs)

    def api_providers(self):
        """ Return a list with all media providers and provider details
            (name, description ..)

        """
        media_providers = []
        prov_map = providers.all()
        for prvid, prv in prov_map.items():
            media_providers.append(dict(prv.get_info(), id=prvid))
        cherrypy.response.headers['Content-Type'] = 'application/json'
        return json.dumps(media_providers)

    def api_provider_items(self, provid):
        """ Get all entries/items (PlayLists, PlayItems) 
            for a given media provider.

        """
        if 'provid' in cherrypy.request.params:
            provid = int(provid)
        else:
            raise cherrypy.HTTPError(404)

        prov_map = providers.all()
        if provid not in prov_map:
            raise cherrypy.HTTPError(404)
        entries = []
        elist, total_res, page_token = prov_map[provid].entries()
        for details in elist:
            entries.append(dict(details, provid=provid))
        cherrypy.response.headers['Content-Type'] = 'application/json'
        return json.dumps(entries)

    def api_search(self, type, id, qtext):
        """ Get all entries (PlayLists, PlayItems)
            for a given media provider.

        """
        if 'provid' in cherrypy.request.params:
            provid = int(provid)
        else:
            raise cherrypy.HTTPError(404)
        if provid not in self._media.providers_map:
            raise cherrypy.HTTPError(404)
        prov_map = providers.all()
        result = prov_map[provid].search(qtext)
        print(result)
        return json.dumps(result)

