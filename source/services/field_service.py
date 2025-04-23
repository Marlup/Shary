from repositories.field_repository import FieldRepository
from core.dtos import FieldDTO
from typing import List, Tuple


class FieldService():
    def __init__(self, repo: FieldRepository):
        self.repo = repo

    def create_field(self, key: str, value: str, alias_key: str = "") -> FieldDTO:
        field = FieldDTO(key=key, value=value, alias_key=alias_key)
        self.repo.add_field(field)
        return field

    def delete_fields(self, keys: List[Tuple[str]]):
        if len(keys) == 1:
            key = keys[0][0]
            self.repo.delete_field(key)
        else:
            self.repo.delete_fields(keys)

    def get_all_fields(self) -> List[Tuple[str]]:
        fields_dtos = self.repo.load_fields_from_db()
        fields_data = [(f.key, f.value, f.date_added) for f in fields_dtos]
        
        return fields_data
