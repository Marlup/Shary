from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel

class FieldDTO(BaseModel):
    key: str
    value: str
    alias_key: Optional[str] = ""
    date_added: Optional[str|datetime] = "now"

class RequestDTO(BaseModel):
    receivers: str
    keys: List[str]  # List of keys instead of CSV format for better parsing
    creation_date: Optional[str|datetime] = "now"

class UserDTO(BaseModel):
    username: str | None
    email: str | None
    date_added: Optional[str|datetime] = "now"

class OwnerDTO(BaseModel):
    username: str | None
    email: str | None
    safe_password: str | None
