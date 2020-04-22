import json
import psycopg2
from contextlib import closing


class YoutubeObjectError(Exception):
    """ An error from YoutubeObjects. """

    def __init__(self, errdetail):
        self.errdetail = errdetail



class YoutubeObjects(object):
    """ Manage youtube playlists and channels. """

    def __init__(self, dsn, app_config):
        self._dsn = dsn
        # Set up database
        self.query("CREATE TABLE IF NOT EXISTS youtube_app (        \
                                           id varchar(5) UNIQUE,    \
                                           config text DEFAULT '',  \
                                           playlists varchar(64)[], \
                                           channels varchar(64)[]   \
                   );                                               \
                   INSERT INTO youtube_app                          \
                   VALUES('cfg', %s, ARRAY[]::varchar[], ARRAY[]::varchar[])   \
                   ON CONFLICT (id) DO NOTHING;                                \
                                                                               \
                   INSERT INTO youtube_app                                     \
                   VALUES('pls', '', ARRAY[]::varchar[], ARRAY[]::varchar[])   \
                   ON CONFLICT (id) DO NOTHING;                                \
                                                                               \
                   INSERT INTO youtube_app                                     \
                   VALUES('chan', '', ARRAY[]::varchar[], ARRAY[]::varchar[])  \
                   ON CONFLICT (id) DO NOTHING;", (json.dumps(app_config),))

    def config(self):
        """ 
        Get app config.

        """
        result = self.result_query("SELECT config FROM youtube_app WHERE id='cfg'")
        app_config = json.loads(result[0])
        return app_config

    def result_query(self, query, args=[], fetchone=True):
        """
        Execute database query and return result.
        
        """
        with closing(psycopg2.connect(self._dsn, sslmode='require')) as con, con:
            with con.cursor() as cur:
                cur.execute(query, args)
                if fetchone:
                    return cur.fetchone()
                else:
                    return cur.fetchall()

    def query(self, query, args=[]):
        """
        Execute database query without result.
        
        """

        with closing(psycopg2.connect(self._dsn, sslmode='require')) as con, con:
            with con.cursor() as cur:
                cur.execute(query, args) 

    def add_playlist(self, url):
        """
        Import/add Youtube playlist from url.
        Playlist must be public.

        """
        try:
            list_id = url.split('list=')[1]
            if not list_id.isalnum():
                raise YoutubeObjectError('Inalid playlist id')
        except Exception as err:
            raise YoutubeObjectError('Invalid playlist url')
 
        with closing(psycopg2.connect(self._dsn, sslmode='require')) as con, con:
            with con.cursor() as cur:
                cur.execute("SELECT playlists FROM youtube_app \
                             WHERE %s = ANY(playlists) and id = 'pls'", (list_id,))
                if not cur.fetchone():
                    cur.execute("UPDATE youtube_app SET playlists = \
                                 array_append(playlists, %s) WHERE id = 'pls'", 
                               (list_id,))
                else:
                    raise YoutubeObjectError('PlaylistExists')

    def add_channel(url):
        """
        Import/add Youtube channel from url.
        Channel must be public.

        """
        pass

    def del_playlist(list_id):
        """
        Remove/delete Youtube playlist from the DB.


        """
        if not list_id.isalnum():
            raise YoutubeObjectError('Inalid playlist id')
        with closing(psycopg2.connect(self._dsn, sslmode='require')) as con, con:
            with con.cursor() as cur:
                cur.execute("UPDATE youtube_app SET playlists = \
                             array_remove(playlists, %s) WHERE id = 'pls'", (list_id,))

    def del_channel(chan_id):
        """
        Remove/delete Youtube channel from the DB.

        """
        pass

    def playlists(self):
        """
        Get all imported playlists (id's).
        
        """
        result = self.result_query("SELECT playlists FROM youtube_app WHERE id='pls'")
        return result[0]

    def channels(self):
        """
        Get all imported channels (id's).
        
        """
        pass



