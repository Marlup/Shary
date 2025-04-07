from typing import List
import sqlite3
from kivy.logger import Logger

from core.constant import PATH_DB
from core.queries import (
    INSERT_USER,
    SELECT_ALL_USERS,
    DELETE_USER_BY_USERNAME
)
from core.interfaces import IUserRepository
from core.dtos import UserDTO

class UserRepository(IUserRepository):
    def __init__(self, db_connection=None):
        self.db_connection = db_connection if db_connection else sqlite3.connect(PATH_DB)

    def add_user(self, user: UserDTO) -> None:
        cursor = self.db_connection.cursor()
        try:
            cursor.execute(INSERT_USER, (user.username, user.email))
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
        return [UserDTO(username=r[0], email=r[1]) for r in records]

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