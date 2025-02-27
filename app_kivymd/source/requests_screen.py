# --- source/requests_screen.py ---
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

from source.constant import (
    ROW_HEIGHT,
)

class AddRequestField(MDBoxLayout):
    pass

class RequestsScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(name="requests", **kwargs)
        self._selected_req_fields = []
        self.table = None
        self.dialog = None
        
        if self.table:
            self.ids.table_container.remove_widget(self.table)
        
        Builder.load_file("widget_schemas/add_request_dialog.kv")  # Load the dialog definition

    def _initialize_table(self):
        self.table = MDDataTable(
            size_hint=(1, 0.8),
            use_pagination=True,
            check=True,
            column_data=[("Key", dp(30)),],
        )
        self.table.bind(on_check_press=self.update_selected_req_fields)
        self.ids.table_container.add_widget(self.table)
    
    def update_selected_req_fields(self, instance, row_data):
        if row_data in self._selected_req_fields:
            self._selected_req_fields.remove(tuple(row_data))
        else:
            self._selected_req_fields.append(row_data)

    def _delete_req_fields(self):
        if len(self._selected_req_fields) < 1:
            return
        
        print(self._selected_req_fields)
        print(self.table.table_data.row_data)
        for selected in self._selected_req_fields:
            self.table.remove_row(selected)
        
        self._selected_req_fields.clear()

    def _add_req_field(self, key):
        self.table.add_row((key, ))

    def show_add_req_field_dialog(self):
        self.dialog = MDDialog(
            title="Add Request Field",
            type="custom",
            content_cls=AddRequestField(size_hint_y=None, height="150dp"),
            buttons=[
                MDRaisedButton(text="CANCEL", on_release=lambda x: self.dialog.dismiss()),
                MDRaisedButton(text="ADD", on_release=self.add_req_field_from_popup),
            ],
        )
        self.dialog.open()

    def add_req_field_from_popup(self, *args):
        dialog_ids = self.dialog.content_cls.ids
        key = dialog_ids.key_input.text.strip()

        if key:
            self._add_req_field(key)
            self.dialog.dismiss()
            toast(f"Request field '{key}' added successfully!")
        else:
            toast("Key is required.")

    def go_to_fields_screen(self):
        self.manager.transition = SlideTransition(direction="left", duration=0.4)
        self.manager.current = "fields"

    def go_to_users_screen(self):
        self.manager.transition = SlideTransition(direction="right", duration=0.4)
        self.manager.current = "users"

    def on_enter(self):
        self._initialize_table()
    
    def on_exit(self):
        self.ids.table_container.remove_widget(self.table)

def get_requests_screen():
    Builder.load_file("widget_schemas/requests.kv")
    return RequestsScreen()