# --- source/screen_manager.py ---
import os
from kivy.uix.screenmanager import ScreenManager
from dotenv import load_dotenv

from source.user_creation_screen import get_user_creation_screen
from source.login_screen import get_login_screen
from source.fields_screen import get_fields_screen
from source.users_screen import get_users_screen
from source.requests_screen import get_requests_screen
from source.class_utils import DataManager
from kivy.logger import Logger

load_dotenv(".env")

class SharyScreenManager(ScreenManager):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        Logger.info(f"Current screen is {self.current_screen}")

        self.data_manager = DataManager()

        # Load rest of the screens
        self.add_widget(get_login_screen())
        self.add_widget(get_fields_screen())
        self.add_widget(get_users_screen())
        self.add_widget(get_requests_screen())
        
        if os.getenv("SHARY_USERNAME") and os.getenv("SHARY_PASSWORD"):
            Logger.info("Going to login screen")
            self.current = "login"
        else:
            Logger.info("Going to user creation screen")
            self.add_widget(get_user_creation_screen())
            self.current = "user_creation"
        
        Logger.info(f"Current screen is {self.current_screen}")
        Logger.info(f"Screen names ({len(self.screen_names)}) are {self.screen_names}")
        