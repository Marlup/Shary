from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import Screen
from kivy.core.window import Window
from kivy.uix.dropdown import DropDown
from kivy.graphics import Color, Rectangle

import sqlite3

from source.query_schemas import (
    SELECT_ALL_FIELDS,
    DELETE_FIELD_BY_KEY,
    INSERT_FIELD,
)

from source.constant import (
    ROW_HEIGHT,
    FIELD_HEADERS,
    MSG_DEFAULT_SEND_FILENAME,
    FILE_FORMATS
)

from source.class_utils import SelectableRow

from source.func_utils import (
    build_success_dialog,
    build_format_warning_dialog,
    build_email_error_dialog,
    build_no_fields_warning_dialog,
    send_email, 
    build_email_html_body,
    load_user_credentials,
    send_email,
)

class FieldsScreen(Screen):
    """Screen for managing fields with database interaction."""

    def __init__(self, **kwargs):
        super().__init__(name="fields", **kwargs)
        self.db_connection = self.connect_db()

        # Initialize internal _attributes
        self._selected_fields = []

        # Main layout
        main_layout = BoxLayout(orientation="vertical", spacing=10, padding=10)
      
        # Title header
        title_header = Label(text="Fields Management", size_hint_y=None, height=50)
        main_layout.add_widget(title_header)

        # Header
        header_layout = BoxLayout(size_hint=(1, 0.1), height=ROW_HEIGHT)
        self.add_header_label(header_layout, "[b]Key[/b]")
        self.add_header_label(header_layout, "[b]Value[/b]")
        self.add_header_label(header_layout, "[b]Date[/b]")
        main_layout.add_widget(header_layout)

        # Table Container
        self.table = GridLayout(
            cols=1,
            size_hint_y=None,
            row_default_height=ROW_HEIGHT,
            row_force_default=True,
            spacing=5,
            padding=[5, 5, 5, 5]
        )

        # Load Fields
        self.load_fields_from_db(SELECT_ALL_FIELDS)
        self.rows_indices = [i for i in self.table.children]
        
        scroll_view = ScrollView(size_hint=(1, 0.9))
        scroll_view.add_widget(self.table)
        main_layout.add_widget(scroll_view)

        # Buttons Layout
        btn_layout = BoxLayout(size_hint_y=None, height=50, spacing=20)

        # Send button
        self.send_btn = Button(text="Send Fields")
        self.send_btn.bind(on_press=self.send_fields)
        btn_layout.add_widget(self.send_btn)

        # Add button
        self.add_field_btn = Button(text="Add Field")
        self.add_field_btn.bind(on_press=self.add_field)
        btn_layout.add_widget(self.add_field_btn)

        # Select users button
        self.select_users_btn = Button(text="Select Users")
        self.select_users_btn.bind(on_press=self.select_users)
        btn_layout.add_widget(self.select_users_btn)

        main_layout.add_widget(btn_layout)
        self.add_widget(main_layout)

    def update_selected_fields(self, row_data, is_selected):
        """Track selected rows for future operations."""
        if is_selected:
            if row_data not in self._selected_fields:
                self._selected_fields.append(row_data)
        else:
            if row_data in self._selected_fields:
                self._selected_fields.remove(row_data)

    def delete_row(self, row, row_data):
        """Delete a specific row."""
        key = row_data[0]
        print(f"Deleting row with key: {key}")
        
        self.delete_field(key)
        self.table.remove_widget(row)
        self.update_selected_fields(row, False)

    def delete_field(self, key):
        """Deletes a field by key from the database."""
        cursor = self.db_connection.cursor()
        cursor.execute(DELETE_FIELD_BY_KEY, (key, ))
        self.db_connection.commit()
        cursor.close()
        self.load_fields_from_db(SELECT_ALL_FIELDS)

        self.on_n_rows_changed = True

    def send_fields(self, instance):
        sender_email, sender_password = load_user_credentials()
        # Accessing 'user_input' TextInput from FirstScreen
        recipients = self.manager.get_screen('users').get_selected_emails()
        
        # Collect selected fields
        num_fields = len(recipients)
        
        if num_fields == 0:
            build_no_fields_warning_dialog()
            return

        subject = f"Shary message with {num_fields} fields"

        popup_layout = BoxLayout(orientation="vertical", spacing=10, padding=10)
        options_layout = BoxLayout(orientation="horizontal", spacing=10, padding=10)
        
        filename_input = TextInput(hint_text="file name")
        popup_layout.add_widget(filename_input)

        dropdown_formats = DropDown()
        # Add items dynamically
        for file_format in FILE_FORMATS:
            btn = Button(text=file_format, size_hint_y=None, height=44)
            btn.bind(on_release=lambda btn: dropdown_formats.select(btn.text))
            dropdown_formats.add_widget(btn)
        
        file_format_button = Button(text="Select a format", size_hint=(None, None), size=(200, 44))
        file_format_button.bind(on_release=dropdown_formats.open)
        
        dropdown_formats.bind(on_select=lambda instance, x: x)
        popup_layout.add_widget(file_format_button)

        def _accept_send_email(instance):
            popup.dismiss()
        
        def _cancel_send_email(instance):
            popup.dismiss()

        send_btn = Button(text="Send", on_press=_accept_send_email, size_hint=(1, 0.2))
        cancel_btn = Button(text="Cancel", on_press=_cancel_send_email, size_hint=(1, 0.2))

        options_layout.add_widget(cancel_btn)
        options_layout.add_widget(send_btn)
        popup_layout.add_widget(options_layout)

        popup = Popup(title="Set email", content=popup_layout, size_hint=(0.7, 0.4))
        popup.open()
        
        file_format = file_format_button.text.strip()
        if not file_format:
            return
        
        filename = filename_input.text.strip()
        if not filename:
            sender_name = sender_email.split("@")[0]
            filename = f"{MSG_DEFAULT_SEND_FILENAME}{sender_name}"
        filename += f".{file_format}"

        message = build_email_html_body(
            sender_email, 
            recipients, 
            subject, 
            filename, 
            file_format_button.text, 
            self.table, 
            self._selected_fields
            )
        print("before send_email")
        return_message = send_email(sender_email, sender_password, message)
        
        if return_message == "":
            build_success_dialog()
        elif return_message == "bad-format":
            build_format_warning_dialog()
        else:
            build_email_error_dialog() # return_message

    def add_header_label(self, layout, text):
        """Add a styled label to the header."""
        label = Label(
            text=text,
            markup=True,            # Enables [b] bold tags
            halign="center",
            valign="middle"
        )
        label.bind(size=label.setter('text_size'))  # Ensure text aligns properly
        with label.canvas.before:
            Color(0.2, 0.6, 0.8, 0.8)  # Background color (light blue)
            rect = Rectangle(pos=label.pos, size=label.size)
            label.bind(pos=lambda instance, value: setattr(rect, 'pos', instance.pos))
            label.bind(size=lambda instance, value: setattr(rect, 'size', instance.size))
        layout.add_widget(label)

    def connect_db(self):
        """Establishes a connection to the SQLite database."""
        return sqlite3.connect("shary_demo")

    def load_fields_from_db(self, query):
        """Loads fields from the database and displays them in the UI."""
        cursor = self.db_connection.cursor()
        cursor.execute(query)
        records = cursor.fetchall()
        cursor.close()
        
        # Clear existing widgets
        self.table.clear_widgets()

        # Display rows
        self.rows = []
        
        for record in records:
            row = SelectableRow(
                *record,
                select_callback=self.update_selected_fields
            )
            # Dummy delete button action
            row.delete_button.bind(on_press=lambda instance, 
                                   r=row: self.delete_row(r, record))
            self.table.add_widget(row)

        # Update height based on the number of rows
        self.table.height = ROW_HEIGHT * len(records)

    def add_field(self, instance):
        """Opens a popup to add a new field."""
        popup_layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        options_layout = BoxLayout(orientation="horizontal", spacing=10, padding=10)
        
        key_input = TextInput(hint_text="Key")
        value_input = TextInput(hint_text="Value")

        def _save_field(instance):
            key = key_input.text.strip()
            value = value_input.text.strip()
            if key:
                cursor = self.db_connection.cursor()
                cursor.execute(INSERT_FIELD, (key, value, ""))
                self.db_connection.commit()
                cursor.close()
                self.load_fields_from_db(SELECT_ALL_FIELDS)
            popup.dismiss()
        
        def _cancel_add(instance):
            popup.dismiss()

        save_btn = Button(text="Save", on_press=_save_field, size_hint=(1, 0.2))
        cancel_btn = Button(text="Cancel", on_press=_cancel_add, size_hint=(1, 0.2))
        popup_layout.add_widget(key_input)
        popup_layout.add_widget(value_input)

        options_layout.add_widget(cancel_btn)
        options_layout.add_widget(save_btn)
        popup_layout.add_widget(options_layout)

        popup = Popup(title="Add Field", content=popup_layout, size_hint=(0.7, 0.4))
        popup.open()
    
    def select_users(self, instance):
        """method for users selection."""
        self.manager.current = "users"

    def on_key_down(self, window, key, scancode, codepoint, modifier):
        """Handle Tab and Enter key behaviors."""
        if key == 9:  # Tab key
            self.focus_next_widget()
            return True
        return False

    def focus_next_widget(self):
        """Cycle focus between field's rows."""
        if self.manager.current != 'fields':  # Ensure you're on the right screen
            return
        
        if not self.table.children:
            return

        focused_widget = next((w for w in self.table.children if getattr(w, 'focus', False)), None)
        if focused_widget:
            current_index = self.table.children.index(focused_widget)
            next_index = (current_index + 1) % len(self.table.children)
        else:
            next_index = 0

        #print(f"next_index - {next_index}")
        # Set focus
        if hasattr(self.table.children[next_index], 'focus'):
            self.table.children[next_index].focus = True

    def on_enter(self):
        """Bind key event when this screen becomes active."""
        print(f"Screen '{self.name}' active: Key events bound.")
        Window.bind(on_key_down=self.on_key_down)

    def on_leave(self):
        """Unbind key event when leaving this screen."""
        print(f"Screen '{self.name}' inactive: Key events unbound.")
        Window.unbind(on_key_down=self.on_key_down)

def get_fields_screen():
    """Returns an instance of FieldsScreen."""
    return FieldsScreen()
