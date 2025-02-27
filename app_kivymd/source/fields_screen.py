# --- source/fields_screen.py ---
from kivy.lang import Builder
from kivymd.uix.screen import MDScreen
from kivymd.uix.button import MDRaisedButton
from kivy.uix.screenmanager import SlideTransition
from kivymd.toast import toast
from kivymd.uix.datatables import MDDataTable
from kivymd.uix.dialog import MDDialog
from kivy.metrics import dp
from kivy.logger import Logger
from kivymd.uix.dialog import MDDialog
from kivymd.uix.menu import MDDropdownMenu

from source.func_utils import (
    load_user_credentials,
    build_email_html_body,
    send_email,
    information_panel
)

from source.constant import (
    FILE_FORMATS,
    MSG_DEFAULT_SEND_FILENAME
)

from source.class_utils import (
    Utils,
    AddField,
    SendEmailDialog
)

class FieldsScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(name="fields", **kwargs)
        self.table = None
        self.dialog = Builder.load_file("widget_schemas/add_field_dialog.kv")  # Load the dialog definition
        self.email_dialog = Builder.load_file("widget_schemas/send_email_dialog.kv")  # Load the dialog definition

    def _delete_fields(self):
        checked_rows = self.table.get_row_checks()

        if not checked_rows:
            return
        
        if len(checked_rows) == 1:
            key = checked_rows[0][0]
            self.manager \
                .data_manager \
                .delete_field(key)
        else:
            keys = self._get_cells_from_checked_rows(cell_as_tuple=True)
            self.manager \
                .data_manager \
                .delete_fields(keys)
        
        self._remove_rows_from_checked_rows()
    
    def _get_cells_from_checked_rows(self, index=0, cell_as_tuple=False):
        rows = self.table.get_row_checks()

        cells = [
            (r[index], ) if cell_as_tuple else r[index] for r in rows
            ]
        print(f"cells - {cells}")
        return cells

    def _remove_rows_from_checked_rows(self):
        rows = self.table.get_row_checks()
        if not rows:
            return
        for row in rows:
            Logger.critical(f"\n self.table - {self.table.row_data}")
            Logger.critical(f"\n row - {row}")
            self.table.remove_row(tuple(row))

    def _add_field(self, key, value, alias_key=""):
        self.manager.data_manager.add_field(key, value, alias_key)
        self.table.add_row((key, value, alias_key))

    def _load_fields_from_db(self):
        #self.ids.table_container.remove_widget(self.table)
        if self.table:
            return
        
        records = self.manager.data_manager.load_fields_from_db()

        self.table = MDDataTable(
            size_hint=(1, 0.8),
            use_pagination=True,
            check=True,
            column_data=[
                ("Key", dp(30)),
                ("Value", dp(30)),
                ("Date", dp(30)),
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

    def show_add_field_dialog(self):
        self.dialog = MDDialog(
            title="Add New Field",
            type="custom",
            content_cls=AddField(size_hint_y=None, height="200dp"),  # Adjust height here
            buttons=[
                MDRaisedButton(text="CANCEL", on_release=lambda _: self.dialog.dismiss()),
                MDRaisedButton(text="ADD", on_release=lambda _: self.add_field_from_popup()),
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
                    MDRaisedButton(text="Cancel", on_release=lambda _: self.email_dialog.dismiss()),
                    MDRaisedButton(text="Send", on_release=lambda _: self.send_email_from_dialog()),
            ],
            )
            #self._init_menu_formats()

        self.email_dialog.open()

    def _init_menu_formats(self):
        menu_items = [
            {
                "text": f"{format}",
                "on_release": lambda x=f"{format}": self.set_file_format(x),
            }
            for format in FILE_FORMATS
        ]
        print(f"self.email_dialog.content_cls - {self.email_dialog.content_cls.ids}")
        self.menu_formats = MDDropdownMenu(
            caller=self.email_dialog.content_cls.ids.file_format_dropdown,
            items=menu_items,
            width_mult=4,
        )

    def set_file_format(self, file_format):
        self.email_dialog.content_cls.ids.file_format_dropdown.text = file_format
        self.menu_formats.dismiss()

    def send_email_from_dialog(self):
        # Get Data
        dialog_ids = self.email_dialog.content_cls.ids
        filename = dialog_ids.filename_input.text.strip()
        file_format = "json" #dialog_ids.file_format_dropdown.text.strip()
        rows_to_send = self.table.get_row_checks()
        print(rows_to_send)
        sender_email, sender_password = load_user_credentials()
        subject = f"Shary message with {len(rows_to_send)} fields"

        # Get file metadata
        if not filename:
            sender_name = sender_email.split("@")[0]
            filename = f"{MSG_DEFAULT_SEND_FILENAME}{sender_name}"
        filename += f".{file_format}"

        if file_format not in FILE_FORMATS:
            information_panel("Action: sending email", "Invalid file format.")
            return
        
        # Get recipients (email)
        recipients = self.manager.get_screen("users").get_checked_emails(index=1)
        if not recipients:
            information_panel("Action: sending email", "Select at least one external user.")
            return
        
        # Build the email instance
        message = build_email_html_body(
            sender_email,
            recipients,
            subject,
            filename,
            file_format,
            rows_to_send,
        )

        # Send the email
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