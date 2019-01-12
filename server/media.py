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


import providers


class MediaManager(object):
    """ Manages all media objects (cloud sources, provider sources, disk sources)."""
    def __init__(self):
        self._load_providers()

    def _load_providers(self):
        """ Create an instance of every provider and mapped to a unique id. """
        self._providers_map = {}
        provid = 1
        klasses = providers.get_classes()
        for cls in klasses:
            self._providers_map[provid] = cls()
            provid += 1

    @property
    def providers_map(self):
        return self._providers_map

