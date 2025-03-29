# --- screen/screen_manager.py ---
import os
from kivy.uix.screenmanager import ScreenManager
from dotenv import load_dotenv

from screen.user_creation_screen import UserCreationScreen
from screen.login_screen import LoginScreen
from screen.field_screen import FieldScreen
from screen.user_screen import UserScreen
from screen.request_screen import RequestScreen
from screen.file_visualizer_screen import FileVisualizerScreen
from core.class_utils import DataManager
from kivy.logger import Logger
from core.class_utils import FirebaseManager  # Import the manager class
from kivy.lang import Builder

from core.constant import (
    SCREEN_NAME_LOGIN,
    SCREEN_NAME_USER_CREATION
)

load_dotenv(".env")

class SharyScreenManager(ScreenManager):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        Logger.info(f"Current screen is {self.current_screen}")

        #self.data_manager = DataManager()
        #self.firebase_manager = FirebaseManager(self) # Initialize Firebase manager

        # Add test session requests (example)
        #self.firebase_manager.add_request("session_123", "my_secret_key")
        #self.firebase_manager.add_request("session_456", "another_secret")

        # Load KV files before adding the widgets
        Builder.load_file("widget_schemas/field.kv")
        Builder.load_file("widget_schemas/user.kv")
        Builder.load_file("widget_schemas/login.kv")
        Builder.load_file("widget_schemas/request.kv")
        Builder.load_file("widget_schemas/file_visualizer.kv")

        # Load rest of the screens
        self.add_widget(LoginScreen())
        self.add_widget(FieldScreen())
        self.add_widget(UserScreen())
        self.add_widget(RequestScreen())
        self.add_widget(FileVisualizerScreen())
        
        if os.getenv("SHARY_ROOT_USERNAME") and os.getenv("SHARY_ROOT_PASSWORD"):
            Logger.info("Going to login screen")
            self.current = SCREEN_NAME_LOGIN
        else:
            Logger.info("Going to user creation screen")
            Builder.load_file("widget_schemas/user_creation.kv")
            
            self.add_widget(UserCreationScreen())
            self.current = SCREEN_NAME_USER_CREATION
        
        Logger.info(f"Current screen is {self.current_screen}")
        Logger.info(f"Screen names ({len(self.screen_names)}) are {self.screen_names}")