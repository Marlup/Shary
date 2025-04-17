# --- source/user_creation_screen.py ---
import logging

from dotenv import set_key
from kivy.uix.screenmanager import Screen
from kivymd.uix.dialog import MDDialog
import bcrypt

from controller.app_controller import AppController
from core.session import CurrentSession

from core.functions import (
    validate_password,
    validate_email,
)

from core.constant import (
    SCREEN_NAME_USER_CREATION,
)

class UserCreationScreen(Screen):
    def __init__(self, controller: AppController, **kwargs):
        super().__init__(name=SCREEN_NAME_USER_CREATION, **kwargs)
        
        self.session = CurrentSession.get_instance()
        self.controller = controller

    # ----- Internal methods -----
    def _create_user(self):
        if not self._validate_inputs():
            return
        
        self.session.generate_cryptographic_keys()
        self.session.save_cryptographic_keys()

        success = self._store_user_in_cloud()
        if success:
            # Store previously validated user credentials
            self._store_cached_credentials()
            
            # Store previously generated cryptographic keys
            self._store_cryptographic_keys()
            
            # Login screen
            self._go_to_login_screen()

            self._show_dialog("Success", "User created successfully!")
        else:
            self._show_dialog("Error", "Invalid username or email. Choose another.")

    def _validate_inputs(self) -> bool:
        email = self._get_ui_email()
        username = self._get_ui_username()
        password = self._get_ui_password()
        confirm_password = self._get_ui_confirm_password()

        logging.info(f"_validate_inputs - email: {email}")
        logging.info(f"_validate_inputs - username: {username}")
        logging.info(f"_validate_inputs - password: {password}")
        logging.info(f"_validate_inputs - confirm_password: {confirm_password}")

        # Validate email exists
        msg_email_validation, validated = validate_email(email)
        if validated:
            self._show_dialog("Invalid Input", msg_email_validation)
            return False

        # Validate username exists
        if not username:
            self._show_dialog("Invalid Input", "Username cannot be empty.")
            return False

        validated, msg_password_validation = validate_password(password)
        if not validated:
            self._show_dialog("Weak Password", msg_password_validation)
            return False
        
        if password != confirm_password:
            self._show_dialog("Password Error", "Passwords do not match.")
            return False

        # Hash password safely
        safe_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

        # Cache session credentials
        self._cache_session_credentials(email, username, safe_password)

        return True
    
    def _show_dialog(self, title, message):
        dialog = MDDialog(title=title, text=message)
        dialog.open()

    #  ----- UI entrypoints -----
    # UI Getters
    def _get_ui_username(self) -> str:
        return self.ids.username_input.text.strip()

    def _get_ui_email(self) -> str:
        return self.ids.email_input.text.strip()

    def _get_ui_password(self) -> str:
        return self.ids.password_input.text.strip()
    
    def _get_ui_confirm_password(self):
        return self.ids.confirm_password_input.text.strip()
    
    # UI screen transition
    def _go_to_login_screen(self):
        self.manager.load_login_screen()
        self.manager.go_to_login_screen("left")
    
    # ----- Cache and store of credentials and cryptographic keys entrypoints -----
    # Cryptographic keys
    def _save_cryptographic_keys(self):
        self.session.save_cryptographic_keys()()

    def _store_cryptographic_keys(self):
        self.session.load_cryptographic_keys()

    # Credentials
    def _cache_session_credentials(self, email: str, username: str, safe_password: str):
        self.session.cache_credentials(email, username, safe_password)

    def _store_cached_credentials(self):
        self.session.store_cached_credentials()

    # User
    def _store_user_in_cloud(self) -> bool:
        ok_store = self.controller.store_user(self.session.get_email())
        return ok_store