from .sources import *

_ALL_CLASSES = [
    klass for name, klass in globals().items() if name.endswith('Media')
]


def get_media_classes():
    """ Return the list with all media source classes. """
    return _ALL_CLASSES


def get_media(source_name):
    """Returns the media source class with the given name. """
    return globals()[source_name]
