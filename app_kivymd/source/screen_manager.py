# --- source/screen_manager.py ---
import os
from kivy.uix.screenmanager import ScreenManager
from dotenv import load_dotenv

from source.user_creation_screen import get_user_creation_screen
from source.login_screen import get_login_screen
from source.field_screen import get_field_screen
from source.user_screen import get_user_screen
from source.request_screen import get_request_screen
from source.file_visualizer_screen import get_file_visualizer_screen
from source.class_utils import DataManager
from kivy.logger import Logger
from source.class_utils import FirebaseManager  # Import the manager class

load_dotenv(".env")

class SharyScreenManager(ScreenManager):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        Logger.info(f"Current screen is {self.current_screen}")

        self.data_manager = DataManager()
        self.firebase_manager = FirebaseManager(self) # Initialize Firebase manager

        # Add test session requests (example)
        self.firebase_manager.add_request("session_123", "my_secret_key")
        self.firebase_manager.add_request("session_456", "another_secret")

        # Load rest of the screens
        self.add_widget(get_login_screen())
        self.add_widget(get_field_screen())
        self.add_widget(get_user_screen())
        self.add_widget(get_request_screen())
        self.add_widget(get_file_visualizer_screen())
        
        if os.getenv("SHARY_ROOT_USERNAME") and os.getenv("SHARY_ROOT_PASSWORD"):
            Logger.info("Going to login screen")
            self.current = "login"
        else:
            Logger.info("Going to user creation screen")
            self.add_widget(get_user_creation_screen())
            self.current = "user_creation"
        
        Logger.info(f"Current screen is {self.current_screen}")
        Logger.info(f"Screen names ({len(self.screen_names)}) are {self.screen_names}")