# --- screen/screen_manager.py ---
import os

from dotenv import load_dotenv
from kivy.uix.screenmanager import ScreenManager
from kivy.logger import Logger
from kivy.lang import Builder

from front.screen.user_creation_screen import UserCreationScreen
from front.screen.login_screen import LoginScreen
from front.screen.field_screen import FieldScreen
from front.screen.user_screen import UserScreen
from front.screen.request_screen import RequestScreen
from front.screen.file_visualizer_screen import FileVisualizerScreen

from front.core.constant import (
    SCREEN_NAME_LOGIN,
    SCREEN_NAME_USER_CREATION,
    PATH_ENV_VARIABLES,
    KV_PATHS,
    PATH_SCHEMA_USER_CREATION,
    PATH_DATA_AUTHENTICATION,
    PATH_DATA_SECURITY
)

from front.core.func_utils import is_dir_empty

from front.security.crypto import RSACrypto
from front.service.email_service import EmailService
from front.service.cloud_service import CloudService

class SharyScreenManager(ScreenManager):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        load_dotenv(PATH_ENV_VARIABLES)
        
        self.super_user = None
        self.email_service = EmailService()
        self.cryptographer = None
        self.cloud_service = CloudService("a")

        Logger.info(f"Current screen is {self.current_screen}")

        #self.data_manager = DataManager()
        #self.firebase_manager = FirebaseManager(self) # Initialize Firebase manager

        # Add test session requests (example)
        #self.firebase_manager.add_request("session_123", "my_secret_key")
        #self.firebase_manager.add_request("session_456", "another_secret")

        # Load KV files before adding the widgets
        for path in KV_PATHS:
            Builder.load_file(path)

        # Load rest of the screens
        self.add_widget(LoginScreen())
        self.add_widget(FieldScreen())
        self.add_widget(UserScreen())
        self.add_widget(RequestScreen())
        self.add_widget(FileVisualizerScreen())
        
        if os.getenv("SHARY_MAIN_USERNAME") \
        and os.getenv("SHARY_MAIN_PASSWORD") \
        and os.getenv("SHARY_MAIN_PUBKEY_LIVE") == "true" \
        and not is_dir_empty(PATH_DATA_AUTHENTICATION) \
        and not is_dir_empty(PATH_DATA_SECURITY):
            Logger.info("Going to login screen")
            self.current = SCREEN_NAME_LOGIN
        else:
            Logger.info("Going to user creation screen")
            Builder.load_file(PATH_SCHEMA_USER_CREATION)
            
            self.add_widget(UserCreationScreen())
            self.current = SCREEN_NAME_USER_CREATION
        
        Logger.info(f"Current screen is {self.current_screen}")
        Logger.info(f"Screen names ({len(self.screen_names)}) are {self.screen_names}")

    def load_cryptographer(self):
        self.cryptographer = RSACrypto.try_load_from_files()