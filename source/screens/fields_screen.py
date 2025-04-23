# --- source/fields_screen.py ---

from kivy.lang import Builder
from kivy.metrics import dp
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.snackbar import MDSnackbar
from kivymd.uix.dialog import MDDialog
from kivymd.uix.menu import MDDropdownMenu

from core.constant import (
    FILE_FORMATS,
    DEFAULT_ROW_KEY_WIDTH,
    DEFAULT_ROW_VALUE_WIDTH,
    DEFAULT_ROW_REST_WIDTH,
    SCREEN_NAME_FIELDS,
    PATH_SCHEMA_FIELD_DIALOG,
    PATH_SCHEMA_SEND_EMAIL_DIALOG,
    PATH_SCHEMA_SELECT_CHANNEL_DIALOG,
)

from core.enums import StatusDataSentDb

from core.classes import (
    FieldDialog,
    SendEmailDialog,
    SelectChannel,
    EnhancedTableMDScreen
)

from core.functions import information_panel

from services.field_service import FieldService
from services.email_service import EmailService
from services.cloud_service import CloudService
from core.session import Session

class FieldsScreen(EnhancedTableMDScreen):
    def __init__(self, field_service: FieldService, session: Session, email_service: EmailService, cloud_service: CloudService, **kwargs):
        super().__init__(name=SCREEN_NAME_FIELDS, **kwargs)
        self.field_service = field_service
        self.session = session
        self.cloud_service = cloud_service
        self.email_service = email_service
        
        self.field_dialog = Builder.load_file(PATH_SCHEMA_FIELD_DIALOG)  # Load the dialog definition
        self.email_dialog = Builder.load_file(PATH_SCHEMA_SEND_EMAIL_DIALOG)  # Load the dialog definition
        self.select_channel_dialog = Builder.load_file(PATH_SCHEMA_SELECT_CHANNEL_DIALOG)  # Load the dialog definition
        
    def show_field_dialog(self):
        self.field_dialog = MDDialog(
            title="Add New Field",
            type="custom",
            content_cls=FieldDialog(size_hint_y=None, height="200dp"),  # Adjust height here
            buttons=[
                MDRaisedButton(text="CANCEL", on_release=lambda _: self.field_dialog.dismiss()),
                MDRaisedButton(text="ADD", on_release=lambda _: self.add_field_from_popup()),
            ],
        )
        self.field_dialog.open()

    def add_field_from_popup(self, *args):
        key = self._get_field_dialog_key()
        value = self._get_field_dialog_value()

        if key and value:
            self._add_field(key, value)
            self.field_dialog.dismiss()
            MDSnackbar(f"Field '{key}' added successfully!").open()
        else:
            MDSnackbar("Both Key and Value are required.").open()

    def show_select_channel_dialog(self):
        if not self._get_checked_fields():
            MDSnackbar("No field selected.").open()
            return

        if not self.select_channel_dialog:
            self.select_channel_dialog = MDDialog(
                title="Select Channel",
                type="custom",
                content_cls=SelectChannel(),
                buttons=[
                    MDRaisedButton(text="Cancel", on_release=lambda _: self.dismiss_select_channel_dialog()),
                    MDRaisedButton(text="Send", on_release=lambda _: self.process_channel()),
                ]
            )
        self.select_channel_dialog.open()
    
    def dismiss_select_channel_dialog(self):
        if self.select_channel_dialog:
            self.select_channel_dialog.dismiss()

    def show_menu(self, instance):
        menu_items = [
            {
                "viewclass": "OneLineListItem",
                "text": "Cloud",
                "on_release": lambda: self.set_channel_sel_text("Cloud")
            },
            {
                "viewclass": "OneLineListItem",
                "text": "Email",
                "on_release": lambda: self.set_channel_sel_text("Email")
            },
        ]

        self.menu_channel = MDDropdownMenu(
            caller=instance,
            items=menu_items
        )
        self.menu_channel.open()

    def set_channel_sel_text(self, text):
        if hasattr(self, "select_channel_dialog") and self.select_channel_dialog:
            if hasattr(self.select_channel_dialog.content_cls, "ids") and "checked_channel" in self.select_channel_dialog.content_cls.ids:
                self._set_channel_name_from_sel_dialog(text)  # Update label text
            else:
                print("checked_channel not found in select_channel_dialog.content_cls.ids")
        else:
            print("select_channel_dialog is not initialized")

        self.menu_channel.dismiss()  # Close menu

    def process_channel(self):
        channel_name = self._get_channel_sel_dialog_channel_name()
        
        if channel_name == "Email":
            self.show_send_email_dialog()
        elif channel_name == "Cloud":
            # Obtener datos de la tabla
            rows = self._get_checked_fields()
            
            results = self._upload_data_to_cloud(
                rows, 
                self.session.get_email(), 
                self.session.get_checked_users(), 
                False
                )
            self.show_channel_result(results)
        
        if channel_name != "Cloud":
            return
        
    def show_channel_result(self, results):
        if results:
            insertions = [user for user, status in results.items() if status != StatusDataSentDb.STORED]
        else:
            insertions = []
        MDSnackbar(f"Stored {len(insertions)} of {len(results)} data documents").open()

    def show_send_email_dialog(self):
        if not self.field_service:
            MDSnackbar("No field selected.").open()
            return
        
        if not self.email_dialog:
            self.email_dialog = MDDialog(
                title="Send Fields via Email",
                type="custom",
                content_cls=SendEmailDialog(size_hint_y=None, height="200dp"),
                buttons=[
                    MDRaisedButton(text="Cancel", on_release=lambda _: self.dismiss_email_dialog()),
                    MDRaisedButton(text="Send", on_release=lambda _: self.send_email_from_dialog()),
            ],
            )

        self.email_dialog.open()

    def set_file_format_from_dropdown(self, file_format):
        self._set_file_format_from_dropdown(file_format)
        self.menu_formats.dismiss()
    
    def send_email_from_dialog(self):
        filename = self._get_email_dialog_filename()
        fields = self._get_checked_fields(self.main_table, self.checked_rows)
        if not fields or not filename:
            information_panel("Action: sending email", "No requested keys or filename provided")
            return

        # Send email
        self.email_service.send_email_with_fields(
            fields, 
            self.session.get_checked_users(), 
            filename, 
            )

    def dismiss_email_dialog(self):
        if self.email_dialog:
            self.email_dialog.dismiss()

    #  ----- UI entrypoints -----
    # Screen Manager
    def go_to_users_screen(self):
        self.manager.go_to_users_screen("left")

    def go_to_files_visualizer_screen(self):
        self.manager.go_to_files_visualizer_screen("right")

    def go_to_requests_screen(self):
        self.manager.go_to_requests_screen("right")

    def generate_secret_key(self):
        new_secret_key = self.manager.cryptographer.generate_nonce()
        self.select_channel_dialog.content_cls.ids.secret_key.hint_text = "secret_key"
        self.select_channel_dialog.content_cls.ids.secret_key.text = new_secret_key  # Optional: clear previous input
        self.cloud_service.set_secret_key(new_secret_key)

    def toggle_password_visibility(self):
        field = self.select_channel_dialog.content_cls.ids.secret_key
        field.password = not field.password
        field.icon_right = "eye" if not field.password else "eye-off"
    
    def _upload_data_to_cloud(self, data_rows: list, email: str, users: list, on_request=False):
        self.cloud_service.upload_data(data_rows, email, users, on_request)

    def on_enter(self):
        self._load_fields_table_from_db()
        
    # ----- Internal methods -----
    def _get_checked_fields(self) -> list[str]:
        return self._get_checked_rows()
    
    def _get_field_dialog_value(self):
        field_dialog_ids = self.field_dialog.content_cls.ids
        return field_dialog_ids.value_input.text.strip()

    def _get_field_dialog_key(self):
        field_dialog_ids = self.field_dialog.content_cls.ids
        return field_dialog_ids.key_input.text.strip()

    def _get_email_dialog_filename(self):
        email_dialog_ids = self.email_dialog.content_cls.ids
        return email_dialog_ids.filename_input.text.strip()
    
    def _get_channel_sel_dialog_channel_name(self):
        channel_sel_dialog_ids = self.select_channel_dialog.content_cls.ids
        return channel_sel_dialog_ids.checked_channel.text.strip()

    def _set_channel_name_from_sel_dialog(self, channel_name):
        self.select_channel_dialog.content_cls.ids.checked_channel.text = channel_name

    def _set_file_format_from_dropdown(self, file_format):
        self.email_dialog.content_cls.ids.file_format_dropdown.text = file_format

    def _delete_fields(self):
        keys = self._delete_rows()
        
        if not keys:
            MDSnackbar(f"No keys selected.").open()
            return
        
        self.field_service.delete_fields(keys)
    
    #def _get_checked_keys(self):
    #    return self._get_cells_from_checked_rows(0, True)

    def _add_field(self, key, value, alias_key=""):
        self.field_service.create_field(key, value, alias_key)
        self._add_row((key, value, "now"))

    def _load_fields_table_from_db(self):
        column_data = [
            ("Key", dp(DEFAULT_ROW_KEY_WIDTH)),
            ("Value", dp(DEFAULT_ROW_VALUE_WIDTH)),  # Wider column
            ("Date", dp(DEFAULT_ROW_REST_WIDTH)),
            ]
        
        fields_data = self.field_service.get_all_fields()
        self._initialize_table(column_data, fields_data)

    def _init_menu_formats(self):
        menu_items = [
            {
                "text": f"{format}",
                "on_release": lambda x=f"{format}": self.set_file_format_from_dropdown(x),
            }
            for format in FILE_FORMATS
        ]
        print(f"self.email_dialog.content_cls - {self.email_dialog.content_cls.ids}")
        self.menu_formats = MDDropdownMenu(
            caller=self.email_dialog.content_cls.ids.file_format_dropdown,
            items=menu_items,
            width_mult=4,
        )