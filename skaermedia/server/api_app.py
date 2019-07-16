import os
import json
from skaermedia import providers
from skaermedia.server import path_utils
from skaermedia.server.api_router import Router


class Application(object):

    router = Router()

    def call(self, method, path, **kwargs):
        """ Calls the appropriate api function handler from the handlers
            dict, if available otherwise error is returned.

        """
        api_handler = Application.router.lookup(method.lower(), path)
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

    @router.get('play')
    def play_item(self, item_id, provider_id=None):
        """ Start playing a specific media item. """

        if provider_id:
            prov = providers.get(int(provider_id))
            # May return a file system link, in case file is extracted audio.
            url = prov.stream_url(item_id)
            if url.startswith('file'):
                streamdir = path_utils.get_streampath()
                path_utils.assure_folder_exists(streamdir)
                dst = os.path.join(streamdir, os.path.split(url)[1])
                os.rename(url.lstrip('file:'), dst)
            return json.dumps(dst)


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

