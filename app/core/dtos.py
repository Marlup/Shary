from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

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
    username: str
    email: str
    phone: Optional[int] = 0
    extension: Optional[int] = 0
    date_added: Optional[str|datetime] = "now"