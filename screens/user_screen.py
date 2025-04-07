# --- source/users_screen.py ---
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.logger import Logger
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.datatables import MDDataTable
from kivymd.uix.snackbar import MDSnackbar
from kivymd.uix.dialog import MDDialog

from core.classes import (
    AddUser,
    EnhancedMDScreen
)

from core.functions import (
    get_checked_rows
)

from core.constant import (
    DEFAULT_ROW_KEY_WIDTH,
    DEFAULT_NUM_ROWS_PAGE,
    DEFAULT_USE_PAGINATION,
    SCREEN_NAME_FIELD,
    SCREEN_NAME_REQUEST,
    SCREEN_NAME_USER,
    PATH_SCHEMA_USER_DIALOG,
)

from core.dtos import UserDTO
from repositories.user_repository import UserRepository

class UserScreen(EnhancedMDScreen):
    def __init__(self, db_connection=None, **kwargs):
        super().__init__(name=SCREEN_NAME_USER, **kwargs)
        self.user_repo = UserRepository(db_connection)
        
        self.dialog = Builder.load_file(PATH_SCHEMA_USER_DIALOG)  # Load the dialog definition
        
        self.main_table = None

    def _delete_users(self):
        checked_rows = get_checked_rows(self.main_table, self.checked_rows)

        if not checked_rows:
            return
        
        if len(checked_rows) == 1:
            username = checked_rows[0][0]
            self.user_repo.delete_user(username)
        else:
            usernames = self._get_cells_from_checked_rows(cell_as_tuple=True)
            self.user_repo.delete_users(usernames)
        
        self._remove_rows_from_checked_rows()
    
    def _get_cells_from_checked_rows(self, index=0, cell_as_tuple=False):
        rows = get_checked_rows(self.main_table, self.checked_rows)

        if not rows:
            return

        cells = [
            (r[index], ) if cell_as_tuple else r[index] for r in rows
            ]
        return cells

    def _remove_rows_from_checked_rows(self):
        rows = get_checked_rows(self.main_table, self.checked_rows)
        if not rows:
            return
        
        for row in rows:
            Logger.critical(f"\n self.main_table - {self.main_table.row_data}")
            Logger.critical(f"\n row - {row}")
            self.main_table.remove_row(tuple(row))
            self.checked_rows.remove(row)

    def _add_user(self, username, email):
        user = UserDTO(username=username, email=email)
        self.user_repo.add_user(user)
        self.main_table.add_row((username, email, ""))
    
    def _load_users_from_db(self):
        if self.main_table:
            return
        
        records = self.user_repo.load_users_from_db()

        self.main_table = MDDataTable(
            size_hint=(1, 0.8),
            pos_hint={"center_x": 0.5, "center_y": 0.5},  # Ensure centering
            check=True,
            column_data=[
                ("Username", dp(DEFAULT_ROW_KEY_WIDTH)),
                ("Email", dp(DEFAULT_ROW_KEY_WIDTH + 10)),
                ("Creation Date", dp(DEFAULT_ROW_KEY_WIDTH)),
            ],
            row_data=[(r.username, r.email, r.date_added) for r in records],
            use_pagination=DEFAULT_USE_PAGINATION,
            rows_num=DEFAULT_NUM_ROWS_PAGE,
            pagination_menu_height=dp(300),  # Set dropdown menu height
        )

        # Bind checkbox selection event
        self.main_table.bind(on_check_press=self.on_row_check)
        self.ids.table_container.add_widget(self.main_table)
    
    def show_add_user_dialog(self):
        self.dialog = MDDialog(
            title="Add New User",
            type="custom",
            content_cls=AddUser(size_hint_y=None, height="200dp"),  # Adjust height here
            buttons=[
                MDRaisedButton(text="CANCEL", on_release=lambda _: self.dialog.dismiss()),
                MDRaisedButton(text="ADD", on_release=lambda _: self.add_user_from_popup()),
            ],
        )
        self.dialog.open()

    def add_user_from_popup(self, *args):
        #Logger.info(f"ids for root {self.ids}")
        #Logger.info(f"ids for root.dialog {self.dialog.ids}")
        #Logger.info(f"ids for root.dialog.content_cls {self.dialog.content_cls.ids}")

        dialog_ids = self.dialog.content_cls.ids
        username = dialog_ids.username_input.text.strip()
        email = dialog_ids.email_input.text.strip()
        # TODO add phone and extension

        if username and email:
            self._add_user(username, email)
            self.dialog.dismiss()
            #toast(f"User '{username}' added successfully!")
            MDSnackbar(f"User '{username}' added successfully!").open()
        else:
            #toast("Both Username and Email are required.")
            MDSnackbar("Both Username and Email are required.").open()

    def get_checked_emails(self, index):
        return self._get_cells_from_checked_rows(index)
    
    def go_to_fields_screen(self):
        self.manager.go_to_user_screen("right")
    
    def go_to_requests_screen(self):
        self.manager.g_oto_request_screen("left")

    def on_enter(self):
        self._load_users_from_db()