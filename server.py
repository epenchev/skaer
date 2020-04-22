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


import os
import sys
import signal
import cherrypy
import psycopg2
from contextlib import closing

import apps
from http_api import ServerApi
from server_config import load as load_config
from path_utils import get_resourcepath, get_basepath
from streaming import Streamer


class RootUI(object):
    """ Handle requests for UI static files."""
    @cherrypy.expose
    def index(self, name):
        return serve_file(os.path.join(static_dir, name))


class Server:
    """ Sets up configuration and database and starts the server. """

    def __init__(self):
        self._config = load_config()

        signal.signal(signal.SIGTERM, Server.stop_and_cleanup)
        signal.signal(signal.SIGINT, Server.stop_and_cleanup)
        if os.name == 'posix':
            signal.signal(signal.SIGHUP, Server.stop_and_cleanup)

        self.start_server()

    @staticmethod
    def run():
        Server()

    @staticmethod
    def stop_and_cleanup(signal=None, stackframe=None):
        """ Delete the process id file and exit. """
        # delete pid file
        print('Exiting...')
        sys.exit(0)

    def init_db(self):
        dsn = self._config['db.dsn']
        with closing(psycopg2.connect(dsn, sslmode='require')) as con, con:
            with con.cursor() as cur:
                cur.execute("CREATE TABLE IF NOT EXISTS config(data jsonb)")

    @classmethod
    def create_pid_file(cls):
        """ Create a process id file, exit if it already exists. """
        pass

    @classmethod
    def delete_pid_file(cls):
        """ Delete process id file. """
        pass

    def start_server(self):
        """ Set configuration values and run cherrypy server. """

        cherrypy.config.update({'log.screen': True})
        ipv6_enabled = self._config['server.ipv6_enabled']
        socket_host = "::" if ipv6_enabled else "0.0.0.0"

        self.init_db()
        apps.load()

        resourcedir = os.path.abspath(get_resourcepath('res'))
        cherrypy.config.update({'server.socket_port': self._config['server.port']})
        cherrypy.config.update({
            'log.error_file': os.path.join(get_basepath(), 'server.log'),
            #'environment': 'development', # 'production',
            'server.socket_host': socket_host,
            'server.thread_pool': 30,
            #'tools.sessions.on': True,
            #'tools.sessions.timeout': int(self._config.get('server.session_duration', 60 * 24)),
        })

        # REST Api
        cherrypy.tree.mount(ServerApi(), '/api', config={ 
            '/' : { 
                    'tools.response_headers.on': True,
                    'tools.response_headers.headers': [('Content-Type', 'application/json'),
                                                       ('Access-Control-Allow-Origin', '*')]
                  },
        })

        # media streaming
        cherrypy.tree.mount(Streamer.instance(), '/stream')

        # User interface
        cherrypy.tree.mount(RootUI, '/ui', config={
            '/': {
                    'tools.staticdir.on': True,
                    'tools.staticdir.dir': resourcedir,
                    'tools.staticdir.index': 'index.html',
                    'tools.caching.on': True,
                    'tools.caching.delay': 3600,
                    'tools.gzip.mime_types': ['text/html', 'text/plain', 'text/javascript', 'text/css'],
                    'tools.gzip.on': True
                },
        })

        # Register apps and expose REST API of each app 
        for app in apps.all():
            cherrypy.tree.mount(app, app.info['path'], config={ 
                '/' : { 
                        'tools.response_headers.on': True,
                        'tools.response_headers.headers': [('Content-Type', 'application/json'),
                                                           ('Access-Control-Allow-Origin', '*')]
                      },
            })

        # Run cherrypy engine
        cherrypy.lib.caching.expires(0)  # disable expiry caching
        cherrypy.engine.start()
        cherrypy.engine.block()

