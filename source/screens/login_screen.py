# --- source/login_screen.py ---

import logging
from kivymd.uix.snackbar import MDSnackbar

from core.classes import EnhancedMDScreen
from core.functions import enter_message
from core.session import Session
from services.cloud_service import CloudService
from services.security_service import SecurityService

from core.constant import SCREEN_NAME_LOGIN

class LoginScreen(EnhancedMDScreen):
    def __init__(self, session: Session, security_service: SecurityService, cloud_service: CloudService, **kwargs):
        super().__init__(name=SCREEN_NAME_LOGIN, **kwargs)
        
        self.session = session
        self.security_service = security_service
        self.cloud_service = cloud_service

    def check_login(self):
        # Get credentials from UI
        username = self._get_ui_username()
        password = self._get_ui_password()
        logging.debug(f"check_login - _get_ui_...: username: {username}, password: {password}")

        self.security_service.generate_keys_from_secrets(password, username)
        
        #session.save_cryptographic_keys()

        # Try login
        login_succesful = self.session.try_login(username, password)

        if login_succesful:
            logging.info(f"User logged-in by input credentials.")

            # Check if the user is already registered
            logging.info(f"session.get_email() : {self.session.get_email()}")
            
            is_registered = self._check_owner_registered(self.session.get_email())
            logging.info(f"{enter_message(True, is_registered)}. Going to home screen")
            
            # Load cryptographic keys
            #session.load_cryptographic_keys()
            
            # Remove the user creation screen after successful registration
            self._load_other_screens()

            # Remove the login screen after validating credentials and 
            # pressing the login button
            self._go_to_fields_screen()
        else:
            MDSnackbar("Invalid credentials").open()
    
    # Owner registration checker
    def _check_owner_registered(self, email: str) -> bool:
        return self.cloud_service.is_owner_registered(email)

    #  ----- UI entrypoints -----
    # UI Getters
    def _get_ui_username(self) -> str:
        return self.ids.username_input.text.strip()

    def _get_ui_password(self) -> str:
        return self.ids.password_input.text.strip()

    # Screen Manager
    def _load_other_screens(self):
        self.manager.load_other_screens()
    
    def _go_to_fields_screen(self):
        self.manager.go_to_fields_screen("left")

    # callbacks current screen events
    def on_leave(self):
        # Load the services
        #self.manager.load_services()
        pass