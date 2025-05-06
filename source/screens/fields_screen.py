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
        
    def open_add_dialog(self):
        self.field_dialog = MDDialog(
            title="Add New Field",
            type="custom",
            content_cls=FieldDialog(size_hint_y=None, height="200dp"),  # Adjust height here
            buttons=[
                MDRaisedButton(text="CANCEL", on_release=lambda _: self.field_dialog.dismiss()),
                MDRaisedButton(text="ADD", on_release=lambda _: self.validate_add_field()),
            ],
        )
        self.field_dialog.open()

    def validate_add_field(self, *args):
        key = self._get_ui_new_key()
        value = self._get_ui_new_value()

        if key and value:
            alias_key = key or self._get_ui_new_alias_key()

            self._add_field(key, value, alias_key)
            self.field_dialog.dismiss()
            MDSnackbar(f"Field '{key}' added successfully!").open()
        else:
            MDSnackbar("Both Key and Value are required.").open()

    def open_channel_dialog(self):
        if not self._get_checked_fields():
            MDSnackbar("No field selected.").open()
            return

        if not self.select_channel_dialog:
            self.select_channel_dialog = MDDialog(
                title="Select Channel",
                type="custom",
                content_cls=SelectChannel(),
                buttons=[
                    MDRaisedButton(text="Cancel", on_release=lambda _: self.close_channel_dialog()),
                    MDRaisedButton(text="Send", on_release=lambda _: self.process_channel()),
                ]
            )
        self.select_channel_dialog.open()
    
    def close_channel_dialog(self):
        if self.select_channel_dialog:
            self.select_channel_dialog.dismiss()

    def show_menu(self, instance):
        menu_items = [
            {
                "viewclass": "OneLineListItem",
                "text": "Cloud",
                "on_release": lambda: self.set_ui_channel_text("Cloud")
            },
            {
                "viewclass": "OneLineListItem",
                "text": "Email",
                "on_release": lambda: self.set_ui_channel_text("Email")
            },
        ]

        self.menu_channel = MDDropdownMenu(
            caller=instance,
            items=menu_items
        )
        self.menu_channel.open()

    def set_ui_channel_text(self, text):
        if hasattr(self, "select_channel_dialog") and self.select_channel_dialog:
            if hasattr(self.select_channel_dialog.content_cls, "ids") and "checked_channel" in self.select_channel_dialog.content_cls.ids:
                self._set_ui_channel_name(text)  # Update label text
            else:
                print("checked_channel not found in select_channel_dialog.content_cls.ids")
        else:
            print("select_channel_dialog is not initialized")

        self.menu_channel.dismiss()  # Close menu

    def process_channel(self):
        channel_name = self._get_ui_channel()
        
        if channel_name == "Email":
            self.open_email_dialog()
        elif channel_name == "Cloud":
            # Obtener datos de la tabla
            rows = self._get_checked_fields()
            
            results = self._upload_data(
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
            MDSnackbar(f"Stored {len(insertions)} of {len(results)} data documents").open()
        else:
            insertions = []

    def open_email_dialog(self):
        if not self.field_service:
            MDSnackbar("No field selected.").open()
            return
        
        if not self.email_dialog:
            self.email_dialog = MDDialog(
                title="Send Fields via Email",
                type="custom",
                content_cls=SendEmailDialog(size_hint_y=None, height="200dp"),
                buttons=[
                    MDRaisedButton(text="Cancel", on_release=lambda _: self.close_email_dialog()),
                    MDRaisedButton(text="Send", on_release=lambda _: self.call_email_service()),
            ],
            )

        self.email_dialog.open()

    def set_file_format_from_dropdown(self, file_format):
        self._set_file_format_from_dropdown(file_format)
        self.menu_formats.dismiss()
    
    def call_email_service(self):
        filename = self._get_ui_email_filename()
        fields = self._get_checked_fields()
        if not fields or not filename:
            information_panel("Action: sending email", "No requested keys or filename provided")
            return

        # Send email
        self.email_service.send_email_with_fields(
            fields, 
            self.session.get_checked_users(), 
            filename, 
            )

    def close_email_dialog(self):
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

    def toggle_password_visibility(self):
        field = self.select_channel_dialog.content_cls.ids.secret_key
        field.password = not field.password
        field.icon_right = "eye" if not field.password else "eye-off"
    
    def _upload_data(self, data_rows: list, email: str, users: list, on_request=False):
        self.cloud_service.upload_data(data_rows, email, users, on_request)

    def on_enter(self):
        self._load_table_from_db()
        
    # ----- Internal methods -----
    def _get_checked_fields(self) -> list[str]:
        return self._get_checked_rows()
    
    def _get_ui_new_key(self):
        field_dialog_ids = self.field_dialog.content_cls.ids
        return field_dialog_ids.key_input.text.strip()

    def _get_ui_new_value(self):
        field_dialog_ids = self.field_dialog.content_cls.ids
        return field_dialog_ids.value_input.text.strip()

    def _get_ui_new_alias_key(self):
        field_dialog_ids = self.field_dialog.content_cls.ids
        return field_dialog_ids.alias_key_input.text.strip()

    def _get_ui_email_filename(self):
        email_dialog_ids = self.email_dialog.content_cls.ids
        return email_dialog_ids.filename_input.text.strip()
    
    def _get_ui_channel(self):
        channel_sel_dialog_ids = self.select_channel_dialog.content_cls.ids
        return channel_sel_dialog_ids.checked_channel.text.strip()

    def _set_ui_channel_name(self, channel_name):
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
        self._add_row((key, value, alias_key, "today"))

    def _load_table_from_db(self):
        column_data = [
            ("Key", dp(DEFAULT_ROW_KEY_WIDTH)),
            ("Value", dp(DEFAULT_ROW_VALUE_WIDTH)), 
            ("Alias", dp(DEFAULT_ROW_VALUE_WIDTH)), 
            ("Date", dp(DEFAULT_ROW_REST_WIDTH)),
            ]
        
        fields_data = self.field_service.get_all_fields()
        self._initialize_table(column_data, fields_data)

    def _initialize_ui_file_formats(self):
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