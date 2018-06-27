from app_manager import AppManager

# Global config
listen_port = 8888


if __name__ == '__main__':
    app = AppManager()
    app.run(listen_port)
