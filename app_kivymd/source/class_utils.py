from kivymd.uix.screen  import MDScreen
import sqlite3

from source.constant import (
    ROW_HEIGHT
)

from source.query_schemas import (
    # Queries for users 
    SELECT_ALL_USERS,
    DELETE_USER_BY_USERNAME,
    INSERT_USER,
    # Queries for fields 
    SELECT_ALL_FIELDS,
    DELETE_FIELD_BY_KEY,
    INSERT_FIELD,
)

class DataManager():
    def __init__(self):
        self.db_connection = sqlite3.connect("shary_demo")
    
    def add_user(self, username, email, phone=0, extension=0):
        cursor = self.db_connection.cursor()
        cursor.execute(INSERT_USER, (username, email, phone, extension))
        self.db_connection.commit()
        cursor.close()

    def load_users_from_db(self):
        cursor = self.db_connection.cursor()
        cursor.execute(SELECT_ALL_USERS)
        records = cursor.fetchall()
        cursor.close()

        return records

    def delete_user(self, username):
        cursor = self.db_connection.cursor()
        cursor.execute(DELETE_USER_BY_USERNAME, (username,))
        self.db_connection.commit()
        cursor.close()

    def delete_users(self, usernames):
        cursor = self.db_connection.cursor()
        cursor.executemany(DELETE_USER_BY_USERNAME, usernames)
        self.db_connection.commit()
        cursor.close()

    def add_field(self, key, value, custom_name=""):
        cursor = self.db_connection.cursor()
        cursor.execute(INSERT_FIELD, (key, value, custom_name))
        self.db_connection.commit()
        cursor.close()

    def load_fields_from_db(self):
        cursor = self.db_connection.cursor()
        cursor.execute(SELECT_ALL_FIELDS)
        records = cursor.fetchall()
        cursor.close()

        return records

    def delete_field(self, key):
        cursor = self.db_connection.cursor()
        cursor.execute(DELETE_FIELD_BY_KEY, (key,))
        self.db_connection.commit()
        cursor.close()

    def delete_fields(self, keys):
        cursor = self.db_connection.cursor()
        cursor.executemany(DELETE_FIELD_BY_KEY, keys)
        self.db_connection.commit()
        cursor.close()

# --- source/email_handler.py ---
from kivy.lang import Builder
from kivymd.uix.dialog import MDDialog
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.boxlayout import MDBoxLayout
from source.func_utils import (
    load_user_credentials,
    build_email_html_body,
    send_email,
    information_panel
)
from source.constant import FILE_FORMATS, MSG_DEFAULT_SEND_FILENAME

class EmailHandler():
    def __init__(self, parent_screen: MDScreen):
        self.parent_screen = parent_screen
        self.dialog = None
        self.dropdown_menu = None
        Builder.load_file("widget_schemas/send_email_dialog.kv")

    """   
    def show_send_email_dialog(self):
        print(f"self, self.parent_screen - {self, self.parent_screen}")
        if not self.dialog:
            self.dialog = MDDialog(
                title="Send Fields via Email",
                type="custom",
                content_cls=SendEmailDialog(size_hint_y=None, height="200dp"),
            )
            self._init_dropdown_menu()
        self.dialog.open()
    """

    def _init_dropdown_menu(self):
        menu_items = [
            {
                "text": f"{format}",
                "on_release": lambda x=f"{format}": self.set_file_format(x),
            }
            for format in FILE_FORMATS
        ]
        self.dropdown_menu = MDDropdownMenu(
            caller=self.dialog.content_cls.ids.file_format_dropdown,
            items=menu_items,
            width_mult=4,
        )

    def set_file_format(self, file_format):
        self.dialog.content_cls.ids.file_format_dropdown.text = file_format
        self.dropdown_menu.dismiss()

    def send_email_from_dialog(self):
        dialog_ids = self.dialog.content_cls.ids
        filename = dialog_ids.filename_input.text.strip()
        file_format = dialog_ids.file_format_dropdown.text.strip()

        if not filename:
            sender_email, _ = load_user_credentials()
            sender_name = sender_email.split("@")[0]
            filename = f"{MSG_DEFAULT_SEND_FILENAME}{sender_name}"
        filename += f".{file_format}"

        if file_format not in FILE_FORMATS:
            information_panel("Action: sending email", "Invalid file format.")
            return

        recipients = self.parent_screen.manager.get_screen("users").get_selected_emails()
        if not recipients:
            information_panel("Action: sending email", "Select at least one external user to send to.")
            return

        sender_email, sender_password = load_user_credentials()
        subject = f"Shary message with {len(self.parent_screen._selected_fields)} fields"
        message = build_email_html_body(
            sender_email,
            recipients,
            subject,
            filename,
            file_format,
            self.parent_screen._selected_fields,
        )

        return_message = send_email(sender_email, sender_password, message)
        if return_message == "":
            information_panel("Action: sending email", "Email sent successfully")
        elif return_message == "bad-format":
            information_panel("Action: sending email", "Invalid file format.")
        else:
            information_panel("Action: sending email", f"Error at sending: {str(return_message)}")
        self.dialog.dismiss()

    def dismiss_email_dialog(self):
        if self.dialog:
            self.dialog.dismiss()
