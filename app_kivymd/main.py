# --- main.py ---
import threading
from kivymd.app import MDApp
from source.screen_manager import SharyScreenManager
from source.backend import run_flask

class SharyApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = "Shary"

    def build(self):
        return SharyScreenManager()

def main():
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    SharyApp().run()

if __name__ == "__main__":
    main()
