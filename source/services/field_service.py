from repositories.field_repository import FieldRepository
from services.security_service import SecurityService
from core.dtos import FieldDTO
from typing import List, Tuple


class FieldService():
    def __init__(self, repo: FieldRepository, security_service: SecurityService):
        self.repo = repo
        self.security_service = security_service

    def encrypt_keys_before():
        def decorator(method):
            def wrapper(self, *args, **kwargs):
                keys = args[0]

                encrypted_keys = []
                for key, *_ in keys:
                    encrypted_key = self.security_service.encrypt(key.encode())
                    encrypted_keys.append((encrypted_key, ))

                return method(self, encrypted_keys)
            
            return wrapper
        return decorator

    def encrypt_field_before():
        def decorator(method):
            def wrapper(self, *args, **kwargs):
                key, value, alias_key, *_ = args
                data = (
                    self.security_service.encrypt(key.encode()),
                    self.security_service.encrypt(value.encode()),
                    self.security_service.encrypt(alias_key.encode()),
                )
                
                method(self, data)
            return wrapper
        return decorator

    def decrypt_fields_after():
        def decorator(method):
            def wrapper(self, *args, **kwargs):
                records = method(self, *args, **kwargs)

                fields = []
                for key, value, alias, date in records:
                    field = (
                        self.security_service.decrypt(key).decode(), 
                        self.security_service.decrypt(value).decode(), 
                        self.security_service.decrypt(alias).decode(),
                        date
                        )
                    fields.append(field)
                
                return fields
            return wrapper
        return decorator

    @encrypt_field_before()
    def create_field(self, field) -> FieldDTO:
        self.repo.add_field(field)

        return field

    @encrypt_keys_before()
    def delete_fields(self, keys: List[str]):
        if len(keys) == 1:
            key = keys[0][0]
            self.repo.delete_field(key)
        else:
            self.repo.delete_fields(keys)
    
    @decrypt_fields_after()
    def get_all_fields(self) -> List[Tuple[str]]:
        fields = self.repo.load_fields_from_db()
        
        return fields
