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


import cherrypy

from mediaserver import configuration as cfg
config = None


def start_server():
    """ Initializes and starts Skaer media server. """
    SkaerMedia()


class SkaerMedia:
    """Sets up services (configuration, database, etc) and starts the server"""
    def __init__(self):
        self.setup_config()

        if config['media.basedir'] is None:
            print(_("Invalid basedir. Please provide a valid basedir path."))
            sys.exit(1)
        else:
            log.debug("Basedir is %r", config['media.basedir'])

        signal.signal(signal.SIGTERM, SkaerMedia.stop_and_cleanup)
        signal.signal(signal.SIGINT, SkaerMedia.stop_and_cleanup)
        if os.name == 'posix':
            signal.signal(signal.SIGHUP, SkaerMedia.stop_and_cleanup)

        SkaerMedia.create_pid_file()
        self.start_server(httphandler.HTTPHandler(config))
        SkaerMedia.delete_pid_file()


    @staticmethod
    def stop_and_cleanup(signal=None, stackframe=None):
        """Delete the process id file and exit"""
        SkaerMediaServer.delete_pid_file()
        print('Exiting...')
        sys.exit(0)


    @classmethod
    def create_pid_file(cls):
        """create a process id file, exit if it already exists"""
        if pathprovider.pidFileExists():
            with open(pathprovider.pidFile(), 'r') as pidfile:
                try:
                    if not sys.platform.startswith('win'):
                        # this call is only available on unix systems and throws
                        # an OSError if the process does not exist.
                        os.getpgid(int(pidfile.read()))
                    sys.exit(_('Process id file %s already exists., you can delete this file and restart SkaerMS.' 
                            % pathprovider.pidFile())
                except OSError:
                    print('Stale process id file, removing.')
                    cls.delete_pid_file()
        with open(pathprovider.pidFile(), 'w') as pidfile:
            pidfile.write(str(os.getpid()))

 
    @classmethod
    def delete_pid_file(cls):
        """Delete the process id file, if it exists"""
        if pathprovider.pidFileExists():
            os.remove(pathprovider.pidFile())
        else:
            print(_("Error removing pid file, doesn't exist!"))


    def setup_config(self):
        """ Updates the internal configuration using the following hierarchy:
            override_dict > file_config > default_config
        """
        defaults = cfg.from_defaults()
        filecfg = cfg.from_configparser(pathprovider.configurationFile())
        custom = defaults.replace(filecfg, on_error=log.e)
        if override_dict:
            custom = custom.replace(override_dict, on_error=log.e)
        global config
        config = custom


    def start_server(self, httphandler):
        """use the configuration to setup and start the cherrypy server
        """
        cherrypy.config.update({'log.screen': True})
        ipv6_enabled = config['server.ipv6_enabled']
        if config['server.localhost_only']:
            socket_host = "::1" if ipv6_enabled else "127.0.0.1"
        else:
            socket_host = "::" if ipv6_enabled else "0.0.0.0"

        resourcedir = os.path.abspath(pathprovider.getResourcePath('res'))

        if config['server.ssl_enabled']:
            cert = pathprovider.absOrConfigPath(config['server.ssl_certificate'])
            pkey = pathprovider.absOrConfigPath(config['server.ssl_private_key'])
            cherrypy.config.update({
                'server.ssl_certificate': cert,
                'server.ssl_private_key': pkey,
                'server.socket_port': config['server.ssl_port'],
            })
            # Create second server for redirecting http to https:
            redirecter = cherrypy._cpserver.Server()
            redirecter.socket_port = config['server.port']
            redirecter._socket_host = socket_host
            redirecter.thread_pool = 10
            redirecter.subscribe()
        else:
            cherrypy.config.update({
                'server.socket_port': config['server.port'],
            })

        cherrypy.config.update({
            'log.error_file': os.path.join(
                pathprovider.getUserDataPath(), 'server.log'),
            'environment': 'production',
            'server.socket_host': socket_host,
            'server.thread_pool': 30,
            'tools.sessions.on': True,
            'tools.sessions.timeout': int(config.get('server.session_duration', 60 * 24)),
        })

        if not config['server.keep_session_in_ram']:
            sessiondir = os.path.join(
                pathprovider.getUserDataPath(), 'sessions')
            if not os.path.exists(sessiondir):
                os.mkdir(sessiondir)
            cherrypy.config.update({
                'tools.sessions.storage_type': "file",
                'tools.sessions.storage_path': sessiondir,
            })
        basedirpath = config['media.basedir']
        if sys.version_info < (3,0):
            basedirpath = codecs.encode(basedirpath, 'utf-8')
            scriptname = codecs.encode(config['server.rootpath'], 'utf-8')
        else:
            if needs_serve_file_utf8_fix:
                # fix cherrypy unicode issue (only for Python3)
                # see patch to cherrypy.lib.static.serve_file way above and
                # https://bitbucket.org/cherrypy/cherrypy/issue/1148/wrong-encoding-for-urls-containing-utf-8
                basedirpath = codecs.decode(codecs.encode(basedirpath, 'utf-8'), 'latin-1')
            scriptname = config['server.rootpath']
        cherrypy.tree.mount(
            httphandler, scriptname,
            config={
                '/res': {
                    'tools.staticdir.on': True,
                    'tools.staticdir.dir': resourcedir,
                    'tools.staticdir.index': 'index.html',
                    'tools.caching.on': False,
                    'tools.gzip.mime_types': ['text/html', 'text/plain', 'text/javascript', 'text/css'],
                    'tools.gzip.on': True,
                },
                '/serve': {
                    'tools.staticdir.on': True,
                    'tools.staticdir.dir': basedirpath,
                    # 'tools.staticdir.index': 'index.html',    if ever needed: in py2 MUST utf-8 encode
                    'tools.staticdir.content_types': MEDIA_MIMETYPES,
                    'tools.encode.on': True,
                    'tools.encode.encoding': 'utf-8',
                    'tools.caching.on': False,
                    'tools.cm_auth.on': True,
                    'tools.cm_auth.httphandler': httphandler,
                },
                '/favicon.ico': {
                    'tools.staticfile.on': True,
                    'tools.staticfile.filename': resourcedir + '/img/favicon.ico',
                }})
        api.v1.mount('/api/v1')
        log.i(_('Starting server on port %s ...') % config['server.port'])

        cherrypy.lib.caching.expires(0)  # disable expiry caching
        cherrypy.engine.start()
        cherrypy.engine.block()


def _cm_auth_tool(httphandler):
    if not httphandler.isAuthorized():
        raise cherrypy.HTTPError(403)
cherrypy.tools.cm_auth = cherrypy.Tool(
    'before_handler', _cm_auth_tool, priority=70)
    # priority=70 -->> make tool run after session is locked (at 50)


