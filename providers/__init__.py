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



from .sources import *

__all__ = ['all', 'get']

# Get the class for every provider from the globals dictionary.
_all_classes = [
    klass for name, klass in globals().items() if name.endswith('Provider')
]

# Load all providers and create an instance for every provider.
_providers_map = { 
    (prvid + 1): cls() for prvid, cls in enumerate(_all_classes) 
}


def all():
    """ Return a dictionary object containing 
        every provider instance mapped with unique id.
    """
    return _providers_map


def get(provider_id):
    """ Lookup provider by provider id. """
    return _providers_map[provider_id]

