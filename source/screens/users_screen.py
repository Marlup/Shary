# --- source/users_screen.py ---

from kivy.lang import Builder
from kivy.metrics import dp
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.snackbar import MDSnackbar
from kivymd.uix.dialog import MDDialog

from core.classes import (
    UserDialog,
    EnhancedTableMDScreen
)

from core.constant import (
    DEFAULT_ROW_KEY_WIDTH,
    SCREEN_NAME_USERS,
    PATH_SCHEMA_USER_DIALOG,
)

from services.user_service import UserService
from core.session import Session


class UsersScreen(EnhancedTableMDScreen):
    def __init__(self, user_service: UserService, session: Session, **kwargs):
        super().__init__(name=SCREEN_NAME_USERS, **kwargs)
        self.user_service = user_service
        self.session = session
        
        self.dialog = Builder.load_file(PATH_SCHEMA_USER_DIALOG)  # Load the dialog definition
    
    def open_add_dialog(self):
        self.dialog = MDDialog(
            title="Add New User",
            type="custom",
            content_cls=UserDialog(size_hint_y=None, height="200dp"),  # Adjust height here
            buttons=[
                MDRaisedButton(text="CANCEL", on_release=lambda _: self.dialog.dismiss()),
                MDRaisedButton(text="ADD", on_release=lambda _: self.validate_add_user()),
            ],
        )
        self.dialog.open()

    def validate_add_user(self, *args):
        username = self.get_ui_username()
        email = self.get_ui_email()

        # TODO add phone and extension

        if username and email:
            self._add_user(username, email)
            self.dialog.dismiss()
            MDSnackbar(f"User '{username}' added successfully!").open()
        else:
            MDSnackbar("Both Username and Email are required.").open()

    def _cache_checked_users_in_session(self):
        """Cache users checked from the Users UI table"""
        emails = self._get_checked_emails()
        self.session.set_checked_users(emails)
    
    def go_to_fields_screen(self):
        self.manager.go_to_fields_screen("right")
    
    def go_to_requests_screen(self):
        self.manager.go_to_requests_screen("left")

    # Callbacks current screen events
    def on_enter(self):
        self._load_table_from_db()
    
    def on_leave(self):
        self._cache_checked_users_in_session()

    # ----- UI methods -----
    def get_ui_username(self):
        dialog_ids = self.dialog.content_cls.ids
        return dialog_ids.username_input.text.strip()

    def get_ui_email(self):
        dialog_ids = self.dialog.content_cls.ids
        return dialog_ids.email_input.text.strip()

    # ----- Internal methods -----
    def _get_checked_users(self) -> list[str]:
        return self._get_checked_rows()
    
    def _delete_users(self):
        usernames = self._delete_rows()

        if not usernames:
            MDSnackbar(f"No users selected.").open()
            return
        
        self.user_service.delete_users(usernames)
    
    #def _get_checked_usernames(self):
    #    return self._get_cells_from_checked_rows(0, True)
    
    def _get_checked_emails(self):
        return self._get_checked_cells(1)

    def _add_user(self, username, email):
        self.user_service.create_user(username, email)
        self._add_row((username, email, ""))
    
    def _load_table_from_db(self):
        column_data = [
            ("Username", dp(DEFAULT_ROW_KEY_WIDTH)),
            ("Email", dp(DEFAULT_ROW_KEY_WIDTH + 10)),
            ("Creation Date", dp(DEFAULT_ROW_KEY_WIDTH)),
            ]
        
        users_data = self.user_service.get_all_users()
        self._initialize_table(column_data, users_data)