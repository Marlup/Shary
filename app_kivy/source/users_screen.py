from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.lang import Builder
from kivy.core.window import Window
import mysql.connector

from source.query_schemas import (
    SELECT_ALL_USERS,
    DELETE_USER_BY_USERNAME,
    INSERT_USER
)

from source.constant import (
    ROW_HEIGHT,
)

class UsersScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(name="users", **kwargs)

        self.db_connection = self.connect_db()
        
        main_layout = BoxLayout(orientation="vertical")
        self.header = Label(text="Users Management", size_hint_y=None, height=50)
        main_layout.add_widget(self.header)

        # Table Container
        self.table = GridLayout(
            cols=4, 
            size_hint_y=None,
            row_default_height=ROW_HEIGHT,
            row_force_default=True,
            spacing=5,
            padding=[5, 5, 5, 5],
            )
        #self.table.bind(minimum_height=self.table.setter('height'))
        
        # Load Fields
        self.load_users_from_db()
        
        scroll_view = ScrollView()
        scroll_view.add_widget(self.table)
        main_layout.add_widget(scroll_view)
        
        # Buttons Layout
        btn_layout = BoxLayout(size_hint_y=None, height=50, spacing=20)
    
        # Delete user Layout
        self.delete_button = Button(text="Delete Selected")
        self.delete_button.bind(on_press=self.delete_users)

        # Add user Layout
        self.add_user_button = Button(text="Add User")
        self.add_user_button.bind(on_press=self.add_user)
        
        # Back from users to fields Layout
        self.back_button = Button(text="Back to Fields")
        self.back_button.bind(on_press=self.go_to_fields_screen)
        
        btn_layout.add_widget(self.back_button)
        btn_layout.add_widget(self.add_user_button)
        btn_layout.add_widget(self.delete_button)
        main_layout.add_widget(btn_layout)
        
        self.add_widget(main_layout)

    def connect_db(self):
        return mysql.connector.connect(
            host="localhost",
            user="root",
            password="admin",
            database="shary_demo"
        )

    def load_users_from_db(self):
        cursor = self.db_connection.cursor()
        cursor.execute(SELECT_ALL_USERS)
        records = cursor.fetchall()
        print(records)
        
        # Clear existing widgets
        self.table.clear_widgets()
        
        # Display rows
        self.table.add_widget(Label(text="Username", bold=True))
        self.table.add_widget(Label(text="Email", bold=True))
        self.table.add_widget(Label(text="Date", bold=True))
        
        # Display rows
        self.rows = []
        for username, email, created_at in records:
            row = [
                TextInput(text=username, readonly=True, size_hint_y=None, height=ROW_HEIGHT),
                TextInput(text=email, readonly=True, size_hint_y=None, height=ROW_HEIGHT),
                Label(text=str(created_at), size_hint_y=None, height=ROW_HEIGHT),
                Button(
                    text="🗑️",
                    size_hint=(None, None),
                    width=40,
                    height=40,
                    on_press=lambda instance, k=username: self.delete_users(k)
                    )
            ]
            self.rows.append(row)
            for widget in row:
                self.table.add_widget(widget)

        cursor.close()
    
    def focus_next_widget(self):
        """Cycle focus between username, password, and login button."""
        if self.manager.current != "users":  # Ensure you're on the right screen
            return

        focused_widget = next((w for w in self.table.children if getattr(w, "focus", False)), None)
        if focused_widget:
            current_index = self.table.children.index(focused_widget)
            next_index = (current_index + 1) % len(self.table.children)
        else:
            next_index = 0

        #print(f"next_index - {next_index}")
        # Set focus
        if hasattr(self.table.children[next_index], "focus"):
            self.table.children[next_index].focus = True

    def add_user(self, instance):
        popup_layout = BoxLayout(orientation="vertical")
        username_input = TextInput(hint_text="Username")
        email_input = TextInput(hint_text="Email")
        add_btn = Button(text="Add")
        
        def insert_user(instance):
            username = username_input.text.strip()
            email = email_input.text.strip()
            if username and email:
                cursor = self.db_connection.cursor()
                cursor.execute(INSERT_USER, (username, email))
                self.db_connection.commit()
                cursor.close()
                self.load_users_from_db()
        
        add_btn.bind(on_press=insert_user)
        popup_layout.add_widget(username_input)
        popup_layout.add_widget(email_input)
        popup_layout.add_widget(add_btn)
        
        self.add_widget(popup_layout)
    
    def delete_users(self, instance):
        cursor = self.db_connection.cursor()
        for username in selected_usernames:
            cursor.execute(DELETE_USER_BY_USERNAME, (username, ))
            self.db_connection.commit()
            cursor.close()

            for row in sorted(self.selected_rows, reverse=True):
                self.table.removeRow(row)

            self.selected_rows.clear()
            self.toggle_deletion_confirmation(False)
    
    def go_to_fields_screen(self, instance):
        self.manager.current = "fields"

    def on_key_down(self, window, key, scancode, codepoint, modifier):
        """Handle Tab and Enter key behaviors."""
        if key == 9:  # Tab key
            self.focus_next_widget()
            return True
        return False

    def on_enter(self):
        """Bind key event when this screen becomes active."""
        print(f"Screen '{self.name}' active: Key events bound.")
        Window.bind(on_key_down=self.on_key_down)

    def on_leave(self):
        """Unbind key event when leaving this screen."""
        print(f"Screen '{self.name}' inactive: Key events unbound.")
        Window.unbind(on_key_down=self.on_key_down)

def get_users_screen():
    #Builder.load_string()
    return UsersScreen()