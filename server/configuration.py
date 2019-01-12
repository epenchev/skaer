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


def load_config():
    return from_defaults()


def from_defaults():
    """ Load default configuration. """

    config = dict()

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

    # This will load parts of the database into memory for improved
    # performance. This option should only be used on systems with
    # sufficient memory, because it will hurt the performance otherwise.
    config['search.load_file_db_into_memory'] = False

    # MAXSHOWFILES specifies how many files and folders should
    # be shown at the same time. E.g. if you open a folder
    # with more than MAXSHOWFILES, the files will be grouped
    # according to the first letter in their name.
    # 100 is a good value, as a CD can have up to 99 tracks for example.
    config['browser.maxshowfiles'] = 100

    # Only use the media database, never the filesystem, for content
    # lookups in browser and search. Useful if the media files reside
    # on an external hard drive or behind a slow network connection.
    config['browser.pure_database_lookup'] = False

    # The port the server will listen to.
    config['server.port'] = 8080

    # When set to true, the server will listen on a IPv6
    # socket instead of IPv4
    config['server.ipv6_enabled'] = False

    # When localhost_only is set to true, the server will not
    # be visible in the network and only play music on the
    # same computer it is running on.
    # Activating this option binds the server to IP 127.0.0.1 or
    # [::1], depending on whether server.ipv6_enabled is true.
    # The server should also be reachable as "localhost" in any case.
    config['server.localhost_only'] = False

    # When localhost_auto_login is set to "True", the server will
    # not ask for credentials when using it locally. The user will
    # be automatically logged in as admin.
    config['server.localhost_auto_login'] = False

    # Duration in minutes of the user sessions. Note that this
    # will not affect auto logged-in users.
    config['server.session_duration'] = 60 * 24
    return config

def from_dict(mapping):
    """ Load configuration from dictionary. """
    # configuration.from_mapping()
    pass

def from_list(properties):
    """ Load configuration from list of properties. """
    # configuration.from_properties(properties)
    pass

def to_list(cfg):
    """ Alias for :meth:`Configuration.to_properties`."""
    # cfg.to_properties()

def to_mapping(cfg):
    """ Configuration to mapping object (dict). """
    pass


