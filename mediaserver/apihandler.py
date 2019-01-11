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

"""
This class provides the api to talk to the client.
It will then call the media model, to get the
requested information.
"""

import os  # shouldn't have to list any folder in the future!
import json
import cherrypy
import codecs
import re
import sys
from mediaserver import media

@cherrypy.expose
class ApiHandler(object):
    _media = media.MediaManager()

    @classmethod
    def mount(cls, mountpath, config=None):
        """ Mount api handler for a given resource. """
        if not config:
            config = {
                mountpath : {
                    'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
                    'tools.sessions.on': True,
                    'tools.response_headers.on': True,
                    'tools.response_headers.headers': [('Content-Type', 'application/json')],
                }})
        cherrypy.tree.mount(cls(), mountpath, config=config)

    def check_auth(self, handler):
        """ Check if resource needs authorization. """
        # Authorize if not explicitly deactivated        
        needs_auth = not ('noauth' in dir(handler) and handler.noauth)
        if needs_auth and not self.is_authorized():
            raise cherrypy.HTTPError(401, 'Unauthorized')
    

class ProviderHandler(ApiHandler):
    def __init__(self):
        self._media = ApiHandler._media

    @cherrypy.tools.json_out()
    def providers_list():
        providers = []
        for provid, prov in self._media.providers_map.items():
            providers.append({
                'id'      : provid
                'name'    : prov.get_info()['name']
                'cover'   : info['cover_image'],
                'category': info['category']
                'descr'   : info['description']
                })
        return providers

    def GET(self):
        return self.providers_list()


class ProviderItemsHandler(object):
    def __init__(self):
        self._media = ApiHandler._media

    @cherrypy.tools.json_out()
    def provider_items():
        if 'provid' not in cherrypy.request.params:
            raise cherrypy.HTTPError(404)

        provid = cherrypy.request.params['provid']
        if provid not in self._media.providers_map:
            raise cherrypy.HTTPError(404)

        prov_items = []
        items_list = self._media.providers_map['provid'].items()
        for _id, details in items_list:
            prov_items.append({
                'id'    : _id,
                'provid': provid,
                'title' : details['title'],
                'cover' : details['cover'],
                'descr' : details['description']
                })
        return prov_items

    def GET(self):
        return self.provider_items()


@cherrypy.expose
class HttpHandler(object):
    def __init__(self):
        ProviderHandler.mount('/providers') 
        ProviderItemsHandler.mount('/providerItems')

    def GET(self):
        # Requests for the rootpath are always redirected to the ui.
        if cherrypy.request.path_info == '/':
            raise cherrypy.HTTPRedirect('/res', 302)

