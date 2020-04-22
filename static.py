import cherrypy
from cherrypy.lib.static import serve_file

import os.path
import sqlite3

class Root:
    def __init__(self):
        self.db = sqlite3.connect("file::memory:?cache=shared")
        c = self.db.cursor()
        c.execute("CREATE TABLE urlmap(urlid varchar(64), url varchar(255))")
        c.execute("INSERT INTO urlmap VALUES('id1','http://localhost')")
        self.db.commit()

    @cherrypy.expose
    def index(self):
        print('Connecting do db ..')
        conn = sqlite3.connect("file::memory:?cache=shared")
        c = conn.cursor()
        c.execute("SELECT * FROM urlmap")
        print(c.fetchone())
        #return serve_file(os.path.join(static_dir, name))
        return ('Hi there ')


class App:
    @cherrypy.expose
    def index(self):
        return 'Hello World'

if __name__=='__main__':
    static_dir = os.path.dirname(os.path.abspath(__file__))  # Root static dir is this file's directory.

    cherrypy.config.update( {  # I prefer configuring the server here, instead of in an external file.
            'server.socket_host': '0.0.0.0',
            'server.socket_port': 8844,
        } )
    conf = {
        '/': {  # Root folder.
            #'tools.staticdir.on':   True,  # Enable or disable this rule.
            #'tools.staticdir.root': static_dir,
            #'tools.staticdir.dir':  '',
        }
    }

    cherrypy.quickstart(Root(), '/', config=conf)  # ..and LAUNCH ! :)
























