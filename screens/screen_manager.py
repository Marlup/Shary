# --- screen/screen_manager.py ---
import os

from dotenv import load_dotenv
from kivy.uix.screenmanager import ScreenManager
from kivy.logger import Logger
from kivy.lang import Builder

from screens.user_creation_screen import UserCreationScreen
from screens.login_screen import LoginScreen
from screens.field_screen import FieldScreen
from screens.user_screen import UserScreen
from screens.request_screen import RequestScreen
from screens.file_visualizer_screen import FileVisualizerScreen

from core.constant import (
    SCREEN_NAME_LOGIN,
    SCREEN_NAME_USER_CREATION,
    PATH_ENV_VARIABLES,
    KV_PATHS_OTHERS,
    PATH_SCHEMA_LOGIN,
    PATH_SCHEMA_USER_CREATION,
    PATH_DATA_AUTHENTICATION,
    PATH_DATA_SECURITY
)

from core.functions import is_dir_empty

from security.crypto import RSACrypto
from services.email_service import EmailService
from services.cloud_service import CloudService

class SharyScreenManager(ScreenManager):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        load_dotenv(PATH_ENV_VARIABLES)
        
        self.super_user = None
        self.cryptographer = None
        self.email_service = None
        self.cloud_service = None

        if os.getenv("SHARY_MAIN_USERNAME") \
        and os.getenv("SHARY_MAIN_PASSWORD") \
        and os.getenv("SHARY_MAIN_PUBKEY_LIVE") == "true" \
        and not is_dir_empty(PATH_DATA_AUTHENTICATION) \
        and not is_dir_empty(PATH_DATA_SECURITY):
            Logger.info("Going to login screen")

            self.load_login_screen()
            self.current = SCREEN_NAME_LOGIN
        else:
            Logger.info("Going to user creation screen")
            
            Builder.load_file(PATH_SCHEMA_USER_CREATION)
            self.load_user_creation_screen()
            self.current = SCREEN_NAME_USER_CREATION
        
        Logger.info(f"Current screen is {self.current_screen}")
        Logger.info(f"Screen names ({len(self.screen_names)}) are {self.screen_names}")

    def load_user_creation_screen(self):
        Builder.load_file(PATH_SCHEMA_USER_CREATION)
        self.add_widget(UserCreationScreen())
    
    def load_login_screen(self):
        Builder.load_file(PATH_SCHEMA_LOGIN)
        self.add_widget(LoginScreen())

    def load_other_screens(self):
        # Load business concerned KV files
        for path in KV_PATHS_OTHERS:
            Builder.load_file(path)

        # Add the ui widgets
        self.add_widget(FieldScreen())
        self.add_widget(UserScreen())
        self.add_widget(RequestScreen())
        self.add_widget(FileVisualizerScreen())

    def load_services(self):
        self.cryptographer = RSACrypto.try_load_from_files()
        self.email_service = EmailService()
        self.cloud_service = CloudService("a")