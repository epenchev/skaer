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



class RouterError(Exception):
    """ An exception for the API Router errors. """

    def __init__(self, message):
        Exception.__init__(self, )
        self._message = message

    @property
    def message(self):
        return self._message


class Router(object):
    """
    Automate the process of routing different Rest API calls
    based on HTTP method and path.
    """
    def __init__(self):
        self._handlers = { 'get': {}, 'post': {}, 'put': {}, 'delete': {} }
 
    def lookup(self, method, path):
        """
        Lookup API call by HTTP method and path.
        """
        if method not in self._handlers:
            raise RouterError('Unknown HTTP method [%s]' % method)
        try:
            return self._handlers[method][path]
        except KeyError:
            raise RouterError('Path not registered [%s]' % path)

    def get(self, path):
        """ A decorator method to register a GET API call. """
        def _decorator(func):
            self._handlers['get'][path] = func
            return func
        return _decorator
    
    def post(self, path):
        """ A decorator method to register a POST API call. """
        def _decorator(func):
            self._handlers['post'][path] = func
            return func
        return _decorator

    def put(self, path):
        """ A decorator method to register a PUT API call. """
        def _decorator(func):
            self._handlers['put'][path] = func
            return func
        return _decorator

    def delete(self, path):
        """ A decorator method to register a DELETE API call. """
        def _decorator(func):
            self._handlers['delete'][path] = func
            return func
        return _decorator


