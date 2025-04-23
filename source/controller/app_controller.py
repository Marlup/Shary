# core/app_controller.py

from services.security_service import SecurityService
from services.cloud_service import CloudService
from services.email_service import EmailService
from core.session import Session

class AppController:
    def __init__(
            self, 
            session: Session, 
            security: SecurityService, 
            cloud_service: CloudService, 
            email_service: EmailService, 
            ):
    
        # Services
        self._session = session
        self._security = security
        self._cloud = cloud_service
        self._email = email_service
    
    # ----- inyection getters -----
    def get_security_service(self) -> SecurityService:
        return None or self._security
    
    def get_session(self) -> Session:
        return None or self._session
    
    def get_cloud_service(self) -> CloudService:
        return None or self._cloud

    def get_email_service(self) -> EmailService:
        return None or self._email

    # ----- Services entrypoints -----
    # Cloud-service
    def is_owner_registered(self, owner: str) -> bool:
        is_registered = self._cloud.is_owner_registered(owner)
        return is_registered

    def send_ping(self) -> bool:
        is_online = self._cloud.send_ping()
        return is_online
    
    def upload_user(self, owner: str):
        return self._cloud.upload_user(owner)
    
    def delete_user(self, owner: str):
        return self._cloud.delete_user(owner)
    
    def get_pubkey(self, other: str):
        return self._cloud.get_user_pubkey(other)

    def send_data_to_cloud(self, rows: list[str], owner: str, consumers: list[str], on_request: bool=False):
        return self._cloud.send_data(rows, owner, consumers, on_request)

    # Email-service
    def send_email_with_fields(self, rows, recipients, filename, file_format):
        self._email.send_email_with_fields(rows, recipients, filename, file_format)