# --- source/users_screen.py ---
from kivy.lang import Builder
from kivymd.uix.screen import MDScreen
from kivymd.uix.button import MDRaisedButton
from kivymd.toast import toast
from kivymd.uix.datatables import MDDataTable
from kivymd.uix.dialog import MDDialog
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.uix.screenmanager import SlideTransition
from kivy.metrics import dp
from kivy.logger import Logger

import sqlite3

from source.query_schemas import (
    SELECT_ALL_USERS,
    DELETE_USER_BY_USERNAME,
    INSERT_USER
)

class AddUser(MDBoxLayout):
    pass

class UsersScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(name="users", **kwargs)
        self._selected_users = []
        self.table = None
        self.dialog = Builder.load_file("widget_schemas/add_user_dialog.kv")  # Load the dialog definition

    def update_selected_users(self, instance, row_data):
        if row_data in self._selected_users:
            self._selected_users.remove(row_data)
        else:
            self._selected_users.append(row_data)

    def _delete_users(self):
        if not self._selected_users:
            return
        if len(self._selected_users) == 1:
            self.manager \
                .data_manager \
                .delete_user(self._selected_users)
        else:
            self.manager \
                .data_manager \
                .delete_users(self._selected_users)
        self._load_users_from_db()

    def _add_user(self, username, email):
        self.manager.data_manager.add_user(username, email)
        self._load_users_from_db()

    def _load_users_from_db(self):
        records = self.manager.data_manager.load_users_from_db()

        if self.table:
            self.ids.table_container.remove_widget(self.table)

        self.table = MDDataTable(
            size_hint=(1, 0.8),
            use_pagination=True,
            check=True,
            column_data=[
                ("Username", dp(30)),
                ("Email", dp(40)),
                ("Phone", dp(30)),
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
        self.table.bind(on_check_press=self.update_selected_users)
        self.ids.table_container.add_widget(self.table)
    
    def show_add_user_dialog(self):
        self.dialog = MDDialog(
            title="Add New User",
            type="custom",
            content_cls=AddUser(size_hint_y=None, height="200dp"),  # Adjust height here
            buttons=[
                MDRaisedButton(text="CANCEL", on_release=lambda x: self.dialog.dismiss()),
                MDRaisedButton(text="ADD", on_release=self.add_user_from_popup),
            ],
        )

        self.dialog.open()

    def add_user_from_popup(self, *args):
        Logger.info(f"ids for root {self.ids}")
        Logger.info(f"ids for root.dialog {self.dialog.ids}")
        Logger.info(f"ids for root.dialog.content_cls {self.dialog.content_cls.ids}")

        dialog_ids = self.dialog.content_cls.ids
        username = dialog_ids.username_input.text.strip()
        email = dialog_ids.email_input.text.strip()

        if username and email:
            self._add_user(username, email)
            self.dialog.dismiss()
            toast(f"User '{username}' added successfully!")
        else:
            toast("Both Username and Email are required.")
    
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
