import os
import threading
from dotenv import load_dotenv
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.app import MDApp
from flask import Flask, request, jsonify

from source.user_creation_screen import get_user_creation_screen
from source.login_screen import get_login_screen
from source.fields_screen import get_fields_screen
from source.users_screen import get_users_screen
from source.requests_screen import get_fields_request_screen

load_dotenv(".env")

class SharyScreenManager(ScreenManager):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Load screens
        self.add_widget(get_user_creation_screen())
        self.add_widget(get_login_screen())
        self.add_widget(get_fields_screen())
        self.add_widget(get_users_screen())
        self.add_widget(get_fields_request_screen())
        
        if os.getenv("SHARY_USERNAME") and os.getenv("SHARY_PASSWORD"):
            self.current = "login"
        else:
            self.current = "user_creation"

def restrict_access():
    allowed_ips = ['127.0.0.1']
    if request.remote_addr not in allowed_ips:
        return jsonify({"error": "Access forbidden"}), 403

def open_file():
    filename = request.args.get("filename")
    if filename:
        return jsonify({"message": f"Processing {filename}..."}), 200
    else:
        return jsonify({"error": "No filename provided."}), 400

def run_flask():
    backend_app = Flask(__name__)
    backend_app.before_request(restrict_access)
    backend_app.add_url_rule("/files/open", "open_file", open_file, methods=['GET'])
    backend_app.run(host="127.0.0.1", port=5001)

class SharyApp(MDApp):
    def build(self):
        return SharyScreenManager()

def main():
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    SharyApp().run()

if __name__ == "__main__":
    main()