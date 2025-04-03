# --- main.py ---
from kivymd.app import MDApp

from screens.screen_manager import SharyScreenManager
from core.functions import try_make_base_tables
from core.constant import APPLICATION_NAME

class SharyApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = APPLICATION_NAME
        
        # Create the database tables
        try_make_base_tables()
    
    def build(self):
        self.screen_manager = SharyScreenManager()
        return self.screen_manager
