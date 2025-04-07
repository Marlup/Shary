# --- screen/screen_manager.py ---
import os

import keyring
from dotenv import load_dotenv
from kivy.uix.screenmanager import ScreenManager
from kivy.logger import Logger
from kivy.lang import Builder
from kivy.uix.screenmanager import SlideTransition

from screens.user_creation_screen import UserCreationScreen
from screens.login_screen import LoginScreen
from screens.field_screen import FieldScreen
from screens.user_screen import UserScreen
from screens.request_screen import RequestScreen
from screens.file_visualizer_screen import FileVisualizerScreen

from core.constant import (
    SCREEN_NAME_LOGIN,
    SCREEN_NAME_USER_CREATION,
    SCREEN_NAME_FIELD,
    SCREEN_NAME_REQUEST,
    SCREEN_NAME_USER,
    SCREEN_NAME_FILE_VISUALIZER,
    PATH_ENV_VARIABLES,
    KV_PATHS_OTHERS,
    PATH_SCHEMA_LOGIN,
    PATH_SCHEMA_USER_CREATION,
    PATH_PRIVATE_KEY,
    PATH_PUBLIC_KEY
)

from security.crypto import RSACrypto
from services.email_service import EmailService
from services.cloud_service import CloudService

from core.dtos import OwnerDTO

class SharyScreenManager(ScreenManager):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        load_dotenv(PATH_ENV_VARIABLES)
        
        self.owner: OwnerDTO = None
        self.cryptographer = None
        self.email_service = None
        self.cloud_service = CloudService()
        self.working_online = False

        # Start the first screen
        self._start_login_or_signup()

    def _start_login_or_signup(self):
        # Load the environment variables
        owner_email, owner_username, owner_password = self.load_credentials()

        if self._is_owner_creds_active(owner_email, 
                                       owner_username,
                                       owner_password) \
        and self._is_owner_keys_active():
            Logger.info("Going to login screen")

            self._is_owner_db_registered(owner_email)
            self.load_login_screen()
            self.current = SCREEN_NAME_LOGIN
        else:
            Logger.info("Going to user creation screen")
            
            Builder.load_file(PATH_SCHEMA_USER_CREATION)
            self.load_user_creation_screen()
            self.current = SCREEN_NAME_USER_CREATION
        
        Logger.info(f"Current screen is {self.current_screen}")
        Logger.info(f"Screen names ({len(self.screen_names)}) are {self.screen_names}")

    def _is_owner_creds_active(self, email, username, password) -> bool:
        """ Check if the owner is already registered. """
        print(f"Owner email: {email}")
        print(f"Owner username: {username}")
        print(f"Owner password: {password}")

        if email and password and password:
            return True
        return False
    
    def _is_owner_keys_active(self) -> bool:
        """ Check if the owner is already registered."""
        if os.path.exists(PATH_PRIVATE_KEY) \
        and os.path.exists(PATH_PUBLIC_KEY):
            return True
        else:
            keyring.delete_password("shary_app", "owner_email")
            keyring.delete_password("shary_app", "owner_username")
            keyring.delete_password("shary_app", "owner_safe_password")
            keyring.delete_password("shary_app", "owner_verification_token")
        return False

    def _is_owner_db_registered(self, owner_email: str) -> bool:
        """ Check if the owner is already registered at database."""
        self.cloud_service.is_owner_registered(owner_email)

    @staticmethod
    def load_credentials():
        email = keyring.get_password("shary_app", "owner_email")
        username = keyring.get_password("shary_app", "owner_username")
        password = keyring.get_password("shary_app", "owner_safe_password")
        return email, username, password

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

    # Screen transitions
    def go_to_user_screen(self, direction):
        self.transition = SlideTransition(direction=direction, duration=0.4)
        self.current = SCREEN_NAME_USER

    def go_to_request_screen(self, direction):
        self.transition = SlideTransition(direction=direction, duration=0.4)
        self.current = SCREEN_NAME_REQUEST

    def go_to_field_screen(self, direction):
        self.transition = SlideTransition(direction=direction, duration=0.4)
        self.current = SCREEN_NAME_FIELD

    def go_to_user_creation_screen(self, direction):
        self.transition = SlideTransition(direction=direction, duration=0.4)
        self.current = SCREEN_NAME_USER_CREATION

    def go_to_login_screen(self, direction):
        self.transition = SlideTransition(direction=direction, duration=0.4)
        self.current = SCREEN_NAME_LOGIN

    def go_to_visualizer_screen(self, direction):
        self.transition = SlideTransition(direction=direction, duration=0.4)
        self.current = SCREEN_NAME_FILE_VISUALIZER

    # Data retrievers
    def get_checked_users(self):
        return self.get_screen(SCREEN_NAME_USER) \
                   .get_checked_emails(index=1)

    def get_owner_email(self):
        return self.owner.email
    
    def get_owner_username(self):
        return self.owner.username
    
    def get_owner_safe_password(self):
        return self.owner.safe_password
    
    def get_owner(self):
        # Load Owner
        self.owner = OwnerDTO(
            keyring.get_password("shary_app", 
                                 "owner_username"), 
            keyring.get_password("shary_app",
                                 "owner_email"),
            keyring.get_password("shary_app",
                                 "owner_safe_password"),
                                 )
    def set_owner(self, username, email, safe_password):
        # Load Owner
        self.owner = OwnerDTO(username, email, safe_password)

    # Service calls
    def send_data_to_cloud(self, 
                           data_rows: list, 
                           consumers: list, 
                           on_request: bool
                           ):
        self.cloud_service.send_data(
            self.cryptographer, 
            data_rows, 
            self.owner.email,
            consumers,
            on_request
            )

    def store_user_in_cloud(self):
        ok_store = self.cloud_service.store_user(
            self.cryptographer,
            self.owner.email
        )
        return ok_store

    def load_services(self):
        self.cryptographer = RSACrypto.generate()
        self.email_service = EmailService(
            self.owner.email,
            self.owner.username)
        if not self.cloud_service:
            self.cloud_service = CloudService()
    
    def save_services(self):
        self.cryptographer.save_keys()