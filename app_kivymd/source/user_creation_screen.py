# --- source/user_creation_screen.py ---
import re
import os
from dotenv import load_dotenv, set_key
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen
from kivymd.uix.dialog import MDDialog
from source.func_utils import make_base_tables

class UserCreationScreen(Screen):

    def __init__(self, **kwargs):
        super().__init__(name="user_creation", **kwargs)
        make_base_tables()

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
        username = self.ids.username_input.text.strip()
        password = self.ids.password_input.text
        confirm_password = self.ids.confirm_password_input.text

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

        set_key(".env", "SHARY_USERNAME", username)
        set_key(".env", "SHARY_PASSWORD", password)

        self.show_dialog("Success", "User created successfully!")

        # Remove the user creation screen after successful registration
        self.manager.remove_widget(self)
        self.manager.current = "login"

    def show_dialog(self, title, message):
        dialog = MDDialog(title=title, text=message)
        dialog.open()

    def on_enter(self):
        load_dotenv(".env")

def get_user_creation_screen():
    Builder.load_file("views/user_creation.kv")
    return UserCreationScreen()
