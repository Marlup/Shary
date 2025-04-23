# --- source/requests_screen.py ---

from kivy.lang import Builder
from kivy.metrics import dp
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.snackbar import MDSnackbar
from kivymd.uix.dialog import MDDialog

from core.classes import (
    RequestFieldDialog,
    SendEmailDialog,
    EnhancedTableMDScreen,
)
from core.constant import (
    DEFAULT_ROW_KEY_WIDTH,
    DEFAULT_ROW_VALUE_WIDTH,
    SCREEN_NAME_REQUESTS,
    PATH_SCHEMA_REQUEST_DIALOG,
)
from services.email_service import EmailService
from services.request_service import RequestService
from core.session import Session
from core.functions import information_panel

class RequestsScreen(EnhancedTableMDScreen):
    def __init__(self, request_service: RequestService, session: Session, email_service: EmailService, **kwargs):
        super().__init__(name=SCREEN_NAME_REQUESTS, **kwargs)
        self.request_service = request_service
        self.email_service = email_service
        self.session = session

        Builder.load_file(PATH_SCHEMA_REQUEST_DIALOG)

        self.request_dialog = None
        self.email_dialog = None

    # ----- Callbacks current screen events -----
    def on_enter(self):
        self._load_requests_from_db()

    # ----- Navigation -----
    def go_to_fields_screen(self):
        self.manager.go_to_fields_screen("left")

    def go_to_users_screen(self):
        self.manager.go_to_users_screen("right")

    # ----- Dialog: Add request field -----
    def show_request_dialog(self):
        self.request_dialog = MDDialog(
            title="Add Field to be requested",
            type="custom",
            content_cls=RequestFieldDialog(size_hint_y=None, height="150dp"),
            buttons=[
                MDRaisedButton(text="CANCEL", on_release=lambda _: self.request_dialog.dismiss()),
                MDRaisedButton(text="ADD", on_release=lambda _: self.add_request_from_popup()),
            ],
        )
        self.request_dialog.open()

    def add_request_from_popup(self, *args):
        key = self._get_ui_key()
        alt_key_name = self._get_ui_alt_key_name()

        if key:
            self._add_request(key, alt_key_name)
            self.request_dialog.dismiss()
            MDSnackbar(f"Request field '{key}' added successfully!").open()
        else:
            MDSnackbar("Key is required.").open()

    # ----- Dialog: Send email -----
    def show_send_email_dialog(self):
        if not self.email_dialog:
            self.email_dialog = MDDialog(
                title="Send Request Fields via Email",
                type="custom",
                content_cls=SendEmailDialog(size_hint_y=None, height="200dp"),
                buttons=[
                    MDRaisedButton(text="Cancel", on_release=lambda _: self.email_dialog.dismiss()),
                    MDRaisedButton(text="Send", on_release=lambda _: self.send_email_from_dialog()),
                ],
            )
        self.email_dialog.open()

    def send_email_from_dialog(self):
        # Load the data for the payload
        filename = self._get_ui_filename_attach()
        requested_keys = self._get_checked_requested_keys()
        if not requested_keys or not filename:
            information_panel("Action: sending email", "No requested keys or filename provided")
            return

        # Load the services
        users: list = self.session.get_checked_users()

        # Send email
        self.email_service.send_email_with_fields(requested_keys, users, filename)

        information_panel("Action: sending email", "Email sent successfully")
        self.email_dialog.dismiss()

    # ----- UI Methods -----
    def _get_ui_filename_attach(self):
        return self.email_dialog.content_cls.ids.filename_input.text.strip()

    def _get_ui_key(self):
        return self.request_dialog.content_cls.ids.key_input.text.strip()

    def _get_ui_alt_key_name(self):
        return self.request_dialog.content_cls.ids.alt_key_name_input.text.strip()

    # ----- Table Data Management -----
    def _load_requests_from_db(self):
        column_data = [
            ("Key", dp(DEFAULT_ROW_KEY_WIDTH)),
            ("Other Names", dp(DEFAULT_ROW_VALUE_WIDTH)),
        ]
        self._initialize_table(column_data)

    def _add_request(self, key, alt_key_name):
        #self.request_service.create_request((key, alt_key_name))
        self._add_row((key, alt_key_name))

    def _delete_fields(self):
        receivers = self._delete_rows()
        
        if not receivers:
            MDSnackbar(f"No receivers selected.").open()
            return
        
        #self.request_service.delete_request(receivers)

    # ----- Internal methods -----
    def _get_checked_requested_keys(self) -> list[str]:
        return self._get_checked_rows()