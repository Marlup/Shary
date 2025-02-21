from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import Screen
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle

import mysql.connector

from source.query_schemas import (
    SELECT_ALL_FIELDS,
    DELETE_FIELD_BY_KEY,
    INSERT_FIELD,
)

from source.constant import (
    ROW_HEIGHT,
)

from source.class_utils import SelectableRow

class FieldsScreen(Screen):
    """Screen for managing fields with database interaction."""

    def __init__(self, **kwargs):
        super().__init__(name="fields", **kwargs)
        self.db_connection = self.connect_db()
        #Window.bind(on_key_down=self.on_key_down)  # 🔑 Bind key press events

        # Constants
        self.on_n_rows_changed = False

        # Main layout
        main_layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        
        # Header layout
        self.header = Label(text="Fields Management", size_hint_y=None, height=50)
        main_layout.add_widget(self.header)

        # Header
        header_layout = BoxLayout(size_hint=(1, 0.1), height=ROW_HEIGHT)
        self.add_header_label(header_layout, "[b]Select[/b]")
        self.add_header_label(header_layout, "[b]Key[/b]")
        self.add_header_label(header_layout, "[b]Value[/b]")
        self.add_header_label(header_layout, "[b]Date[/b]")
        main_layout.add_widget(header_layout)

        # Table Container
        self.table = GridLayout(
            cols=5,
            size_hint_y=None,
            row_default_height=ROW_HEIGHT,
            row_force_default=True,
            spacing=5,
            padding=[5, 5, 5, 5]
        )

        # Load Fields
        self.load_fields_from_db()
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

    def update_selected_fields(self, row, is_selected):
        """Track selected rows for future operations."""
        row_data = {"key": row.key, "value": row.value, "date": row.date}
        if is_selected:
            if row_data not in self.selected_fields:
                self.selected_fields.append(row_data)
        else:
            if row_data in self.selected_fields:
                self.selected_fields.remove(row_data)
        print(f"Selected fields: {self.selected_fields}")

    def delete_row(self, row):
        """Delete a specific row (simulated)."""
        print(f"Deleting row with key: {row.key}")
        self.table.remove_widget(row)
        self.update_selected_fields(row, False)

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
        """Establishes a connection to the MySQL database."""
        return mysql.connector.connect(
            host="localhost",
            user="root",
            password="admin",
            database="shary_demo"
        )

    def load_fields_from_db2(self):
        """Loads fields from the database and displays them in the UI."""
        cursor = self.db_connection.cursor()
        cursor.execute(SELECT_ALL_FIELDS)
        records = cursor.fetchall()
        cursor.close()

        # Clear existing widgets
        self.table.clear_widgets()

        # Display rows
        self.rows = []
        for key, value, date in records:
            row = [
                TextInput(text=key, readonly=True, size_hint_y=None, height=ROW_HEIGHT),
                TextInput(text=value, size_hint_y=None, height=ROW_HEIGHT, multiline=True),
                TextInput(text=str(date), size_hint_y=None, height=ROW_HEIGHT),
                Button(
                    text="🗑️",
                    size_hint=(None, None),
                    width=40,
                    height=40,
                    on_press=lambda instance, k=key: self.delete_field(k),
                    background_color=[0.8, 0, 0, 0.8]
                )
            ]
            self.rows.append(row)
            for widget in row:
                self.table.add_widget(widget)

        # Update height based on the number of rows
        self.table.height = ROW_HEIGHT * len(records)

    def load_fields_from_db(self):
        """Loads fields from the database and displays them in the UI."""
        cursor = self.db_connection.cursor()
        cursor.execute(SELECT_ALL_FIELDS)
        records = cursor.fetchall()
        cursor.close()

        # Clear existing widgets
        self.table.clear_widgets()

        # Display rows
        self.rows = []
        for key, value, date in records:
            row = SelectableRow(
                key=key,
                value=value,
                date=date,
                select_callback=self.update_selected_fields
            )
            # Dummy delete button action
            row.delete_button.bind(on_press=lambda instance, r=row: self.delete_row(r))
            self.table.add_widget(row)

        # Update height based on the number of rows
        self.table.height = ROW_HEIGHT * len(records)

    def add_field(self, instance):
        """Opens a popup to add a new field."""
        popup_layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        key_input = TextInput(hint_text="Key")
        value_input = TextInput(hint_text="Value")

        def save_field(instance):
            key = key_input.text.strip()
            value = value_input.text.strip()
            if key:
                cursor = self.db_connection.cursor()
                cursor.execute(INSERT_FIELD, (key, value))
                self.db_connection.commit()
                cursor.close()
                popup.dismiss()
                self.load_fields_from_db()
            else:
                popup.dismiss()

        save_btn = Button(text="Save", on_press=save_field, size_hint=(1, 0.2))
        popup_layout.add_widget(key_input)
        popup_layout.add_widget(value_input)
        popup_layout.add_widget(save_btn)

        popup = Popup(title="Add Field", content=popup_layout, size_hint=(0.7, 0.4))
        popup.open()

        self.on_n_rows_changed = True

    def delete_field(self, key):
        """Deletes a field by key from the database."""
        cursor = self.db_connection.cursor()
        cursor.execute(DELETE_FIELD_BY_KEY, (key,))
        self.db_connection.commit()
        cursor.close()
        self.load_fields_from_db()

        self.on_n_rows_changed = True

    def send_fields(self, instance):
        """Placeholder method for sending fields."""
        print("Sending fields...")  # Replace with actual logic
    
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
        """Cycle focus between username, password, and login button."""
        if self.manager.current != 'fields':  # Ensure you're on the right screen
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
