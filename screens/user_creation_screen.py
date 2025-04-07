# --- source/user_creation_screen.py ---
import re
import logging

from dotenv import set_key
from kivy.uix.screenmanager import Screen
from kivymd.uix.dialog import MDDialog
import bcrypt
import keyring

from core.constant import (
    SCREEN_NAME_USER_CREATION,
)

from core.dtos import OwnerDTO

class UserCreationScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(name=SCREEN_NAME_USER_CREATION, **kwargs)
    
    def validate_password(self, password):
        if len(password) < 8:
            return "Password must be at least 8 characters long."
        if not re.search(r"[A-Z]", password):
            return "Password must contain at least one uppercase letter."
        if not re.search(r"[a-z]", password):
            return "Password must contain at least one lowercase letter."
        if not re.search(r"\d", password):
            return "Password must contain at least one number."
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            return "Password must contain at least one special character (!@#$%^&*...)."
        return None

    def create_user(self):
        if not self._validate_inputs():
            return
        
        self._load_services()

        success = self._store_keys_to_cloud()
        if success:
            self._setup_environment_variables()
            self._show_dialog("Success", "User created successfully!")
            self._save_services()
            self._load_login_screen()
            self._go_to_login_screen()
        else:
            self._show_dialog("Error", "Invalid username or email. Choose another.")

    def _show_dialog(self, title, message):
        dialog = MDDialog(title=title, text=message)
        dialog.open()

    def _validate_inputs(self) -> bool:
        email = self._get_email()
        username = self._get_username()
        password = self._get_password()
        confirm_password = self._get_confirm_password()

        logging.info(f"_validate_inputs - email: {email}")
        logging.info(f"_validate_inputs - username: {username}")
        logging.info(f"_validate_inputs - password: {password}")
        logging.info(f"_validate_inputs - confirm_password: {confirm_password}")

        if not email:
            self._show_dialog("Invalid Input", "Email cannot be empty.")
            return False

        if not username:
            self._show_dialog("Invalid Input", "Username cannot be empty.")
            return False

        if password != confirm_password:
            self._show_dialog("Password Error", "Passwords do not match.")
            return False

        password_error = self.validate_password(password)
        if password_error:
            self._show_dialog("Weak Password", password_error)
            return False

        safe_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        self._cache_user_data(email, username, safe_password)

        return True

    def _cache_user_data(self, email: str, username: str, safe_password: str):
        if self.manager.owner is None:
            self.manager.owner = OwnerDTO(
                username=username,
                email=email,
                safe_password=safe_password
            )

    def _get_username(self):
        return self.ids.username_input.text.strip()

    def _get_email(self):
        return self.ids.email_input.text.strip()

    def _get_password(self):
        return self.ids.password_input.text.strip()
    
    def _get_confirm_password(self):
        return self.ids.confirm_password_input.text.strip()

    def _setup_environment_variables(self):
        # Hash and store
        keyring.set_password("shary_app", "owner_email", self.manager.owner.email)
        keyring.set_password("shary_app", "owner_username", self.manager.owner.username)
        keyring.set_password("shary_app", "owner_safe_password", self.manager.owner.safe_password)

    def _store_keys_to_cloud(self) -> bool:
        ok_store = self.manager.store_user_in_cloud()
        return ok_store

    def _go_to_login_screen(self):
        self.manager.go_to_login_screen("left")
    
    def _load_login_screen(self):
        self.manager.load_login_screen()

    def _save_services(self):
        self.manager.save_services()


    def _load_services(self):
        self.manager.load_services()
