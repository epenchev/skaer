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
    def __init__(self, config=None):
        self.config = config


    def GET(self):
        print(cherrypy.request.path_info)
        print('index is called')
        raise cherrypy.HTTPRedirect('/res', 302)


