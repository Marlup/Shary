import time
import json
import threading

from kivy.lang import Builder
from kivymd.uix.dialog import MDDialog
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.screen  import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.logger import Logger

from firebase_admin import firestore
from kivy.clock import mainthread
import sqlite3

# Import your Firebase initialization and encryption functions
from core.func_utils import request_access_db_firebase

from core.func_utils import (
    load_user_credentials,
    build_email_html_body,
    send_email,
    information_panel
)


from core.constant import FILE_FORMATS, MSG_DEFAULT_SEND_FILENAME

from core.query_schemas import (
    # Queries for users 
    SELECT_ALL_USERS,
    DELETE_USER_BY_USERNAME,
    INSERT_USER,
    # Queries for fields 
    SELECT_ALL_FIELDS,
    DELETE_FIELD_BY_KEY,
    INSERT_FIELD,
    # Queries for Requests 
    DELETE_REQUEST_BY_RECEIVERS,
    INSERT_REQUEST,
)

class Utils():
    @staticmethod
    def remove_table(func):
        """Removes the table from 'table_container' layout."""
        def wrapper(self, *args, **kwargs):
            func_results = func(self, *args, **kwargs)
            self.ids.table_container.remove_widget(self.table)
            return func_results
        return wrapper

class EnhancedMDScreen(MDScreen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.checked_rows = []
    
    def on_row_check(self, instance_table, current_row):
        """Manually track selected rows when checkboxes are clicked."""
        if current_row in self.checked_rows:
            self.checked_rows.remove(current_row)  # Uncheck → Remove from list
        else:
            self.checked_rows.append(current_row)  # Check → Add to list

        print("Manually Tracked Checked Rows:", self.checked_rows)

class AddUser(MDBoxLayout):
    pass

class AddRequestField(MDBoxLayout):
    pass

class AddField(MDBoxLayout):
    pass

class SendEmailDialog(MDBoxLayout):
    pass

class SendToFirebaseDialog(MDBoxLayout):
    pass

class SelectChannel(MDBoxLayout):
    pass

class DataManager():
    def __init__(self):
        self.db_connection = sqlite3.connect("shary_demo")
    
    @staticmethod
    def log_rows_affected(func):
        def wrapper(*args, **kwargs):
            cursor = func(*args, **kwargs)
            if cursor.rowcount == 0:
                Logger.info(f"0 records affected at function {func.__name__} \
                            operation")
        return wrapper
    
    def add_request(self, receivers, keys):
        cursor = self.db_connection.cursor()
        try:
            cursor.execute(INSERT_REQUEST, (receivers, keys))
            self.db_connection.commit()
        except sqlite3.IntegrityError:
            Logger.warning(f"IntegrityError: INSERT operation attempt failed \
                            for request {receivers}. Potential duplication.")
        cursor.close()

    @log_rows_affected
    def delete_request(self, receivers):
        cursor = self.db_connection.cursor()
        cursor.execute(DELETE_REQUEST_BY_RECEIVERS, (receivers, ))
        self.db_connection.commit()
        cursor.close()

        return cursor

    def add_user(self, username, email, phone=0, extension=0):
        cursor = self.db_connection.cursor()
        try:
            cursor.execute(INSERT_USER, (username, email, phone, extension))
            self.db_connection.commit()
        except sqlite3.IntegrityError:
            Logger.warning(f"IntegrityError: INSERT operation attempt failed \
                            for user {username}. Potential duplication.")
        cursor.close()

    def load_users_from_db(self):
        cursor = self.db_connection.cursor()
        cursor.execute(SELECT_ALL_USERS)
        records = cursor.fetchall()
        cursor.close()

        return records

    @log_rows_affected
    def delete_user(self, username):
        cursor = self.db_connection.cursor()
        cursor.execute(DELETE_USER_BY_USERNAME, (username, ))
        self.db_connection.commit()
        cursor.close()
        return cursor
    
    @log_rows_affected
    def delete_users(self, usernames):
        cursor = self.db_connection.cursor()
        cursor.executemany(DELETE_USER_BY_USERNAME, usernames)
        cursor.close()
        return cursor

    def add_field(self, key, value, alias_key=""):
        cursor = self.db_connection.cursor()
        try:
            cursor.execute(INSERT_FIELD, (key, value, alias_key))
            self.db_connection.commit()
        except sqlite3.IntegrityError:
            Logger.warning(f"IntegrityError: INSERT operation attempt failed \
                            for key {key}. Potential duplication.")
        cursor.close()

    def load_fields_from_db(self):
        cursor = self.db_connection.cursor()
        cursor.execute(SELECT_ALL_FIELDS)
        records = cursor.fetchall()
        cursor.close()

        return records

    @log_rows_affected
    def delete_field(self, key):
        cursor = self.db_connection.cursor()
        cursor.execute(DELETE_FIELD_BY_KEY, (key,))
        self.db_connection.commit()
        cursor.close()
        return cursor

    @log_rows_affected
    def delete_fields(self, keys):
        cursor = self.db_connection.cursor()
        cursor.executemany(DELETE_FIELD_BY_KEY, keys)
        self.db_connection.commit()
        cursor.close()
        return cursor

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

class FirebaseManager:
    firebase_collection_name = "sharing"
    check_interval = 30  # Default check interval in seconds

    def __init__(self, app):
        """
        Initializes the Firebase manager.
        :param app: Reference to the main KivyMD app.
        """
        self.app = app
        self.db = request_access_db_firebase()
        self.running = False
        self.session_requests = []  # List of (session_id, secret_key) tuples
        self.checking_thread = None

    def add_request(self, session_id, secret_key):
        """
        Adds a new request to be monitored.
        """
        if (session_id, secret_key) not in self.session_requests:
            self.session_requests.append((session_id, secret_key))
            print(f"🔍 Added session {session_id} for monitoring.")

        # Start checking if it's not already running
        if not self.running:
            self.running = True
            self.checking_thread = threading.Thread(target=self.check_sessions)
            self.checking_thread.start()

    def check_sessions(self):
        """
        Periodically checks all session requests.
        """
        while self.running:
            if not self.session_requests:
                print("✅ No pending requests. Stopping checks.")
                self.running = False
                break  # Stop the loop if no requests
            
            # Check all pending requests
            self._check_sessions()

    def _check_sessions(self):
        # Iterate over a copy of the list to avoid issues during removal
        for session_id, secret_key in list(self.session_requests):
            self._check_session(session_id, secret_key)

    def _check_session(self, session_id, secret_key):
            doc_ref = self.db \
                          .collection(self.firebase_collection_name) \
                          .document(session_id)
            doc = doc_ref.get()

            if not doc.exists:
                print(f"⏳ Session {session_id} not found. Checking again in {self.check_interval} sec...")
                time.sleep(self.check_interval)
                return  # Skip if the document doesn't exist

            data = doc.to_dict()
            sender = data.get("sender", "Unknown")
            fields = self.decrypt_data(data["data"])  # Decrypt the stored data
            verification_code = data.get("verification_code", "")

            if self.validate_verification_code(verification_code, data["nonce"]):
                # Remove from the pending list
                self.session_requests.remove((session_id, secret_key))

                # Update UI on the main thread
                self.update_ui(sender, fields, session_id)

                print(f"✅ Data verified from {sender}: {fields}")
            else:
                print(f"⚠️ Verification failed for {session_id}. Retrying...")
            
            return

    @mainthread
    def update_ui(self, sender, fields, session_id):
        """
        Updates the UI when a session is verified.
        This runs on the main thread to prevent UI crashes.
        """
        print(f"🎉 Data received from {sender}: {fields}")
        screen = self.app.root.get_screen("fields")
        screen.update_list(sender, fields, session_id)  # Call a UI update method

    def validate_verification_code(self, verification_code, nonce):
        """
        Validates the verification code (simulated).
        """
        return bool(verification_code and nonce)

    def decrypt_data(self, encrypted_data):
        """
        Decrypts the data (stub function).
        """
        try:
            return json.loads(encrypted_data)  # Replace with actual decryption logic
        except json.JSONDecodeError:
            return []

    def delete_file(self, session_id):
        """
        Deletes a file from Firebase.
        """
        doc_ref = self.db \
                      .collection(self.firebase_collection_name) \
                      .document(session_id)
        doc_ref.delete()
        print(f"🗑️ Session {session_id} deleted from Firebase.")
