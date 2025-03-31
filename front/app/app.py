# --- main.py ---
from kivymd.app import MDApp

from front.screen.screen_manager import SharyScreenManager
from front.core.func_utils import try_make_base_tables
from front.security.crypto import RSACrypto, NonceStore
from front.core.constant import APPLICATION_NAME
from front.core.class_utils import FirebaseManager

class SharyApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = APPLICATION_NAME
        
        # Make tables
        try_make_base_tables()

        #self.firebase_manager = FirebaseManager(self, self.cryptographer) # Initialize Firebase manager

        # Add test session requests (example)
        #self.firebase_manager.add_request("session_123", "my_secret_key")
        #self.firebase_manager.add_request("session_456", "another_secret")
    
    def build(self):
        self.screen_manager = SharyScreenManager()
        return self.screen_manager
