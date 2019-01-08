from .provider import *

__all__ = ['get', 'get_classes']


_ALL_CLASSES = [
    klass for name, klass in globals().items() if name.endswith('Provider')
]


def get(name):
    """ Returns the provider class with the given name. """
    return globals()[name]

def get_classes():
    """ Return the list with all provider classes. """
    return _ALL_CLASSES

