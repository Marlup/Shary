# --- source/requests_screen.py ---
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.logger import Logger
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.snackbar import MDSnackbar
from kivymd.uix.datatables import MDDataTable
from kivymd.uix.dialog import MDDialog

from core.classes import (
    RequestFieldDialog,
    SendEmailDialog,
    EnhancedMDScreen
)

from core.functions import (
    information_panel,
    get_checked_rows
)

from controller.app_controller import AppController
from core.session import CurrentSession

from core.constant import (
    DEFAULT_ROW_KEY_WIDTH,
    DEFAULT_ROW_VALUE_WIDTH,
    DEFAULT_USE_PAGINATION,
    DEFAULT_NUM_ROWS_PAGE,
    SCREEN_NAME_REQUESTS,
    PATH_SCHEMA_REQUEST_DIALOG
)

class RequestsScreen(EnhancedMDScreen):
    def __init__(self, controller: AppController, **kwargs):
        super().__init__(name=SCREEN_NAME_REQUESTS, **kwargs)
        self.controller = controller
        self.session: CurrentSession = CurrentSession.get_instance()

        # Load the request dialog definition
        Builder.load_file(PATH_SCHEMA_REQUEST_DIALOG)
        
        # Data
        self._selected_req_fields = []
        
        # Dialog widgets
        self.req_field_dialog = None
        self.email_dialog = None
        
        # Table widgets
        self.main_table = None
        if self.main_table:
            self.ids.table_container.remove_widget(self.main_table)

    def show_req_field_dialog(self):
        self.req_field_dialog = MDDialog(
            title="Add Request Field",
            type="custom",
            content_cls=RequestFieldDialog(size_hint_y=None, height="150dp"),
            buttons=[
                MDRaisedButton(text="CANCEL", on_release=lambda _: self.req_field_dialog.dismiss()),
                MDRaisedButton(text="ADD", on_release=lambda _: self.add_req_field_from_popup()),
            ],
        )
        self.req_field_dialog.open()

    def add_req_field_from_popup(self, *args):
        key = self._get_req_field_dialog_key()
        other_name = self._get_req_field_dialog_other_name()

        if key:
            self._add_req_field(key, other_name)
            self.req_field_dialog.dismiss()
            MDSnackbar(f"Request field '{key}' added successfully!").show()
        else:
            MDSnackbar("Key is required.").show()

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
        filename = self._get_email_dialog_filename()

        # Enviar el email usando el payload completo
        file_format = "json"
        # Obtener datos de la tabla
        rows = get_checked_rows(self.main_table, self.checked_rows)
        # Obtener destinatarios desde la pantalla de usuarios
        consumers = self.session.get_users_selected()
        self.controller.send_email_with_fields(rows, consumers, filename, file_format)

        # Feedback visual y cerrar diálogo
        information_panel("Action: sending email", "Email sent successfully")
        self.email_dialog.dismiss()

    def dismiss_email_dialog(self):
        if self.email_dialog:
            self.email_dialog.dismiss()

    def go_to_fields_screen(self):
        self.manager.go_to_fields_screen("left")

    def go_to_users_screen(self):
        self.manager.go_to_users_screen("right")
    
    def _get_checked_users(self):
        return self.manager.get_checked_users()

    def on_enter(self):
        self._load_users_from_db()

# ----- Internal methods -----
    def _get_email_dialog_filename(self):
        email_dialog_ids = self.email_dialog.content_cls.ids
        return email_dialog_ids.filename_input.text.strip()

    def _get_req_field_dialog_key(self):
        field_dialog_ids = self.req_field_dialog.content_cls.ids
        return field_dialog_ids.key_input.text.strip()

    def _get_req_field_dialog_other_name(self):
        field_dialog_ids = self.req_field_dialog.content_cls.ids
        return field_dialog_ids.other_name_input.text.strip()

    def _load_users_from_db(self):
        if self.main_table:
            return
        
        self.main_table = MDDataTable(
            size_hint=(1, 0.8),
            pos_hint={"center_x": 0.5, "center_y": 0.5},  # Ensure centering
            check=True,
            column_data=[
                ("Key", dp(DEFAULT_ROW_KEY_WIDTH)),
                ("Other Names", dp(DEFAULT_ROW_VALUE_WIDTH)),
                ],
            row_data=[],
            use_pagination=DEFAULT_USE_PAGINATION,
            rows_num=DEFAULT_NUM_ROWS_PAGE,
            pagination_menu_height=dp(300),  # Set dropdown menu height
        )
        self.ids.table_container.add_widget(self.main_table)
    
    def _get_cells_from_checked_rows(self, index=0, cell_as_tuple=False):
        checked_rows = get_checked_rows(self.main_table, self.checked_rows)
        if not checked_rows:
            return
        
        cells = [
            (r[index], ) if cell_as_tuple else r[index] for r in checked_rows
            ]
        print(f"cells - {cells}")
        return cells
    
    def _delete_req_fields(self):
        checked_rows = get_checked_rows(self.main_table, self.checked_rows)

        if not checked_rows:
            return
        self._remove_rows_from_checked_rows()
    
    def _remove_rows_from_checked_rows(self):
        checked_rows = get_checked_rows(self.main_table, self.checked_rows)
        if not checked_rows:
            return
        
        for checked_row in checked_rows:
            Logger.critical(f"\n self.main_table - {self.main_table.row_data}")
            Logger.critical(f"\n row - {checked_row}")
            self.main_table.remove_row(tuple(checked_row))

    def _add_req_field(self, key, other_name):
        print(self._selected_req_fields)
        print(self.main_table.table_data.row_data)
        self.main_table.add_row((key, other_name))