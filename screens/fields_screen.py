# --- source/fields_screen.py ---

from kivy.lang import Builder
from kivy.logger import Logger
from kivy.metrics import dp
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.snackbar import MDSnackbar
from kivymd.uix.datatables import MDDataTable
from kivymd.uix.dialog import MDDialog
from kivymd.uix.menu import MDDropdownMenu

from core.functions import (
    get_checked_rows,
)

from core.constant import (
    FILE_FORMATS,
    DEFAULT_ROW_KEY_WIDTH,
    DEFAULT_ROW_VALUE_WIDTH,
    DEFAULT_ROW_REST_WIDTH,
    DEFAULT_NUM_ROWS_PAGE,
    DEFAULT_USE_PAGINATION,
    SCREEN_NAME_FIELDS,
    PATH_SCHEMA_FIELD_DIALOG,
    PATH_SCHEMA_SEND_EMAIL_DIALOG,
    PATH_SCHEMA_CHANNEL_CONTENT_DIALOG,
)

from core.enums import StatusDataSentDb

from core.classes import (
    FieldDialog,
    SendEmailDialog,
    SelectChannel,
    EnhancedMDScreen
)

from core.dtos import FieldDTO
from repositories.field_repository import FieldRepository
from controller.app_controller import AppController
from core.session import CurrentSession

class FieldsScreen(EnhancedMDScreen):
    def __init__(self, controller: AppController, db_connection=None, **kwargs):
        super().__init__(name=SCREEN_NAME_FIELDS, **kwargs)
        self.controller = controller
        self.field_repo = FieldRepository(db_connection)
        self.session: CurrentSession = CurrentSession.get_instance()
        
        self.field_dialog = Builder.load_file(PATH_SCHEMA_FIELD_DIALOG)  # Load the dialog definition
        self.email_dialog = Builder.load_file(PATH_SCHEMA_SEND_EMAIL_DIALOG)  # Load the dialog definition
        self.channel_selection_dialog = Builder.load_file(PATH_SCHEMA_CHANNEL_CONTENT_DIALOG)  # Load the dialog definition
        
        self.main_table = None
        
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
        if hasattr(self, "channel_selection_dialog") and self.channel_selection_dialog:
            if hasattr(self.channel_selection_dialog.content_cls, "ids") and "selected_channel" in self.channel_selection_dialog.content_cls.ids:
                self._set_channel_name_from_sel_dialog(text)  # Update label text
            else:
                print("selected_channel not found in channel_selection_dialog.content_cls.ids")
        else:
            print("channel_selection_dialog is not initialized")

        self.menu_channel.dismiss()  # Close menu

    def process_channel(self):
        channel_name = self._get_channel_sel_dialog_channel_name()
        
        if channel_name == "Email":
            self.show_send_email_dialog()
        elif channel_name == "Cloud":
            # Obtener datos de la tabla
            rows = get_checked_rows(self.main_table, self.checked_rows)
            # Obtener consumers desde la pantalla de usuarios
            consumers = self.session.get_users_selected()
            results = self.controller.send_data_to_cloud(
                rows, 
                self.session.email, 
                consumers, 
                False)
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
            #self._init_menu_formats()

        self.email_dialog.open()

    def set_file_format_from_dropdown(self, file_format):
        self._set_file_format_from_dropdown(file_format)
        self.menu_formats.dismiss()
    
    def send_email_from_dialog(self):
        filename = self._get_email_dialog_filename()
        file_format = "json"
        rows = get_checked_rows(self.main_table, self.checked_rows)
        consumers = self.session.get_users_selected()
        
        self.controller.send_email_with_fields(rows, consumers, filename, file_format)

    def dismiss_email_dialog(self):
        if self.email_dialog:
            self.email_dialog.dismiss()

    # ----- Internal methods -----
    def _get_field_dialog_value(self):
        field_dialog_ids = self.field_dialog.content_cls.ids
        return field_dialog_ids.value_input.text.strip()

    def _get_field_dialog_key(self):
        field_dialog_ids = self.email_dialog.content_cls.ids
        return field_dialog_ids.key_input.text.strip()

    def _get_email_dialog_filename(self):
        email_dialog_ids = self.field_dialog.content_cls.ids
        return email_dialog_ids.filename_input.text.strip()
    
    def _get_channel_sel_dialog_channel_name(self):
        channel_sel_dialog_ids = self.channel_selection_dialog.content_cls.ids
        return channel_sel_dialog_ids.selected_channel.text.strip()

    def _set_channel_name_from_sel_dialog(self, channel_name):
        self.channel_selection_dialog.content_cls.ids.selected_channel.text = channel_name

    def _set_file_format_from_dropdown(self, file_format):
        self.email_dialog.content_cls.ids.file_format_dropdown.text = file_format

    def _delete_fields(self):
        checked_rows = get_checked_rows(self.main_table, self.checked_rows)

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
        rows = get_checked_rows(self.main_table, self.checked_rows)

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

    #  ----- UI entrypoints -----
    # Screen Manager
    def go_to_users_screen(self):
        self.manager.go_to_users_screen("left")

    def go_to_files_visualizer_screen(self):
        self.manager.go_to_files_visualizer_screen("right")

    def generate_secret_key(self):
        new_secret_key = self.manager.cryptographer.generate_nonce()
        self.channel_selection_dialog.content_cls.ids.secret_key.hint_text = "secret_key"
        self.channel_selection_dialog.content_cls.ids.secret_key.text = new_secret_key  # Optional: clear previous input
        self.manager.cloud_service.set_secret_key(new_secret_key)

    def toggle_password_visibility(self):
        field = self.channel_selection_dialog.content_cls.ids.secret_key
        field.password = not field.password
        field.icon_right = "eye" if not field.password else "eye-off"
    
    def _send_data_to_cloud(self, data_rows, consumers, on_request=False):
        self.manager.send_data_to_cloud(data_rows, consumers, on_request)

    def on_enter(self):
        self._load_fields_from_db()
        