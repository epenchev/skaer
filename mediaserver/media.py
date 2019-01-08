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


class MediaError(Exception):
    """ Base class for media errors. """
    def __init__(self, msg='')
        super().__init__(msg)


class Provider(object):
    """ Media provider instance. 
        Gives acces to various media providers ex. youtube """
    def __init__(self, provid, provider):
        self._instance = provider
        self._provid = provid

    @property
    def items(self):
        return self._instance.get_items()

    @property
    def info(self):
        return self._instance.get_info()

    @property
    def provid(self):
        return self._provid


class ProviderItem(object):
    def __init__(self, provider):
        self._provider = provider



class Media(object):
    """ Manages all media objects (cloud sources, provider sources, disk sources)."""
    def __init__(self):
        self._load_providers()

    def _load_providers(self):
        """ Load media providers. """
        self._providers = {}
        provid = 1
        classes = provider.get_classes()
        for cls in classes:
            self._providers[provid] = MediaProvider(cls(self))
            provid += 1

    @property
    def providers(self):
        """ Get a maping with all media providers """
        return self._providers.items()

    def get_provider(self, provid):
        """ Lookup a Provider instance from id """
        if provid not in self._providers:
            raise MediaError('No provider with this id : [%s]' % provid)
        return self_.providers[provid]

