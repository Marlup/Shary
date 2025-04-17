# core/session.py

import os
import keyring
import logging
import bcrypt

from security.crypto import RSACrypto

from core.constant import (
    PATH_PRIVATE_KEY,
    PATH_PUBLIC_KEY
)

class CurrentSession:
    _instance = None

    def __init__(self):
        # Owner credentials
        self.email = None
        self.username = None
        self.safe_password = None

        # Users selected
        self.users_selected = None

        # Fields selected

        # Fields requested

        # Files available

        # Cryptography
        self.crypto: RSACrypto = RSACrypto.get_instance()

    @classmethod
    def get_instance(cls):
        if not cls._instance:
            cls._instance = CurrentSession()
        return cls._instance

    def is_authenticated(self):
        return all([self.email, self.safe_password])
    
    def cache_credentials(self, email, username, safe_password):
        self.email = email
        self.username = username
        self.safe_password = safe_password
    
    def store_cached_credentials(self):
        self.store_credentials(self.email, self.username, self.safe_password)

    def store_credentials(self, email, username, safe_password):
        if self._exists_owner():
            keyring.set_password("shary_app", "owner_email", email)
            keyring.set_password("shary_app", "owner_username", username)
            keyring.set_password("shary_app", "owner_safe_password", safe_password)
        else:
            logging.warning("Cannot store credentials. Credentials don't exist.")

    def load_credentials(self):
        self.email = keyring.get_password("shary_app", "owner_email")
        self.username = keyring.get_password("shary_app", "owner_username")
        self.safe_password = keyring.get_password("shary_app", "owner_safe_password")

    def delete_credentials(self):
        keyring.delete_password("shary_app", "owner_email")
        keyring.delete_password("shary_app", "owner_username")
        keyring.delete_password("shary_app", "owner_safe_password")
        keyring.delete_password("shary_app", "owner_verification_token")
    
    def get_email(self):
        return self.email
    
    def get_username(self):
        return self.username
    
    def get_safe_password(self):
        return self.safe_password

    def is_owner_keys_active(self) -> bool:
        """ Check if the owner is already registered."""
        if os.path.exists(PATH_PRIVATE_KEY) \
        and os.path.exists(PATH_PUBLIC_KEY):
            return True
        else:
            self.delete_credentials()
        return False

    def is_owner_creds_active(self) -> bool:
        """ Check if the owner is already registered. """
        if self.get_email() \
        and self.get_username() \
        and self.get_safe_password():
            return True
        return False
    
    def get_users_selected(self):
        return self.users_selected if self.users_selected else []
    
    def set_users_selected(self, users):
        if users:
            self.users_selected = users

    def try_login(self, ui_username, ui_password):
        # Hash password from UI
        ui_safe_password = bcrypt.hashpw(ui_password.encode(), bcrypt.gensalt()).decode()

        # Load session credentials (username and safe_password)        
        self.load_credentials()
        if ui_username == self.get_email() \
        and ui_safe_password == self.get_safe_password():
            # User can login
            return True
        else:
            # User rejected
            return False
    
    # Cryptography
    def generate_cryptographic_keys(self):
        self.crypto.generate_keys()

    def save_cryptographic_keys(self):
        self.crypto.store_keys()
        
    def load_cryptographic_keys(self):
        self.crypto.load_keys_from_files()
    
    # ----- Internal methods -----
    def _exists_owner(self):
        if self.email and self.username and self.safe_password:
            return True
        return False
    