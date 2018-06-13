from channel_manager import ChannelManager
from library_manager import LibraryManager
from api_manager import ApiManager
from web_server import WebServer

# Global config
listen_port = 8888


if __name__ == '__main__':
    server = WebServer(listen_port)
    channels = ChannelManager(server.app)
    libs = LibraryManager(server.app)
    server.app['channels'] = channels
    server.app['libraries'] = libs
    api = ApiManager(server.app)
    api.setup_routes()
    server.run()
