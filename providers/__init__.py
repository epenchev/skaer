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

