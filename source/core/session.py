# core/session.py

import os
import json
import logging
from base64 import b64encode

from services.security_service import SecurityService

from core.security_utils import (
    aes_encrypt,
    aes_decrypt,
    make_user_salt,
)

from core.constant import (
    PATH_AUTH_SIGNATURE,
    PATH_FILE_CREDENTIALS,
    PATH_CREDENTIALS
)

class Session():
    _instance = None

    def __init__(self, security_service: SecurityService = None):
        # Owner credentials
        self.email = None
        self.username = None
        self.safe_password = None
        self.is_password_safe = False

        # Owner status

        # Users checked
        self.checked_users = None

        # Fields checked

        # Fields requested

        # Files available

        # Cryptography
        self.security_service = security_service

    @classmethod
    def get_instance(cls):
        if not cls._instance:
            cls._instance = Session()
        return cls._instance

    def is_authenticated(self):
        return all([self.email, self.safe_password])
    
    def cache_credentials_from_ui(self, email, username, password):
        self.email = email
        self.username = username
        self.safe_password = password

        logging.debug(f"User credentials cached.")
    
    def store_cached_credentials(self):
        self.store_credentials(self.email, self.username, self.safe_password)

    def _exists_owner(self) -> bool:
        return ".credentials" in os.listdir(PATH_CREDENTIALS)

    def store_credentials(self, email: str, username: str, password: str):
        user_salt: bytes = make_user_salt(username)
        password_utf8: bytes = password.encode("utf-8")
        safe_password = self.security_service.hash_password(password_utf8, user_salt)

        # Hash encryption key using PBKDF2
        encryption_key = self.security_service.hash_password(safe_password, user_salt)
        
        logging.debug(f"salt: {user_salt}")
        logging.debug(f"safe_password: {password, safe_password}")
        logging.debug(f"encryption_key: {encryption_key}")

        if not self._exists_owner():
            data = {
                "owner_email": email,
                "owner_username": username,
                "owner_safe_password": safe_password.hex()
            }
            encrypted = aes_encrypt(encryption_key, json.dumps(data))
            
            # Store encrypted credentials
            with open(PATH_FILE_CREDENTIALS, "wb") as f:
                f.write(encrypted)
        else:
            logging.warning("Cannot store credentials. Credentials file already exists.")

    def load_credentials(self, salt: bytes, safe_password: bytes):
        if not self._exists_owner():
            logging.warning("Credentials file not found.")
            return
        
        # Load encrypted credentials
        with open(PATH_FILE_CREDENTIALS, "rb") as f:
            encrypted = f.read()
        encryption_key = self.security_service.hash_password(safe_password, salt)
        logging.debug(f"salt: {salt}")
        logging.debug(f"safe_password: {safe_password}")
        logging.debug(f"encryption_key: {encryption_key}")
        try:
            data = json.loads(aes_decrypt(encryption_key, encrypted))
        except Exception as e:
            logging.debug(f"Error at loading credentials: {e}")
            return

        logging.debug(f"load_credentials - data: {data}")
        
        # Load the credentials into session
        self.email = data.get("owner_email")
        self.username = data.get("owner_username")
        self.safe_password = data.get("owner_safe_password")

    def delete_credentials(self):
        if os.path.exists(PATH_FILE_CREDENTIALS):
            os.remove(PATH_FILE_CREDENTIALS)
        else:
            logging.info("Credentials file already deleted.")
    
    def get_email(self):
        return self.email
    
    def get_username(self):
        return self.username
    
    def get_safe_password(self):
        return self.safe_password

    def get_checked_users(self):
        return [] or self.checked_users
    
    def set_checked_users(self, users):
        if users:
            self.checked_users = users

    def try_login(self, ui_username: str, ui_password: str) -> bool:
        # Hash password from UI
        user_salt: bytes = make_user_salt(ui_username)
        password_utf8: bytes = ui_password.encode("utf-8")
        
        test_safe_password = self.security_service.hash_password(password_utf8, user_salt)
        print(f"test_safe_password : {test_safe_password}")
        
        # Load session credentials (username and safe_password)        
        self.load_credentials(user_salt, test_safe_password)
        
        logging.debug(""f"try_login - session credentials - username: {ui_username}, {self.get_username()}")
        logging.debug(""f"try_login - session credentials - password: {test_safe_password}, {self.get_safe_password()}")
        
        if ui_username == self.get_username() \
        and test_safe_password.hex() == self.get_safe_password():
            # User can login
            return True
        else:
            # User rejected
            return False
        
    def is_owner_signature_active(self) -> bool:
        """ Check if the owner is already registered."""
        if os.path.exists(PATH_AUTH_SIGNATURE):
            return True
        else:
            pass#self.delete_credentials()
        return False

    def is_owner_creds_active(self) -> bool:
        """ Check if the owner is already registered. """
        if os.path.exists(PATH_FILE_CREDENTIALS):
            return True
        return False