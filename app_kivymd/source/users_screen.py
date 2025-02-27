# --- source/users_screen.py ---
from kivy.lang import Builder
from kivymd.uix.screen import MDScreen
from kivymd.uix.button import MDRaisedButton
from kivymd.toast import toast
from kivymd.uix.datatables import MDDataTable
from kivymd.uix.dialog import MDDialog
from kivy.uix.screenmanager import SlideTransition
from kivy.metrics import dp
from kivy.logger import Logger

from source.class_utils import (
    AddUser
)

class UsersScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(name="users", **kwargs)
        self.table = None
        self.dialog = Builder.load_file("widget_schemas/add_user_dialog.kv")  # Load the dialog definition

    def _delete_users(self):
        checked_rows = self.get_safe_row_checks()

        if not checked_rows:
            return
        
        if len(checked_rows) == 1:
            username = checked_rows[0][0]
            self.manager \
                .data_manager \
                .delete_user(username)
        else:
            usernames = self._get_cells_from_checked_rows(cell_as_tuple=True)
            self.manager \
                .data_manager \
                .delete_users(usernames)
        
        self._remove_rows_from_checked_rows()
    
    def _get_cells_from_checked_rows(self, index=0, cell_as_tuple=False):
        rows = self.get_safe_row_checks()
        if not rows:
            return

        cells = [
            (r[index], ) if cell_as_tuple else r[index] for r in rows
            ]
        print(f"cells - {cells}")
        return cells

    def _remove_rows_from_checked_rows(self):
        rows = self.get_safe_row_checks()
        if not rows:
            return
        
        for row in rows:
            Logger.critical(f"\n self.table - {self.table.row_data}")
            Logger.critical(f"\n row - {row}")
            self.table.remove_row(tuple(row))

    def _add_user(self, username, email, phone=0, phone_ext=0):
        self.manager.data_manager.add_user(username, email, phone, phone_ext)
        self.table.add_row((username, email, ""))

    def _load_users_from_db(self):
        #self.ids.table_container.remove_widget(self.table)
        if self.table:
            return
        
        records = self.manager.data_manager.load_users_from_db()

        self.table = MDDataTable(
            size_hint=(1, 0.8),
            use_pagination=True,
            check=True,
            column_data=[
                ("Username", dp(30)),
                ("Email", dp(40)),
                ("Creation Date", dp(30)),
            ],
            row_data=[
                (
                    record[0],
                    record[1],
                    record[2],
                )
                for record in records
            ],
        )
        self.ids.table_container.add_widget(self.table)
    
    def show_add_user_dialog(self):
        self.dialog = MDDialog(
            title="Add New User",
            type="custom",
            content_cls=AddUser(size_hint_y=None, height="200dp"),  # Adjust height here
            buttons=[
                MDRaisedButton(text="CANCEL", on_release=lambda x: self.dialog.dismiss()),
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
            toast(f"User '{username}' added successfully!")
        else:
            toast("Both Username and Email are required.")
    
    def get_safe_row_checks(self):
        if self.table is None:
            return []
        if self.table.get_row_checks():
            return self.table.get_row_checks()
        return []

    def get_checked_emails(self, index=0):
        return self._get_cells_from_checked_rows(index)
    
    def go_to_fields_screen(self):
        self.manager.transition = SlideTransition(direction="right", duration=0.4)
        self.manager.current = "fields"
    
    def go_to_requests_screen(self):
        self.manager.transition = SlideTransition(direction="left", duration=0.4)
        self.manager.current = "requests"

    def on_enter(self):
        self._load_users_from_db()

def get_users_screen():
    Builder.load_file("widget_schemas/users.kv")
    return UsersScreen()
