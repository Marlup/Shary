# --- main.py ---
from kivymd.app import MDApp

from core.functions import try_make_base_tables
from screens.screen_manager import RootScreenManager
from core.dependency_container import DependencyContainer

from core.session import Session
from controller.app_controller import AppController
from services.security_service import SecurityService
from services.user_service import UserService
from services.field_service import FieldService
from services.email_service import EmailService
from services.request_service import RequestService
from services.cloud_service import CloudService

from core.constant import APPLICATION_NAME

class SharyApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = APPLICATION_NAME
        DependencyContainer.init_all()
        
        # Create the database tables
        try_make_base_tables()
    
    def build(self) -> RootScreenManager:
        session: Session = DependencyContainer.get("session")
        self.screen_manager = RootScreenManager(session)
        
        return self.screen_manager
