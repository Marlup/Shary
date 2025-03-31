from typing import List

import sqlite3
from kivy.logger import Logger

from front.core.interfaces import (
    IFieldRepository,
    IRequestRepository,
    IUserRepository
)

from front.core.dtos import (
    FieldDTO,
    UserDTO
)

from front.core.constant import (
    PATH_DB
)

from front.core.query_schema import *

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

# Implementation Example (Can be used later)
class RequestRepository(IRequestRepository):
    def __init__(self, db_connection):
        self.db_connection = db_connection if db_connection else sqlite3.connect(PATH_DB)

    def add_request(self, receivers, keys):
        cursor = self.db_connection.cursor()
        try:
            cursor.execute(INSERT_REQUEST, (receivers, keys))
            self.db_connection.commit()
        except sqlite3.IntegrityError:
            Logger.warning(f"IntegrityError: INSERT operation attempt failed \
                            for request {receivers}. Potential duplication.")
        cursor.close()

    def delete_request(self, receivers):
        cursor = self.db_connection.cursor()
        cursor.execute(DELETE_REQUEST_BY_RECEIVERS, (receivers, ))
        self.db_connection.commit()
        cursor.close()

        return cursor

class UserRepository(IUserRepository):
    def __init__(self, db_connection=None):
        self.db_connection = db_connection if db_connection else sqlite3.connect(PATH_DB)

    def add_user(self, user: UserDTO) -> None:
        cursor = self.db_connection.cursor()
        try:
            cursor.execute(INSERT_USER, 
                           (user.username, user.email, user.phone, user.extension))
            self.db_connection.commit()
        except sqlite3.IntegrityError:
            Logger.warning(f"IntegrityError: INSERT operation attempt failed for user {user.username}. Potential duplication.")
        finally:
            cursor.close()

    def load_users_from_db(self) -> List[UserDTO]:
        cursor = self.db_connection.cursor()
        cursor.execute(SELECT_ALL_USERS)
        records = cursor.fetchall()
        cursor.close()
        return [UserDTO(username=r[0], email=r[1], phone=r[2], extension=r[3], date_added=r[4]) for r in records]

    def delete_user(self, username: str) -> None:
        cursor = self.db_connection.cursor()
        cursor.execute(DELETE_USER_BY_USERNAME, (username,))
        self.db_connection.commit()
        cursor.close()

    def delete_users(self, usernames: List[str]) -> None:
        cursor = self.db_connection.cursor()
        cursor.executemany(DELETE_USER_BY_USERNAME, [(username,) for username in usernames])
        self.db_connection.commit()
        cursor.close()