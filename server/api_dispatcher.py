import json
import providers


class Router(object):

    def __init__(self):
        self._handlers = {
            'get': {}, 'post': {}, 'put': {}, 'delete': {}
        }
 
    def lookup(self, method, path):
        print(self._handlers)
        return self._handlers[method][path]

    def get(self, path):
        def _decorator(func):
            self._handlers['get'][path] = func
            return func
        return _decorator
    
    def post(self, path):
        def _decorator(func):
            self._handlers['post'][path] = func
            return func
        return _decorator

    def put(self, path):
        def _decorator(func):
            self._handlers['put'][path] = func
            return func
        return _decorator

    def delete(self, path):
        def _decorator(func):
            self._handlers['delete'][path] = func
            return func
        return _decorator


router = Router()


class Application(object):

    def call(self, method, path, **kwargs):
        """ Calls the appropriate api function handler from the handlers
            dict, if available otherwise error is returned.

        """
        api_handler = router.lookup(method.lower(), path)
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

        if provider_id:
            prov = providers.all()[provider_id]
            playlists = []
            entries_list = prov.entries()
            for details in entries_list:
                playlists.append(dict(details, provid=provid))
        return json.dumps(playlists)

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

