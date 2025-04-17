# --- screen/screen_manager.py ---

from kivy.uix.screenmanager import ScreenManager
from kivy.logger import Logger
from kivy.lang import Builder
from kivy.uix.screenmanager import SlideTransition

from screens.screen_factory import ScreenFactory

from core.constant import (
    SCREEN_NAME_LOGIN,
    SCREEN_NAME_USER_CREATION,
    SCREEN_NAME_FIELDS,
    SCREEN_NAME_REQUESTS,
    SCREEN_NAME_USERS,
    SCREEN_NAME_FILES_VISUALIZER,
    KV_PATHS_OTHERS,
    PATH_SCHEMA_LOGIN,
    PATH_SCHEMA_USER_CREATION,
)

from core.dependency_container import DependencyContainer
from controller.app_controller import AppController
from core.session import CurrentSession

class RootScreenManager(ScreenManager):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.controller: AppController = DependencyContainer.get("controller")
        self.session: CurrentSession = CurrentSession.get_instance()
        
        # Start the first screen
        self._start_login_or_signup()

    def load_user_creation_screen(self):
        Builder.load_file(PATH_SCHEMA_USER_CREATION)
        self.add_widget(ScreenFactory.create_user_creation_screen())
        self.current = SCREEN_NAME_USER_CREATION
    
    def load_login_screen(self):
        Builder.load_file(PATH_SCHEMA_LOGIN)
        self.add_widget(ScreenFactory.create_login_screen())
        self.current = SCREEN_NAME_LOGIN

    def load_other_screens(self):
        # Load business concerned KV files
        for path in KV_PATHS_OTHERS:
            Builder.load_file(path)

        # Add the ui widgets
        self.add_widget(ScreenFactory.create_fields_screen())
        self.add_widget(ScreenFactory.create_users_screen())
        self.add_widget(ScreenFactory.create_requests_screen())
        self.add_widget(ScreenFactory.create_files_visualizer_screen())

    # Screen transitions
    def go_to_users_screen(self, direction):
        self.transition = SlideTransition(direction=direction, duration=0.4)
        self.current = SCREEN_NAME_USERS

    def go_to_requests_screen(self, direction):
        self.transition = SlideTransition(direction=direction, duration=0.4)
        self.current = SCREEN_NAME_REQUESTS

    def go_to_fields_screen(self, direction):
        self.transition = SlideTransition(direction=direction, duration=0.4)
        self.current = SCREEN_NAME_FIELDS

    def go_to_user_creation_screen(self, direction):
        self.transition = SlideTransition(direction=direction, duration=0.4)
        self.current = SCREEN_NAME_USER_CREATION

    def go_to_login_screen(self, direction):
        self.transition = SlideTransition(direction=direction, duration=0.4)
        self.current = SCREEN_NAME_LOGIN

    def go_to_files_visualizer_screen(self, direction):
        self.transition = SlideTransition(direction=direction, duration=0.4)
        self.current = SCREEN_NAME_FILES_VISUALIZER
    
    def save_services(self):
        self.session.save_keys()

   # ----- Internal methods -----
    def _start_login_or_signup(self):
            # Load the environment variables
            self.session.load_credentials()

            if self.session.is_owner_creds_active() \
            and self.session.is_owner_keys_active() \
            and self.controller.is_owner_registered(self.session.get_email()):
                Logger.info("Going to login screen")

                self.load_login_screen()
            else:
                Logger.info(f"Going to user creation screen. Current screen is {self.current_screen}")
                
                self.load_user_creation_screen()
            #Logger.info(f"Screen names ({len(self.screen_names)}) are {self.screen_names}")