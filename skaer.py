from app_manager import AppManager
from api_manager import ApiManager


# Global config
listen_port = 8888


if __name__ == '__main__':
    app = AppManager()
    api = ApiManager(app)
    api.setup_routes()
    app.run(listen_port)
