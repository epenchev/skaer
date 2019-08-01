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
import codecs


def is_windows():
    return sys.platform.startswith('win')


def is_linux():
    return sys.platform.startswith('linux')


def is_macosx():
    return sys.platform.startswith('darwin')


def get_basepath():
    basepath = ''
    if is_linux():
        base_folder = '.skaer'
        if 'HOME' in os.environ:
            basepath = os.path.join(os.environ['HOME'], base_folder)
        else:
            basepath = os.path.join(os.path.expanduser('~'), '.local', 'share', base_folder)
    elif is_windows():
        base_folder = 'skaer'
        basepath = os.path.join(os.environ['APPDATA'], base_folder)
    elif is_macosx():
        base_folder = '.skaer'
        basepath = os.path.join(os.path.expanduser('~'), 'Library', 'Application Support', base_folder)

    if not basepath:
        basepath = fallbackpath()

    if not os.path.exists(basepath):
        os.makedirs(basepath)

    return basepath


def fallbackpath():
    base_folder = 'skaer'
    return os.path.join(os.path.expanduser('~'), base_folder)


def pid_file():
    pid_filename = 'skaer.pid'
    return os.path.join(get_basepath(), pid_filename)


def pid_file_exists():
    return os.path.exists(pidfile())


def license_file():
    owndir = os.path.dirname(__file__)
    basedir = os.path.split(owndir)[0] or '.'
    basedir = os.path.abspath(basedir)
    return os.path.join(basedir, 'COPYING')


def assure_folder_exists(folder, subfolders=['']):
    for subfolder in subfolders:
        dirpath = os.path.join(folder, subfolder)
        if not os.path.exists(dirpath):
            os.makedirs(dirpath)


def readres(path):
    with codecs.open(get_resourcepath(path), encoding='utf-8') as f:
        return f.read()


def get_resourcepath(dirname):
    return os.path.abspath(os.path.join(os.path.dirname( __file__  ), os.pardir, dirname))


def filename(path, pathtofile=False):
    if pathtofile:
        return os.path.split(path)[0]
    else:
        return os.path.split(path)[1]


def stripext(filename):
    if '.' in filename:
        return filename[:filename.rindex('.')]
    return filename


def get_streampath():
    """ Path to store media stream resources. """
    streampath = os.path.join(get_basepath(), 'stream')
    if not os.path.exists(streampath):
        os.makedirs(streampath)
    return streampath


def get_databasepath():
    """ Location to the global database file. """
    dbfile = 'datastore.db'
    return os.path.join(get_basepath(), dbfile)