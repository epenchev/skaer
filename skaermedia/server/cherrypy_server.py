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
import sys
import signal
import cherrypy

from skaermedia.server import configuration, path_utils
from skaermedia.gapi.login import OauthLoginService
from skaermedia.server.api_app import AppInterface

config = None


class HTTP_Handler(object):
    """ Handling all HTTP requests for static resources
        and REST API calls.
    """

    def __init__(self):
        self._api = AppInterface()

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
        path = args[0] if args else ''
        cherrypy.response.headers['Access-Control-Allow-Origin'] = '*'
        cherrypy.response.headers['Content-Type'] = 'application/json'
        return self._api.call(cherrypy.request.method, path, **kwargs)


class CherrypyServer:
    """ Sets up services (configuration, database, etc) and starts the server. """
    def __init__(self):
        global config
        config = configuration.load()

        signal.signal(signal.SIGTERM, CherrypyServer.stop_and_cleanup)
        signal.signal(signal.SIGINT, CherrypyServer.stop_and_cleanup)
        if os.name == 'posix':
            signal.signal(signal.SIGHUP, CherrypyServer.stop_and_cleanup)

        CherrypyServer.create_pid_file()
        self.start_server(HTTP_Handler())
        CherrypyServer.delete_pid_file()

    @staticmethod
    def stop_and_cleanup(signal=None, stackframe=None):
        """ Delete the process id file and exit. """
        # delete pid file
        print('Exiting...')
        sys.exit(0)

    @classmethod
    def create_pid_file(cls):
        """ Create a process id file, exit if it already exists. """
        pass

    @classmethod
    def delete_pid_file(cls):
        """ Delete process id file. """
        pass

    def start_server(self, handler):
        """ Set configuration values and run cherrypy server. """
        cherrypy.config.update({'log.screen': True})
        ipv6_enabled = config['server.ipv6_enabled']
        if config['server.localhost_only']:
            socket_host = "::1" if ipv6_enabled else "127.0.0.1"
        else:
            socket_host = "::" if ipv6_enabled else "0.0.0.0"

        resourcedir = os.path.abspath(path_utils.get_resourcepath('res'))
        cherrypy.config.update({'server.socket_port': config['server.port']})
        cherrypy.config.update({
            'log.error_file': os.path.join(path_utils.get_basepath(), 'server.log'),
            'environment': 'production',
            'server.socket_host': socket_host,
            'server.thread_pool': 30,
            'tools.sessions.on': True,
            'tools.sessions.timeout': int(config.get('server.session_duration', 60 * 24)),
        })

        cherrypy.tree.mount(
            handler, '/', config={
                '/res': {
                    'tools.staticdir.on': True,
                    'tools.staticdir.dir': resourcedir,
                    'tools.staticdir.index': 'index.html',
                    'tools.caching.on': True,
                    'tools.caching.delay': 3600,
                    'tools.gzip.mime_types': ['text/html', 'text/plain', 'text/javascript', 'text/css'],
                    'tools.gzip.on': True,
                },
                '/api': {
                    'tools.caching.on': False,
                    'tools.encode.text_only': False, # Will encode all in ('utf8')
                },
                '/stream': {
                    'tools.staticdir.on': True,
                    'tools.staticdir.dir': path_utils.get_streampath(),
                    'tools.caching.on': True,
                    'tools.caching.delay': 3600,
                },
            })

        # Start login service for Google based API's
        glogin = OauthLoginService()
        glogin.run()
        # Run cherrypy engine
        cherrypy.lib.caching.expires(0)  # disable expiry caching
        cherrypy.engine.start()
        cherrypy.engine.block()


def _cm_auth_tool(handler):
    if not handler.isAuthorized():
        raise cherrypy.HTTPError(403)
cherrypy.tools.cm_auth = cherrypy.Tool(
    'before_handler', _cm_auth_tool, priority=70)
    # priority=70 -->> make tool run after session is locked (at 50)
