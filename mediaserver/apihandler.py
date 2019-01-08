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
It will then call the model, to get the
requested information.
"""

import os  # shouldn't have to list any folder in the future!
import json
import cherrypy
import codecs
import re
import sys

@cherrypy.expose
class HttpApiHandler(object):
    def __init__(self):
        self.handlers = {
            'search': self.api_search,
            'rememberplaylist': self.api_rememberplaylist,
            'saveplaylist': self.api_saveplaylist,
            'loadplaylist': self.api_loadplaylist,
            'generaterandomplaylist': self.api_generaterandomplaylist,
            'deleteplaylist': self.api_deleteplaylist,
            'getmotd': self.api_getmotd,
            'restoreplaylist': self.api_restoreplaylist,
            'getplayables': self.api_getplayables,
            'getuserlist': self.api_getuserlist,
            'adduser': self.api_adduser,
            'userdelete': self.api_userdelete,
            'userchangepassword': self.api_userchangepassword,
            'showplaylists': self.api_showplaylists,
            'logout': self.api_logout,
            'downloadpls': self.api_downloadpls,
            'downloadm3u': self.api_downloadm3u,
            'getsonginfo': self.api_getsonginfo,
            'getencoders': self.api_getencoders,
            'getdecoders': self.api_getdecoders,
            'transcodingenabled': self.api_transcodingenabled,
            'updatedb': self.api_updatedb,
            'getconfiguration': self.api_getconfiguration,
            'compactlistdir': self.api_compactlistdir,
            'listdir': self.api_listdir,
            'fetchalbumart': self.api_fetchalbumart,
            'fetchalbumarturls': self.api_fetchalbumarturls,
            'albumart_set': self.api_albumart_set,
            'heartbeat': self.api_heartbeat,
            'getuseroptions': self.api_getuseroptions,
            'setuseroption': self.api_setuseroption,
            'changeplaylist': self.api_changeplaylist,
            'downloadcheck': self.api_downloadcheck,
            'setuseroptionfor': self.api_setuseroptionfor,
        }

    def GET(self):
        # Requests for the rootpath are always redirected to the ui.
        if cherrypy.request.path_info == '/':
            raise cherrypy.HTTPRedirect('/res', 302)
        action = cherrypy.path_info.strip('/') 
        if not action in self._handlers:
            raise cherrypy.HTTPError(status=404)
        api_call(action)


    def check_auth(self, handler):
        """ Check if resource needs authorization. """
        # Authorize if not explicitly deactivated
        needs_auth = not ('noauth' in dir(handler) and handler.noauth)
        if needs_auth and not self.is_authorized():
            raise cherrypy.HTTPError(401, 'Unauthorized')


    def api_call(self, handler):
        """ Calls the appropriate handler from the handlers dict, if available.
            Check if handler needs authentification to work.
        """
        handler = self._handlers[action]
        check_auth(handler)
        handler_args = {}
        if 'data' in kwargs:
            handler_args = json.loads(kwargs['data'])
        is_binary = ('binary' in dir(handler) and handler.binary)
        if is_binary:
            return handler(**handler_args)
        else:
            return json.dumps({'data': handler(**handler_args)})

    
       async def handle_get_all_collections(self, request):
        col_out = []
        collections = self.get_collections()
        for col_id, col_name in collections.items():
            info = self.get_collection_info(col_id)
            col_out.append({
                    'id' : col_id,
                    'name' : col_name,
                    'cover_image' : info['cover_image'],
                    'category' : info['category']
                    }
            )
        return web.json_response(col_out)

       async def handle_get_collection(self, request):
        return web.json_response(self.get_collection_info(int(request.match_info['id'])))

    async def handle_get_collection_items(self, request):
        return web.json_response(self.get_collection_items(int(request.match_info['id'])))

    async def handle_get_collection_item(self, request):
        item = self.get_collection_item(request.match_info['id'], request.match_info['item'])
        return web.json_response(item)

    def setup_api_routes(self):
        # User interface
        self.router.add_get(r'/', self.handle_redirect_ui)
        self.router.add_static(r'/ui', 'ui/', name='ui')
        # Media Collections API
        self.router.add_get(r'/collections', self.handle_get_all_collections)
        self.router.add_get(r'/collections/{id}', self.handle_get_collection)
        self.router.add_get(r'/collections/{id}/items', self.handle_get_collection_items)
        self.router.add_get(r'/collections/{id}/items/{item_id}', self.handle_get_collection_item)
        # self.router.add_get(r'/collections/{id}/play/{item_id}', self.handle_play_collection_item)
