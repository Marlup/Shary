# core/app_controller.py

from services.cloud_service import CloudService
from services.email_service import EmailService

class AppController:
    def __init__(
            self, 
            cloud_service: CloudService, 
            email_service: EmailService, 
            ):
        # Services
        self.cloud = cloud_service
        self.email = email_service
    
    # ----- Services entrypoints -----
    # Cloud-service
    def is_owner_registered(self, owner: str):
        return self.cloud.is_owner_registered(owner)

    def send_ping(self):
        return self.cloud.send_ping()
    
    def store_user(self, owner: str):
        return self.cloud.store_user(owner)
    
    def delete_user(self, owner: str):
        return self.cloud.delete_user(owner)
    
    def get_pubkey(self, other: str):
        return self.cloud.get_other_pubkey(other)

    def send_data_to_cloud(self, rows: list[str], owner: str, consumers: list[str], on_request: bool=False):
        return self.cloud.send_data(rows, owner, consumers, on_request)

    # Email-service
    def send_email_with_fields(self, rows, recipients, filename, file_format):
        payload = self.email.create_payload(rows, recipients, filename, file_format)
        if payload:
            self.email.send_from_payload(payload)