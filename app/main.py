# --- main.py ---
import threading
from kivymd.app import MDApp
from screen.screen_manager import SharyScreenManager
from core.backend import run_flask
from core.func_utils import try_make_base_tables

class SharyApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = "Shary"
        
        # Make tables
        try_make_base_tables()
    def build(self):
        return SharyScreenManager()

def main():
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    SharyApp().run()

if __name__ == "__main__":
    main()
