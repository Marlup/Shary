from typing import List
import sqlite3
from kivy.logger import Logger

from front.core.constant import PATH_DB
from front.core.query_schema import (
    INSERT_FIELD,
    DELETE_FIELD_BY_KEY,
    SELECT_ALL_FIELDS
)
from front.core.interfaces import IFieldRepository
from front.core.dtos import FieldDTO

class FieldRepository(IFieldRepository):
    def __init__(self, db_connection=None):
        self.db_connection = db_connection if db_connection else sqlite3.connect(PATH_DB)

    def add_field(self, field: FieldDTO) -> None:
        cursor = self.db_connection.cursor()
        try:
            cursor.execute(INSERT_FIELD, (field.key, field.value, field.alias_key))
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
        return [FieldDTO(key=r[0], value=r[1], alias_key=r[2], date_added=r[3]) for r in records]
