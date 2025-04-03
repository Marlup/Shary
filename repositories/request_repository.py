import sqlite3
from kivy.logger import Logger

from core.constant import PATH_DB
from core.queries import (
    INSERT_REQUEST,
    DELETE_REQUEST_BY_RECEIVERS
)
from core.interfaces import IRequestRepository

class RequestRepository(IRequestRepository):
    def __init__(self, db_connection=None):
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
        cursor.execute(DELETE_REQUEST_BY_RECEIVERS, (receivers,))
        self.db_connection.commit()
        cursor.close()

        return cursor
