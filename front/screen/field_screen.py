# --- source/fields_screen.py ---
from kivy.lang import Builder
from kivy.logger import Logger
from kivy.metrics import dp
from kivy.uix.screenmanager import SlideTransition
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.snackbar import MDSnackbar
from kivymd.uix.datatables import MDDataTable
from kivymd.uix.dialog import MDDialog
from kivymd.uix.menu import MDDropdownMenu

from front.core.func_utils import (
    get_safe_row_checks,
)

from front.core.constant import (
    FILE_FORMATS,
    DEFAULT_ROW_KEY_WIDTH,
    DEFAULT_ROW_VALUE_WIDTH,
    DEFAULT_ROW_REST_WIDTH,
    DEFAULT_NUM_ROWS_PAGE,
    DEFAULT_USE_PAGINATION,
    SCREEN_NAME_FIELD,
    SCREEN_NAME_USER,
    SCREEN_NAME_FILE_VISUALIZER,
    PATH_SCHEMA_FIELD_DIALOG,
    PATH_SCHEMA_SEND_EMAIL_DIALOG,
    PATH_SCHEMA_CHANNEL_CONTENT_DIALOG,
)

from front.core.class_utils import (
    AddField,
    SendEmailDialog,
    SelectChannel,
    EnhancedMDScreen
)

from front.core.dtos import FieldDTO
from front.repository.field_repository import FieldRepository

class FieldScreen(EnhancedMDScreen):
    def __init__(self, db_connection=None, **kwargs):
        super().__init__(name=SCREEN_NAME_FIELD, **kwargs)
        self.field_repo = FieldRepository(db_connection)
        
        self.dialog_add_field = Builder.load_file(PATH_SCHEMA_FIELD_DIALOG)  # Load the dialog definition
        self.email_dialog = Builder.load_file(PATH_SCHEMA_SEND_EMAIL_DIALOG)  # Load the dialog definition
        self.channel_selection_dialog = Builder.load_file(PATH_SCHEMA_CHANNEL_CONTENT_DIALOG)  # Load the dialog definition
        
        self.main_table = None

    def _delete_fields(self):
        checked_rows = get_safe_row_checks(self.main_table, self.checked_rows)

        if not checked_rows:
            return
        
        if len(checked_rows) == 1:
            key = checked_rows[0][0]
            self.field_repo.delete_fields(key)
        else:
            keys = self._get_cells_from_checked_rows(cell_as_tuple=True)
            self.field_repo.delete_fields(keys)
        
        self._remove_rows_from_checked_rows()
    
    def _get_cells_from_checked_rows(self, index=0, cell_as_tuple=False):
        rows = get_safe_row_checks(self.main_table, self.checked_rows)

        cells = [
            (r[index], ) if cell_as_tuple else r[index] for r in rows
            ]
        return cells

    def _remove_rows_from_checked_rows(self):
        rows = get_safe_row_checks(self.main_table, self.checked_rows)

        if not rows:
            return
        for row in rows:
            Logger.critical(f"\n self.main_table - {self.main_table.row_data}")
            Logger.critical(f"\n row - {row}")
            self.main_table.remove_row(tuple(row))
            self.checked_rows.remove(row)

    def _add_field(self, key, value, alias_key=""):
        field = FieldDTO(key=key, value=value, alias_key=alias_key)
        self.field_repo.add_field(field)
        self.main_table.add_row((field.key, field.value, "now"))

    def _load_fields_from_db(self):
        if self.main_table:
            return
        
        records = self.field_repo.load_fields_from_db()

        self.main_table = MDDataTable(
            size_hint=(1, 0.8),  # Full size inside the box layout
            pos_hint={"center_x": 0.5, "center_y": 0.5},  # Ensure centering
            check=True,  # Enable row selection
            column_data=[
                ("Key", dp(DEFAULT_ROW_KEY_WIDTH)),
                ("Value", dp(DEFAULT_ROW_VALUE_WIDTH)),  # Wider column
                ("Date", dp(DEFAULT_ROW_REST_WIDTH)),
            ],
            row_data=[(r.key, r.value, r.date_added) for r in records],
            use_pagination=DEFAULT_USE_PAGINATION,
            rows_num=DEFAULT_NUM_ROWS_PAGE,
            pagination_menu_height=dp(300),  # Set dropdown menu height
        )
        
        # Bind checkbox selection event
        self.main_table.bind(on_check_press=self.on_row_check)
        #scroll = ScrollView(size_hint=(1, 1))
        #scroll.add_widget(self.main_table)
        self.ids.table_container.add_widget(self.main_table)
        
    def show_add_field_dialog(self):
        self.dialog_add_field = MDDialog(
            title="Add New Field",
            type="custom",
            content_cls=AddField(size_hint_y=None, height="200dp"),  # Adjust height here
            buttons=[
                MDRaisedButton(text="CANCEL", on_release=lambda _: self.dialog_add_field.dismiss()),
                MDRaisedButton(text="ADD", on_release=lambda _: self.add_field_from_popup()),
            ],
        )
        self.dialog_add_field.open()

    def add_field_from_popup(self, *args):
        dialog_ids = self.dialog_add_field.content_cls.ids
        key = dialog_ids.key_input.text.strip()
        value = dialog_ids.value_input.text.strip()

        if key and value:
            self._add_field(key, value)
            self.dialog_add_field.dismiss()
            MDSnackbar(f"Field '{key}' added successfully!").open()
        else:
            MDSnackbar("Both Key and Value are required.").open()

    def show_channel_selection_dialog(self):
        if not self.channel_selection_dialog:
            self.channel_selection_dialog = MDDialog(
                title="Select Channel",
                type="custom",
                content_cls=SelectChannel(),
                buttons=[
                    MDRaisedButton(text="Cancel", on_release=lambda _: self.dismiss_channel_selection_dialog()),
                    MDRaisedButton(text="Send", on_release=lambda _: self.process_channel()),
                ]
            )
        self.channel_selection_dialog.open()
    
    def dismiss_channel_selection_dialog(self):
        if self.channel_selection_dialog:
            self.channel_selection_dialog.dismiss()

    def toggle_password_visibility(self):
        field = self.channel_selection_dialog.content_cls.ids.secret_key
        field.password = not field.password
        field.icon_right = "eye" if not field.password else "eye-off"

    def generate_secret_key(self):
        from random import choices
        import string
        key = ''.join(choices(string.ascii_letters + string.digits, k=16))
        self.channel_selection_dialog.content_cls.ids.secret_key.text = key

    def show_menu(self, instance):
        menu_items = [
            {
                "viewclass": "OneLineListItem",
                "text": "Cloud",
                "on_release": lambda: self.set_text("Cloud")
            },
            {
                "viewclass": "OneLineListItem",
                "text": "Email",
                "on_release": lambda: self.set_text("Email")
            },
        ]

        self.menu_channel = MDDropdownMenu(
            caller=instance,
            items=menu_items,
            width_mult=3
        )
        self.menu_channel.open()

    def set_text(self, text):
        if hasattr(self, "channel_selection_dialog") and self.channel_selection_dialog:
            if hasattr(self.channel_selection_dialog.content_cls, "ids") and "selected_channel" in self.channel_selection_dialog.content_cls.ids:
                self.channel_selection_dialog.content_cls.ids.selected_channel.text = text  # Update label text
            else:
                print("selected_channel not found in channel_selection_dialog.content_cls.ids")
        else:
            print("channel_selection_dialog is not initialized")

        self.menu_channel.dismiss()  # Close menu

    def process_channel(self):
        channel = self.channel_selection_dialog \
                      .content_cls \
                      .ids \
                      .selected_channel \
                      .text
        
        if channel == "Email":
            self.show_send_email_dialog()
        elif channel == "Cloud":
            self.manager.cloud_service.send_data(
                rows, sender, recipients, on_request=False
            )
    
    def show_send_email_dialog(self):
        if not self.email_dialog:
            self.email_dialog = MDDialog(
                title="Send Fields via Email",
                type="custom",
                content_cls=SendEmailDialog(size_hint_y=None, height="200dp"),
                buttons=[
                    MDRaisedButton(text="Cancel", on_release=lambda _: self.dismiss_email_dialog()),
                    MDRaisedButton(text="Send", on_release=lambda _: self.prepare_email()),
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
    
    def prepare_email(self):
        dialog_ids = self.email_dialog.content_cls.ids

        filename = dialog_ids.filename_input.text.strip()
        file_format = "json"
        rows = get_safe_row_checks(self.main_table, self.checked_rows)
        users = self.get_selected_users()

        payload = self.manager.email_service.create_payload(rows, users, filename, file_format)

        if payload:
            self.manager.email_service.send_from_payload(payload)

    def dismiss_email_dialog(self):
        if self.email_dialog:
            self.email_dialog.dismiss()

# -------- callbacks --------
    def go_to_users_screen(self):
        self.manager.transition = SlideTransition(direction="left", duration=0.4)
        self.manager.current = SCREEN_NAME_USER

    def go_to_field_visualizer_screen(self):
        self.manager.transition = SlideTransition(direction="right", duration=0.4)
        self.manager.current = SCREEN_NAME_FILE_VISUALIZER

    def generate_secret_key(self):
        secret_key = self.manager.cryptographer.generate_nonce()
        self.channel_selection_dialog.content_cls.ids.secret_key.hint_text = "secret_key"
        self.channel_selection_dialog.content_cls.ids.secret_key.text = secret_key  # Optional: clear previous input
    
    def toggle_password_visibility(self):
        field = self.channel_selection_dialog.content_cls.ids.secret_key
        field.password = not field.password
        field.icon_right = "eye" if not field.password else "eye-off"
    
    def get_selected_users(self):
        return self.manager.get_screen(SCREEN_NAME_USER).get_checked_emails(index=1)

    def on_enter(self):
        self._load_fields_from_db()
        