from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle

import sqlite3

from source.query_schemas import (
    SELECT_ALL_USERS,
    DELETE_USER_BY_USERNAME,
    INSERT_USER
)

from source.constant import (
    ROW_HEIGHT,
    USER_HEADERS,
)

from source.class_utils import SelectableRow

class UsersScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(name="users", **kwargs)
        self.db_connection = self.connect_db()

        # Initialize internal _attributes
        self._selected_users = []
        
        # Main layout
        main_layout = BoxLayout(orientation="vertical", spacing=10, padding=10)

        # Title header
        title_header = Label(text="Users Management", size_hint_y=None, height=50)
        main_layout.add_widget(title_header)
        
        # Header
        header_layout = BoxLayout(size_hint=(1, 0.1), height=ROW_HEIGHT)
        self.add_header_label(header_layout, "[b]Username[/b]")
        self.add_header_label(header_layout, "[b]Email[/b]")
        self.add_header_label(header_layout, "[b]Phone[/b]")
        self.add_header_label(header_layout, "[b]Date[/b]")
        main_layout.add_widget(header_layout)

        # Table Container
        self.table = GridLayout(
            cols=1, 
            size_hint_y=None,
            row_default_height=ROW_HEIGHT,
            row_force_default=True,
            spacing=5,
            padding=[5, 5, 5, 5],
            )
        
        # Load Users
        self.load_users_from_db(SELECT_ALL_USERS)
        self.rows_indices = [i for i in self.table.children]

        scroll_view = ScrollView(size_hint=(1, 0.9))
        scroll_view.add_widget(self.table)
        main_layout.add_widget(scroll_view)
        
        # Buttons Layout
        btn_layout = BoxLayout(size_hint_y=None, height=50, spacing=20)

        # Back from users to fields Layout
        self.back_button = Button(text="Back to Fields")
        self.back_button.bind(on_press=self.go_to_fields_screen)
        
        # Add user Layout
        self.add_user_button = Button(text="Add User")
        self.add_user_button.bind(on_press=self.add_user)
        
        # Back from users to fields Layout
        self.request_button = Button(text="Start Request")
        self.request_button.bind(on_press=self.go_to_requests_screen)
        
        btn_layout.add_widget(self.back_button)
        btn_layout.add_widget(self.add_user_button)
        btn_layout.add_widget(self.request_button)
        main_layout.add_widget(btn_layout)
        
        self.add_widget(main_layout)

    def update_selected_users(self, row_data, is_selected):
        """Track selected rows for future operations."""
        print(row_data)
        if is_selected:
            if row_data not in self._selected_users:
                self._selected_users.append(row_data)
        else:
            if row_data in self._selected_users:
                self._selected_users.remove(row_data)
        print(f"Selected users: {self._selected_users}")

    def delete_row(self, row, row_data):
        """Delete a specific row."""
        key = row_data[0]
        print(f"Deleting row with key: {key}")

        self.delete_user(key)
        self.table.remove_widget(row)
        self.update_selected_users(row_data, False)

    def delete_user(self, key):
        """Deletes a user by username from the database."""
        cursor = self.db_connection.cursor()
        cursor.execute(DELETE_USER_BY_USERNAME, (key, ))
        self.db_connection.commit()
        cursor.close()
        self.load_users_from_db(SELECT_ALL_USERS)

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
        return sqlite3.connect("shary_demo")

    def load_users_from_db(self, query):
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
                select_callback=self.update_selected_users
            )
            # Dummy delete button action
            row.delete_button.bind(on_press=lambda _: self.delete_row(row, record))
            self.table.add_widget(row)

        # Update height based on the number of rows
        self.table.height = ROW_HEIGHT * len(records)
    
    def add_user(self, instance):
        """Opens a popup to add a new user."""
        popup_layout = BoxLayout(orientation="vertical")
        options_layout = BoxLayout(orientation="horizontal", spacing=300)
        
        username_input = TextInput(hint_text="Username", multiline=False)
        email_input = TextInput(hint_text="Email", multiline=False)

        def _save_user(instance):
            username = username_input.text.strip()
            email = email_input.text.strip()
            
            if username and email:
                cursor = self.db_connection.cursor()
                cursor.execute(INSERT_USER, (username, email, 0, 0))
                self.db_connection.commit()
                cursor.close()
                self.load_users_from_db(SELECT_ALL_USERS)
            popup.dismiss()
        
        def _cancel_add(instance):
            popup.dismiss()

        save_btn = Button(text="Save", on_press=_save_user, size_hint=(0.3, 0.35))
        cancel_btn = Button(text="Cancel", on_press=_cancel_add, size_hint=(0.3, 0.35))
        popup_layout.add_widget(username_input)
        popup_layout.add_widget(email_input)

        options_layout.add_widget(cancel_btn)
        options_layout.add_widget(save_btn)
        popup_layout.add_widget(options_layout)

        popup = Popup(title="Add User", content=popup_layout, size_hint=(0.7, 0.4))
        popup.open()

    def go_to_fields_screen(self, instance):
        self.manager.current = "fields"
    
    def go_to_requests_screen(self, instance):
        self.manager.current = "requests"

    def on_key_down(self, window, key, scancode, codepoint, modifier):
        """Handle Tab and Enter key behaviors."""
        if key == 9:  # Tab key
            self.focus_next_widget()
            return True
        return False

    def focus_next_widget(self):
        """Cycle focus between user's rows."""
        if self.manager.current != 'users':  # Ensure you're on the right screen
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

    def get_selected_emails(self):
        users = self._get_selected_users()
        # user -> (username, email, creation_date)
        return [user.get_data()[1] for user in users]
    
    def _get_selected_users(self):
        return self._selected_users

def get_users_screen():
    #Builder.load_string()
    return UsersScreen()