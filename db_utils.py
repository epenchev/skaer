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


import sqlite3
import psycopg2
from contextlib import closing


class Sqlite(object):
    """ Sqlite common set of database utils. """

    def __init__(self, db_url, in_mem=False):
        self._db_url = db_url
        # If DB is in memory create a persistent connection.
        if in_mem:
            self._db_con = sqlite3.connect(self._db_url)

    def execute(self, query, args=[]):
        """ 
        Executes an SQL statement and return all the results. 
        Wrapper around sqlite3.Cursor.execute.

        """
        with closing(sqlite3.connect(self._db_url)) as con, con:
            with closing(con.cursor()) as cursor:
                cursor.execute(query, args)
                return cursor.fetchall()

    def executescript(self, sql_script):
        """
        Method for executing multiple SQL statements at once.
        Wrapper around sqlite3.Cursor.executescript.

        """
        with closing(sqlite3.connect(self._db_url)) as con, con:
            with closing(con.cursor()) as cursor:
                cursor.executescript(sql_script)

    def executemany(self, query, seq_of_parameters):
        """ 
        Executes an SQL command against all parameter sequences 
        or mappings found in the sequence seq_of_parameters.
        Wrapper around sqlite3.Cursor.executemany.
        """
        with closing(sqlite3.connect(self._db_url)) as con, con:
            with closing(con.cursor()) as cursor:
                cursor.executemany(query, seq_of_parameters)


class PostgreSQL(object):
    """ PostgreSQL python api (psycopg2) wrapper. """

    @staticmethod
    def connect():
        local_dsn = "dbname=skaer host=localhost user=emil passowrd=emil"
        DATABASE_URL = os.environ.get("DATABASE_URL", local_dsn)
        return psycopg2.connect(DATABASE_URL, sslmode="require")

    @staticmethod
    def execute(query, args=[]):
        with closing(PostgreSQL.connect()) as con, con:
            with con.cursor() as cur:
                cur.execute(query, args)
                return cur.fetchall()




