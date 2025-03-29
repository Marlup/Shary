from abc import ABC, abstractmethod
from typing import List
from .dtos import FieldDTO, UserDTO, RequestDTO

# Interfaces
class IFieldRepository(ABC):
    @abstractmethod
    def add_field(self, field: FieldDTO) -> None:
        pass
    
    @abstractmethod
    def delete_field(self, key: str) -> None:
        pass
    
    @abstractmethod
    def delete_fields(self, keys: List[str]) -> None:
        pass
    
    @abstractmethod
    def load_fields_from_db(self) -> List[FieldDTO]:
        pass


class IRequestRepository(ABC):
    @abstractmethod
    def add_request(self, request: RequestDTO) -> None:
        pass
    
    @abstractmethod
    def delete_request(self, receivers: str) -> None:
        pass


class IUserRepository(ABC):
    @abstractmethod
    def add_user(self, user: UserDTO) -> None:
        pass
    
    @abstractmethod
    def delete_user(self, username: str) -> None:
        pass
    
    @abstractmethod
    def delete_users(self, usernames: List[str]) -> None:
        pass
    
    @abstractmethod
    def load_users_from_db(self) -> List[UserDTO]:
        pass