import sys
import os.path

# Global config
listen_port = 8888


if __name__ == '__main__':
    path = os.path.realpath(os.path.abspath(__file__))
    sys.path.insert(0, os.path.dirname(os.path.dirname(path)))

    from app_manager import AppManager
    app = AppManager()
    app.run(listen_port)
