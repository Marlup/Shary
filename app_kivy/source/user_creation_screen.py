import re
import os

from dotenv import load_dotenv, set_key

from kivy.lang import Builder
from kivy.uix.screenmanager import Screen
from kivymd.uix.dialog import MDDialog

from source.func_utils import make_base_tables

KV = """
<UserCreationScreen>:
    name: "create_user"
    BoxLayout:
        orientation: 'vertical'
        padding: dp(20)
        spacing: dp(10)

        MDLabel:
            text: "Create New User"
            halign: "center"
            theme_text_color: "Primary"
            font_style: "H5"

        MDTextField:
            id: username_input
            hint_text: "Username"
            helper_text: "Enter your username"
            helper_text_mode: "on_focus"

        MDTextField:
            id: password_input
            hint_text: "Password"
            password: True
            helper_text: "Must contain uppercase, lowercase, number, and special character"
            helper_text_mode: "on_focus"

        MDTextField:
            id: confirm_password_input
            hint_text: "Confirm Password"
            password: True

        MDRaisedButton:
            text: "Create User"
            pos_hint: {"center_x": 0.5}
            on_release: root.create_user()
"""

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
        if not re.search(r"[!@#$%^&*(),.?\\\":{}|<>]", password):
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
        self.manager.current = "login"  # Switch to login screen

    def show_dialog(self, title, message):
        dialog = MDDialog(title=title, text=message)
        dialog.open()

    def on_enter(self):
        """Initialize on enter."""
        # Load env variables
        load_dotenv(".env")

def get_user_creation_screen():
    Builder.load_string(KV)
    return UserCreationScreen()
