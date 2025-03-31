import time
import json
import threading

from kivy.lang import Builder
from kivy.logger import Logger
from kivy.clock import mainthread
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.screen  import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout

import sqlite3

from front.core.func_utils import (
    load_user_credentials,
    information_panel
)

from front.core.constant import FILE_FORMATS, MSG_DEFAULT_SEND_FILENAME
from front.security.crypto import RSACrypto

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

class FirebaseManager():
    firebase_collection_name = "sharing"
    check_interval = 30  # Default check interval in seconds

    def __init__(self, app, cryptographer: RSACrypto):
        """
        Initializes the Firebase manager.
        :param app: Reference to the main KivyMD app.
        """
        self.app = app
        self.cryptographer = cryptographer
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

            if data["mode"] == "request":
                pass
            elif data["mode"] == "send":
                #fields = self.cryptographer.decrypt(data["data"])  # Decrypt the stored data
                pass
            elif data["mode"] == "share-pubkey":
                #received_pubkey = data["data"]  # Decrypt the stored data
                pass

            sender = data.get("sender", "Unknown")
            verification_hash = data.get("verification_hash", "")

            if self.validate_verification_hash(verification_hash, data["nonce"]):
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

    def validate_verification_hash(self, verification_hash, nonce):
        """
        Validates the verification code (simulated).
        """
        return bool(verification_hash and nonce)

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
