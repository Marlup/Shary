# --- source/requests_screen.py ---
from kivy.lang import Builder
from kivymd.uix.screen import MDScreen
from kivymd.uix.button import MDRaisedButton
from kivymd.toast import toast
from kivymd.uix.datatables import MDDataTable
from kivymd.uix.dialog import MDDialog
from kivy.uix.screenmanager import SlideTransition
from kivy.metrics import dp
from kivy.logger import Logger

from source.constant import (
    MSG_DEFAULT_REQUEST_FILENAME,
    FILE_FORMATS
)

from source.class_utils import (
    AddRequestField,
    SendEmailDialog
)

from source.func_utils import (
    information_panel,
    load_user_credentials,
    build_email_html_body,
    send_email
)

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
        if self.table:
            return
        
        self.table = MDDataTable(
            size_hint=(1, 0.8),
            use_pagination=True,
            check=True,
            column_data=[
                ("Key", dp(30)),
                ("Other Names", dp(30)),
                ],
            row_data=[]
        )
        self.ids.table_container.add_widget(self.table)
    
    def _delete_req_fields(self):
        checked_rows = self.table.get_row_checks()

        if not checked_rows:
            return
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

    def _add_req_field(self, key, other_name):
        print(self._selected_req_fields)
        print(self.table.table_data.row_data)
        self.table.add_row((key, other_name))

    def show_add_req_field_dialog(self):
        self.dialog = MDDialog(
            title="Add Request Field",
            type="custom",
            content_cls=AddRequestField(size_hint_y=None, height="150dp"),
            buttons=[
                MDRaisedButton(text="CANCEL", on_release=lambda x: self.dialog.dismiss()),
                MDRaisedButton(text="ADD", on_release=lambda x: self.add_req_field_from_popup()),
            ],
        )
        self.dialog.open()

    def add_req_field_from_popup(self, *args):
        dialog_ids = self.dialog.content_cls.ids
        key = dialog_ids.key_input.text.strip()
        other_name = dialog_ids.other_name_input.text.strip()

        if key:
            self._add_req_field(key, other_name)
            self.dialog.dismiss()
            toast(f"Request field '{key}' added successfully!")
        else:
            toast("Key is required.")

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
        dialog_ids = self.email_dialog.content_cls.ids
        filename = dialog_ids.filename_input.text.strip()
        file_format = "json_req"

        if not filename:
            sender_email, _ = load_user_credentials()
            sender_name = sender_email.split("@")[0]
            filename = f"{MSG_DEFAULT_REQUEST_FILENAME}{sender_name}"
        filename += f".{file_format}"

        if file_format not in FILE_FORMATS:
            information_panel("Action: sending email", "Invalid file format.")
            return
        
        recipients = self.manager.get_screen("users").get_checked_emails(index=1)
        if not recipients:
            information_panel("Action: sending email", "Select at least one external user to send to.")
            return

        sender_email, sender_password = load_user_credentials()
        subject = f"Shary message with {len(self.table.get_row_checks())} fields"
        message = build_email_html_body(
            sender_email,
            recipients,
            subject,
            filename,
            file_format,
            self.table.get_row_checks(),
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

    def go_to_fields_screen(self):
        self.manager.transition = SlideTransition(direction="left", duration=0.4)
        self.manager.current = "fields"

    def go_to_users_screen(self):
        self.manager.transition = SlideTransition(direction="right", duration=0.4)
        self.manager.current = "users"

    def on_enter(self):
        self._initialize_table()

def get_requests_screen():
    Builder.load_file("widget_schemas/requests.kv")
    return RequestsScreen()