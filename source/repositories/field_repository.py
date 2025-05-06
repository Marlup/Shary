import sqlite3
from typing import List
from kivy.logger import Logger

from core.constant import PATH_DB
from core.queries import (
    INSERT_FIELD,
    DELETE_FIELD_BY_KEY,
    SELECT_ALL_FIELDS
)

from core.dtos import FieldDTO
from core.interfaces import IFieldRepository
from services.security_service import SecurityService


class FieldRepository(IFieldRepository):
    def __init__(self, db_connection=None):
        self.db_connection = db_connection if db_connection else sqlite3.connect(PATH_DB)

    def add_field(self, field: List[str]) -> None:
        cursor = self.db_connection.cursor()

        try:
            cursor.execute(INSERT_FIELD, field)
            self.db_connection.commit()
        except sqlite3.IntegrityError:
            Logger.warning(f"IntegrityError: INSERT operation attempt failed for key {field.key}. Potential duplication.")
        finally:
            cursor.close()

    def delete_field(self, key: str) -> None:
        cursor = self.db_connection.cursor()
        cursor.execute(DELETE_FIELD_BY_KEY, (key,))
        self.db_connection.commit()
        cursor.close()

    def delete_fields(self, keys: List[str]) -> None:
        cursor = self.db_connection.cursor()
        cursor.executemany(DELETE_FIELD_BY_KEY, [(key,) for key in keys])
        self.db_connection.commit()
        cursor.close()

    def load_fields_from_db(self) -> List[FieldDTO]:
        cursor = self.db_connection.cursor()
        cursor.execute(SELECT_ALL_FIELDS)
        records = cursor.fetchall()
        cursor.close()

        return records #[FieldDTO(key=r[0], value=r[3], alias_key=r[2], date_added=r[3]) for r in records]
