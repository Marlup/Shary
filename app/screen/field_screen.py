# --- source/fields_screen.py ---
from kivy.lang import Builder
from kivy.logger import Logger
from kivymd.uix.snackbar import MDSnackbar
from kivy.metrics import dp
from kivymd.uix.button import MDRaisedButton
from kivy.uix.screenmanager import SlideTransition
from kivymd.uix.datatables import MDDataTable
from kivymd.uix.dialog import MDDialog
from kivymd.uix.dialog import MDDialog
from kivymd.uix.menu import MDDropdownMenu
from kivy.utils import platform
from kivy.uix.scrollview import ScrollView

from core.func_utils import (
    load_user_credentials,
    send_email,
    build_email,
    information_panel,
    get_safe_row_checks,
    send_data_to_firebase
)

from core.constant import (
    FILE_FORMATS,
    DEFAULT_ROW_KEY_WIDTH,
    DEFAULT_ROW_VALUE_WIDTH,
    DEFAULT_ROW_REST_WIDTH,
    DEFAULT_NUM_ROWS_PAGE,
    DEFAULT_USE_PAGINATION,
    SCREEN_NAME_FIELD,
    SCREEN_NAME_USER,
    SCREEN_NAME_FILE_VISUALIZER,
)

from core.class_utils import (
    AddField,
    SendEmailDialog,
    SendToFirebaseDialog,
    SelectChannel,
    EnhancedMDScreen
)

from core.dtos import FieldDTO
from core.repositories import FieldRepository

class FieldScreen(EnhancedMDScreen):
    def __init__(self, db_connection=None, **kwargs):
        super().__init__(name=SCREEN_NAME_FIELD, **kwargs)
        self.field_repo = FieldRepository(db_connection)
        
        self.dialog_add_field = Builder.load_file("widget_schemas/add_field_dialog.kv")  # Load the dialog definition
        self.email_dialog = Builder.load_file("widget_schemas/send_email_dialog.kv")  # Load the dialog definition
        self.to_firebase_dialog = Builder.load_file("widget_schemas/send_to_firebase_dialog.kv")  # Load the dialog definition
        self.channel_selection_dialog = Builder.load_file("widget_schemas/channel_selection_dialog.kv")  # Load the dialog definition
        
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
        #self.ids.table_container.remove_widget(self.main_table)
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
                title="Select Sending Channel",
                type="custom",
                content_cls=SelectChannel(size_hint_y=None, height="200dp"),
                buttons=[
                    MDRaisedButton(text="Cancel", on_release=lambda _: self.dismiss_channel_selection_dialog()),
                    MDRaisedButton(text="Send", on_release=lambda _: self.process_channel()),
            ],
            )
            #self._init_menu_formats()

        self.channel_selection_dialog.open()

    def show_menu(self, instance):
        menu_items = [
            {
                "viewclass": "OneLineListItem",
                "text": "Firebase Database",
                "on_release": lambda: self.set_text("Firebase Database")
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
        elif channel == "Firebase Database":
            self.show_send_to_firebase_dialog()
        else:
            self.show_send_to_firebase_dialog()

    def show_send_to_firebase_dialog(self):
        if not self.to_firebase_dialog:
            self.to_firebase_dialog = MDDialog(
                title="Send Fields via Firebase",
                type="custom",
                content_cls=SendToFirebaseDialog(size_hint_y=None, height="200dp"),
                buttons=[
                    MDRaisedButton(text="Cancel", on_release=lambda _: self.dismiss_to_firebase_dialog()),
                    MDRaisedButton(text="Send", on_release=lambda _: self.prepare_to_firebase()),
            ],
            )
            #self._init_menu_formats()

        self.to_firebase_dialog.open()
    
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
    
    def prepare_to_firebase(self):
        # Get Data
        # Row fields to be sent
        rows_to_send = get_safe_row_checks(self.main_table, self.checked_rows)
        print(f"rows_to_send - {rows_to_send}")

        # User credentials
        sender, _ = load_user_credentials()
        
        # Get and validate the recipients (list of emailss)
        recipients = self.manager.get_screen("users").get_checked_emails(index=1)
        print(f"recipients - {recipients}")

        if not recipients:
            information_panel("Action: sending fields", "Select at least one external user.")
            return
        
        # Check if to_firebase_dialog.
        if not hasattr(self, "to_firebase_dialog") or not self.to_firebase_dialog:
            print("to_firebase_dialog is not initialized")
            return
        
        # Check if the session id and secret key are set
        if hasattr(self.to_firebase_dialog.content_cls, "ids") \
           and (
                "session_id" in self.to_firebase_dialog.content_cls.ids \
                or "secret_key" in self.to_firebase_dialog.content_cls.ids
                ):
            session_id = self.to_firebase_dialog.content_cls.ids.session_id.text
            secret_key = self.to_firebase_dialog.content_cls.ids.secret_key.text
        else:
            print("session_id not found in to_firebase_dialog.content_cls.ids")
            return

        #self.menu_channel.dismiss()  # Close menu

        # Build the message
        send_data_to_firebase(rows_to_send, session_id, sender, recipients, secret_key)

    def prepare_email(self):
        # Get Data
        dialog_ids = self.email_dialog.content_cls.ids
        filename = dialog_ids.filename_input.text.strip()
        file_format = "json" #dialog_ids.file_format_dropdown.text.strip()
        
        # Row fields to be sent
        rows_to_send = get_safe_row_checks(self.main_table, self.checked_rows)
        print(f"rows_to_send - {rows_to_send}")
        
        # Email subject
        subject = f"Shary message with {len(rows_to_send)} fields"

        # User credentials
        sender_email, sender_password = load_user_credentials()

        # Validate file format
        if file_format not in FILE_FORMATS:
            information_panel("Action: sending email", "Invalid file format.")
            return
        
        # Get and validate the recipients (list of emailss)
        recipients = self.manager.get_screen("users").get_checked_emails(index=1)
        print(f"recipients - {recipients}")
        if not recipients:
            information_panel("Action: sending email", "Select at least one external user.")
            return
        
        # Build the email message
        message = build_email(sender_email, recipients, subject, rows_to_send, filename, file_format)
        
        # Send the email
        send_email(sender_email, sender_password, message)

    def dismiss_email_dialog(self):
        if self.email_dialog:
            self.email_dialog.dismiss()

    def dismiss_to_firebase_dialog(self):
        if self.to_firebase_dialog:
            self.to_firebase_dialog.dismiss()

    def dismiss_channel_selection_dialog(self):
        if self.channel_selection_dialog:
            self.channel_selection_dialog.dismiss()

    def clean_inputs(self):
        self.to_firebase_dialog.content_cls.ids.session_id.text = ""
        self.to_firebase_dialog.content_cls.ids.secret_key.text = ""

# -------- callbacks --------
    def go_to_users_screen(self):
        self.manager.transition = SlideTransition(direction="left", duration=0.4)
        self.manager.current = SCREEN_NAME_USER

    def go_to_field_visualizer_screen(self):
        self.manager.transition = SlideTransition(direction="right", duration=0.4)
        self.manager.current = SCREEN_NAME_FILE_VISUALIZER
    
    def on_enter(self):
        self._load_fields_from_db()
        