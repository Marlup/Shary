from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel

class BaseDTO(BaseModel):
    date_added: Optional[str|datetime] = "now"

class FieldDTO(BaseDTO):
    key: str
    value: str
    alias_key: Optional[str] = ""

class RequestDTO(BaseDTO):
    receivers: str
    keys: List[str]  # List of keys instead of CSV format for better parsing

class UserDTO(BaseDTO):
    username: str | None
    email: str | None

class OwnerDTO(BaseDTO):
    username: str | None
    email: str | None
    safe_password: str | None
