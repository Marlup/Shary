# --- source/user_creation_screen.py ---
import re

from dotenv import set_key
from kivy.uix.screenmanager import Screen
from kivymd.uix.dialog import MDDialog

from front.core.constant import (
    SCREEN_NAME_LOGIN,
    SCREEN_NAME_USER_CREATION,
    PATH_ENV_VARIABLES
)

from front.core.dtos import SuperUserDTO

class UserCreationScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(name=SCREEN_NAME_USER_CREATION, **kwargs)
    
    def validate_email(self, email):
        pass
    
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
        email = self.ids.email_input.text.strip()
        username = self.ids.username_input.text.strip()
        password = self.ids.password_input.text
        confirm_password = self.ids.confirm_password_input.text

        if not email:
            self.show_dialog("Invalid Input", "Email cannot be empty.")
            return

        if not username:
            self.show_dialog("Invalid Input", "Username cannot be empty.")
            return

        if password != confirm_password:
            self.show_dialog("Password Error", "Passwords do not match.")
            return

        password_error = self.validate_password(password)
        if password_error:
            self.show_dialog("Weak Password", password_error)
            return
        
        if self.manager.super_user is None:
            self.manager.super_user = SuperUserDTO(username=username, 
                                                   email=email,
                                                   phone=0,
                                                   extension=0
                                                   )
        
        # Remove the user creation screen after successful registration
        self.manager.current = SCREEN_NAME_LOGIN

        # Load the cryptographer
        self.manager.load_cryptographer()

        # Save ENV variables
        set_key(PATH_ENV_VARIABLES, "SHARY_MAIN_EMAIL", email)
        set_key(PATH_ENV_VARIABLES, "SHARY_MAIN_USERNAME", username)
        set_key(PATH_ENV_VARIABLES, "SHARY_MAIN_PASSWORD", password)
        set_key(PATH_ENV_VARIABLES, "SHARY_MAIN_PUBKEY_LIVE", "false")
        
        # Upload the private keys to the cloud service
        ok_upload = self.manager.cloud_service.upload_pubkey(
            self.manager.cryptographer,
            self.manager.super_user.username
            )
        if ok_upload:
            set_key(PATH_ENV_VARIABLES, "SHARY_MAIN_PUBKEY_LIVE", "true")
            self.show_dialog("Success", "User created successfully!")
        else:
            self.show_dialog("Error", "User wasn't created. Conflict at pubkey upload!")

    def show_dialog(self, title, message):
        dialog = MDDialog(title=title, text=message)
        dialog.open()
