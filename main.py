# --- main.py ---
import threading
from front.core.backend import run_flask
from front.app.app import SharyApp

def main():
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    SharyApp().run()

if __name__ == "__main__":
    main()
