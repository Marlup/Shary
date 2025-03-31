# --- source/requests_screen.py ---
from kivy.lang import Builder
from kivy.uix.screenmanager import SlideTransition
from kivy.metrics import dp
from kivy.logger import Logger
from kivymd.uix.screen import MDScreen
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.snackbar import MDSnackbar
from kivymd.uix.datatables import MDDataTable
from kivymd.uix.dialog import MDDialog

from front.core.constant import (
    MSG_DEFAULT_REQUEST_FILENAME,
    FILE_FORMATS,
    DEFAULT_ROW_KEY_WIDTH,
    DEFAULT_ROW_VALUE_WIDTH,
    DEFAULT_USE_PAGINATION,
    DEFAULT_NUM_ROWS_PAGE,
    SCREEN_NAME_FIELD,
    SCREEN_NAME_REQUEST,
    SCREEN_NAME_USER,
    PATH_SCHEMA_REQUEST_DIALOG
)

from front.core.class_utils import (
    AddRequestField,
    SendEmailDialog
)

from front.core.func_utils import (
    information_panel,
)

class RequestScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(name=SCREEN_NAME_REQUEST, **kwargs)
        Builder.load_file(PATH_SCHEMA_REQUEST_DIALOG)  # Load the dialog definition
        
        self.main_table = None
        self._selected_req_fields = []
        self.dialog = None
        self.email_dialog = None
        
        if self.main_table:
            self.ids.table_container.remove_widget(self.main_table)
        
    def _initialize_table(self):
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
    
    def _delete_req_fields(self):
        checked_rows = self.main_table.get_row_checks()

        if not checked_rows:
            return
        self._remove_rows_from_checked_rows()
    
    def _get_cells_from_checked_rows(self, index=0, cell_as_tuple=False):
        rows = self.main_table.get_row_checks()

        cells = [
            (r[index], ) if cell_as_tuple else r[index] for r in rows
            ]
        print(f"cells - {cells}")
        return cells

    def _remove_rows_from_checked_rows(self):
        rows = self.main_table.get_row_checks()
        if not rows:
            return
        for row in rows:
            Logger.critical(f"\n self.main_table - {self.main_table.row_data}")
            Logger.critical(f"\n row - {row}")
            self.main_table.remove_row(tuple(row))

    def _add_req_field(self, key, other_name):
        print(self._selected_req_fields)
        print(self.main_table.table_data.row_data)
        self.main_table.add_row((key, other_name))

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
            #toast(f"Request field '{key}' added successfully!")
            MDSnackbar(f"Request field '{key}' added successfully!").show()
        else:
            #toast("Key is required.")
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
        dialog_ids = self.email_dialog.content_cls.ids
        filename = dialog_ids.filename_input.text.strip()
        file_format = "json_req"  # Tipo especial para solicitudes (puede ser extendido en el servicio)

        # Obtener datos de la tabla
        rows_to_send = self.main_table.get_row_checks()

        # Obtener destinatarios desde la pantalla de usuarios
        recipients = self.manager.get_screen(SCREEN_NAME_USER).get_checked_emails(index=1)

        # Preparar payload con validación dentro del servicio
        payload = self.manager.email_service.create_payload(
            rows=rows_to_send,
            recipients=recipients,
            filename=filename,
            file_format=file_format
        )

        if not payload:
            return  # El servicio ya manejó la información del error

        # Enviar el email usando el payload completo
        self.manager.email_service.send_from_payload(payload)

        # Feedback visual y cerrar diálogo
        information_panel("Action: sending email", "Email sent successfully")
        self.email_dialog.dismiss()

    def dismiss_email_dialog(self):
        if self.email_dialog:
            self.email_dialog.dismiss()

    def go_to_fields_screen(self):
        self.manager.transition = SlideTransition(direction="left", duration=0.4)
        self.manager.current = SCREEN_NAME_FIELD

    def go_to_users_screen(self):
        self.manager.transition = SlideTransition(direction="right", duration=0.4)
        self.manager.current = SCREEN_NAME_USER

    def on_enter(self):
        self._initialize_table()