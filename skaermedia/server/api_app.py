import os
import json
from skaermedia import providers
from skaermedia.server import path_utils
from skaermedia.gapi import login as glogin
from skaermedia.server.api_router import Router
from skaermedia.streaming import streamer


class AppInterface(object):
    """ Application interface exposed for public use. """

    router = Router()

    def call(self, method, path, **kwargs):
        """ Lookup api function handler for method and path,
            if no handler is registered an error is returned.
            :param method: HTTP method (GET, POST ..)
            :param path: URI path for this request.
            :param kwargs: API call supplied arguments.

        """
        api_handler = AppInterface.router.lookup(method.lower(), path)
        return api_handler(self, **kwargs)

    @router.get('providers')
    def get_providers(self):
        """ Return a list with all media providers and provider details
            (name, description ..)

        """
        media_providers = []
        provs = providers.all()
        for prvid, prov in provs.items():
            media_providers.append(dict(prov.get_info(), id=prvid))
        return json.dumps(media_providers)

    @router.get('playlists')
    def get_playlists(self, provider_id=None):
        """ List/get all Playlists.
            If provider_id is set return playlists for a given media provider.

        """
        playlists = []
        if provider_id:
            prov = providers.get(int(provider_id))
            entries_list = prov.playlists()
            for details in entries_list:
                playlists.append(dict(details, provid=provider_id))
        return json.dumps(playlists)

    @router.get('playlistItems')
    def get_playlist_items(self, playlist_id, provider_id=None):
        """ Return all the items in a playlist."""

        play_items = []
        if provider_id:
            prov = providers.get(int(provider_id))
            play_items = prov.playlist_items(playlist_id)
        return json.dumps(play_items)

    @router.get('playstream')
    def play_item(self, item_id):
        """ Stream media item.
            item_id can presentet as url.
        """

        s = streamer.Streamer()
        return json.dumps(s.url(item_id))

    @router.get('google_auth')
    def get_google_auth(self):
        """ Get verification Oauth url
            and device code to register device with Google API.

        """
        oauth = glogin.OauthParams()
        return json.dumps({'url': oauth.get_login()['verification_url'],
                           'user_code': oauth.get_login()['user_code']})

    def get_collections(self):
        pass

    def provider_items(self):
        pass

    def collection_items(self):
        pass

    def search(self, type, id, qtext):
        pass

    def add_collection(self):
        pass

    def add_playlist(self):
        pass

    def add_collection_item(self):
        pass

    def add_playlist_item(self):
        pass


# Test example
# TODO add more test
if __name__ == '__main__':
    app = Application()
    app.call('get', 'playlists')

