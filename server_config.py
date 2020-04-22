#!/usr/bin/env python3
#
# skaer media streamer
# Copyright (c) 2019 Emil Penchev
#
# Project page:
#   http://skae.org
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


def load():
    return from_defaults()


def from_defaults():
    """ Load default configuration. """

    config = dict()

    # Database datasource name.
    # Includes database name, server, port, user and port to connect to.
    local_dsn = 'dbname=skaer host=localhost user=emil password=emil'
    config['db.dsn'] = os.environ.get('DATABASE_URL', local_dsn)

    # enables automatic live transcoding, 
    # This requires you to have the appropriate codecs installed.
    # Please note that transcoding will significantly increase the stress on the CPU!
    config['media.transcode'] = False

    # Tries to fetch the album cover from various locations in the web,
    # if no image is found locally. By default it will be fetched from iTunes.
    # They will be shown next to folders that qualify as a possible album.
    config['media.fetch_album_art'] = False

    # Maximum size in bytes of all files to be downloaded in one zipfile.
    # Defaults to 250 MBytes.
    config['media.maximum_download_size'] = 1024*1024*250

    # MAXRESULTS sets the maximum amount of search results
    # to be displayed. If MAXRESULTS is set to a higher value,
    # the search will take longer, but will also be more accurate.  
    config['search.maxresults'] = 20
   
    # The port the server will listen to.
    config['server.port'] = int(os.environ.get('PORT', 8844))

    # Duration in minutes of the user sessions. Note that this
    # will not affect auto logged-in users.
    config['server.session_duration'] = 60 * 24

    # IP v6 setting.
    config['server.ipv6_enabled'] = False


    return config


