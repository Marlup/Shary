# --- source/fields_screen.py ---
from kivy.lang import Builder
from kivymd.uix.screen import MDScreen
from kivymd.uix.button import MDRaisedButton
from kivy.uix.screenmanager import SlideTransition
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.toast import toast
from kivymd.uix.datatables import MDDataTable
from kivymd.uix.dialog import MDDialog
from kivy.metrics import dp
from kivy.logger import Logger
from kivymd.uix.dialog import MDDialog
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.boxlayout import MDBoxLayout

from source.func_utils import (
    load_user_credentials,
    build_email_html_body,
    send_email,
    information_panel
)

from source.query_schemas import (
    SELECT_ALL_FIELDS,
    DELETE_FIELD_BY_KEY,
    INSERT_FIELD,
    
)
from source.constant import (
    ROW_HEIGHT,
    FILE_FORMATS,
    MSG_DEFAULT_SEND_FILENAME
)

from source.class_utils import (
    EmailHandler,
)

class AddField(MDBoxLayout):
    pass

class SendEmailDialog(MDBoxLayout):
    pass

class FieldsScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(name="fields", **kwargs)
        self._selected_fields = []
        self.table = None
        self.dialog = Builder.load_file("widget_schemas/add_field_dialog.kv")  # Load the dialog definition
        self.email_dialog = Builder.load_file("widget_schemas/add_field_dialog.kv")  # Load the dialog definition

    def update_selected_fields(self, instance, row_data):
        if row_data in self._selected_fields:
            self._selected_fields.remove(row_data)
        else:
            self._selected_fields.append(row_data)

    def _delete_fields(self):
        if not self._selected_fields:
            return
        
        if len(self._selected_fields) == 1:
            self.manager \
                .data_manager \
                .delete_field(self._selected_fields)
        else:
            self.manager \
                .data_manager \
                .delete_fields(self._selected_fields)
        self._load_users_from_db()

    def _add_field(self, key, value):
        self.manager.data_manager.add_field(key, value)
        self._load_fields_from_db()

    def _load_fields_from_db(self):
        records = self.manager.data_manager.load_fields_from_db()

        if self.table:
            self.ids.table_container.remove_widget(self.table)

        self.table = MDDataTable(
            size_hint=(1, 0.8),
            use_pagination=True,
            check=True,
            column_data=[
                ("Key", dp(30)),
                ("Value", dp(30)),
                ("Date", dp(30)),
                ("Actions", dp(20)),
            ],
            row_data=[
                (
                    record[0],
                    record[1],
                    record[2],
                    "X"  # Unicode for a cross symbol (X) for delete
                )
                for record in records
            ],
        )
        self.table.bind(on_check_press=self.update_selected_fields)
        self.ids.table_container.add_widget(self.table)

    def show_add_field_dialog(self):
        self.dialog = MDDialog(
            title="Add New Field",
            type="custom",
            content_cls=AddField(size_hint_y=None, height="200dp"),  # Adjust height here
            buttons=[
                MDRaisedButton(text="CANCEL", on_release=lambda x: self.dialog.dismiss()),
                MDRaisedButton(text="ADD", on_release=self.add_field_from_popup),
            ],
        )
        self.dialog.open()

    def add_field_from_popup(self, *args):
        dialog_ids = self.dialog.content_cls.ids
        key = dialog_ids.key_input.text.strip()
        value = dialog_ids.value_input.text.strip()

        if key and value:
            self._add_field(key, value)
            self.dialog.dismiss()
            toast(f"Field '{key}' added successfully!")
        else:
            toast("Both Key and Value are required.")

    def show_send_email_dialog(self):
        if not self.email_dialog:
            self.email_dialog = MDDialog(
                title="Send Fields via Email",
                type="custom",
                content_cls=SendEmailDialog(size_hint_y=None, height="200dp"),
                buttons=[
                    MDRaisedButton(text="Cancel", on_release=lambda x: self.email_dialog.dismiss()),
                    MDRaisedButton(text="Send", on_release=self.send_email_from_dialog),
            ],
            )
            self._init_dropdown_menu()

        self.email_dialog.open()

    def _init_dropdown_menu(self):
        menu_items = [
            {
                "text": f"{format}",
                "on_release": lambda x=f"{format}": self.set_file_format(x),
            }
            for format in FILE_FORMATS
        ]
        print(f"self.email_dialog.content_cls - {self.email_dialog.content_cls.ids}")
        self.dropdown_menu = MDDropdownMenu(
            caller=self.email_dialog.content_cls.ids.file_format_dropdown,
            items=menu_items,
            width_mult=4,
        )

    def set_file_format(self, file_format):
        self.email_dialog.content_cls.ids.file_format_dropdown.text = file_format
        self.dropdown_menu.dismiss()

    def send_email_from_dialog(self):
        dialog_ids = self.email_dialog.content_cls.ids
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
        self.email_dialog.dismiss()

    def dismiss_email_dialog(self):
        if self.email_dialog:
            self.email_dialog.dismiss()

# -------- callbacks --------
    def go_to_users_screen(self):
        self.manager.transition = SlideTransition(direction="left", duration=0.4)
        self.manager.current = "users"

    def on_enter(self):
        self._load_fields_from_db()

def get_fields_screen():
    Builder.load_file("widget_schemas/fields.kv")
    return FieldsScreen()