# --- source/user_creation_screen.py ---

import logging
from kivymd.uix.dialog import MDDialog

from core.functions import (
    validate_password,
    validate_email_syntax,
)

from core.classes import (
    EnhancedMDScreen
)

from core.constant import (
    SCREEN_NAME_USER_CREATION,
    CONTINUE_FOR_TESTING
)

from services.security_service import SecurityService
from services.cloud_service import CloudService
from core.session import Session

class UserCreationScreen(EnhancedMDScreen):
    def __init__(self, session: Session, security_service: SecurityService, cloud_service: CloudService, **kwargs):
        super().__init__(name=SCREEN_NAME_USER_CREATION, **kwargs)
        self.session = session
        self.cloud_service = cloud_service
        self.security_service = security_service
    
    # ----- Internal methods -----
    def _create_user(self):
        ui_inputs = self._get_ui_inputs()

        if not self._validate_inputs(ui_inputs):
            return
        
        # Cache session credentials from ui inputs
        email, username, password, *_ = ui_inputs
        
        self._cache_session_credentials(email, username, password)
        self._generate_cryptographic_keys(password, username)

        _ = self._upload_user(email)
        #if success_store or CONTINUE_FOR_TESTING:
        # Store previously validated user credentials
        self._store_cached_credentials()
        
        # Store previously generated cryptographic keys
        self._save_user_signature(username, email, password)
        
        # Login screen
        self._go_to_login_screen()

        self._show_dialog("Success", "User created successfully!")
        #self._show_dialog("Error", "Invalid username or email. Choose another.")

    def _get_ui_inputs(self):
        email = self._get_ui_email()
        username = self._get_ui_username()
        password = self._get_ui_password()
        confirm_password = self._get_ui_confirm_password()

        return (email, username, password, confirm_password)

    def _validate_inputs(self, ui_inputs: tuple[str]) -> bool:
        email, username, confirm_password, password = ui_inputs

        # Validate email exists
        validated, msg_email_validation = validate_email_syntax(email)
        if not validated:
            self._show_dialog("Invalid Input", msg_email_validation)
            return False

        # Validate username exists
        if not username:
            self._show_dialog("Invalid Input", "Username cannot be empty.")
            return False
        logging.debug(f"Username validated: {username}")

        validated, msg_password_validation = validate_password(password)
        if not validated:
            self._show_dialog("Weak Password", msg_password_validation)
            return False
        
        if password != confirm_password:
            self._show_dialog("Password Error", "Passwords do not match.")
            return False
        logging.debug(f"Password confirmation validated")

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
    def _generate_cryptographic_keys(self, password, username):
        self.security_service.generate_keys_from_secrets(password, username)
    
    def _save_user_signature(self, username: str, email: str, password: str):
        self.security_service.save_signature(username, email, password)

    # Credentials
    def _cache_session_credentials(
            self,
            email: str,
            username: str,
            password: str
            ):
        self.session.cache_credentials_from_ui(email, username, password)

    def _store_cached_credentials(self):
        self.session.store_cached_credentials()

    # User
    def _upload_user(self, email: str) -> bool:
        ok_store, token = self.cloud_service.upload_user(email)
        self.session.set_verification_token(token)
        return ok_store