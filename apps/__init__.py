#
# skaer media streamer
# Copyright (c) 2019 Emil Penchev
#
# Project page:
#   http://skaer.org
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

__all__ = ['all', 'load']

all_apps = None 


def load():
    """
    Get the class for every app from the globals dictionary.
    Load all apps and create an instance for every app.


    """
    global all_apps
    klasses = [klass for name, klass in globals().items() if name.endswith('App')]
    all_apps = [cls() for cls in klasses]



def all():
    """ 
    Return a list containing every app instance.
    """
    global all_apps
    return all_apps

