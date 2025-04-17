# --- main.py ---
from kivymd.app import MDApp

from screens.screen_manager import RootScreenManager
from core.functions import try_make_base_tables
from core.constant import APPLICATION_NAME
from core.dependency_container import DependencyContainer

class SharyApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = APPLICATION_NAME
        DependencyContainer.init_all()
        
        # Create the database tables
        try_make_base_tables()
    
    def build(self):
        self.screen_manager = RootScreenManager()
        return self.screen_manager
