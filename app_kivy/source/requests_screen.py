from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.core.window import Window
from kivy.uix.dropdown import DropDown
from kivy.graphics import Color, Rectangle

from source.constant import (
    ROW_HEIGHT,
    MSG_DEFAULT_REQUEST_FILENAME,
)

from source.class_utils import SelectableRow

from source.func_utils import (
    load_user_credentials,
    build_email_html_body,
    send_email,
    information_panel
)

class RequestsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(name="requests", **kwargs)

        # Initialize internal _attributes
        self._selected_requests = []
        
        # Main layout
        main_layout = BoxLayout(orientation="vertical", spacing=10, padding=10)

        # Title header
        title_header = Label(text="Requests Management", size_hint_y=None, height=50)
        main_layout.add_widget(title_header)
        
        # Header
        header_layout = BoxLayout(size_hint=(1, 0.1), height=ROW_HEIGHT)
        self.add_header_label(header_layout, "[b]Key[/b]")
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
        
        scroll_view = ScrollView(size_hint=(1, 0.9))
        scroll_view.add_widget(self.table)
        main_layout.add_widget(scroll_view)
        
        # Buttons Layout
        btn_layout = BoxLayout(size_hint_y=None, height=50, spacing=20)

        # Back from requests to users button
        self.back_button = Button(text="Back to Fields")
        self.back_button.bind(on_press=self.go_to_users_screen)
        
        # Add field button
        self.add_field_button = Button(text="Add Field")
        self.add_field_button.bind(on_press=self.add_field_request)

        # Add send request button
        self.send_request_button = Button(text="Send Request")
        self.send_request_button.bind(on_press=self.send_request)
        
        btn_layout.add_widget(self.back_button)
        btn_layout.add_widget(self.add_field_button)
        btn_layout.add_widget(self.send_request_button)
        main_layout.add_widget(btn_layout)
        
        self.add_widget(main_layout)

    def update_selected_requests(self, row_data, is_selected):
        """Track selected rows for future operations."""
        print(row_data)
        if is_selected:
            if row_data not in self._selected_requests:
                self._selected_requests.append(row_data)
        else:
            if row_data in self._selected_requests:
                self._selected_requests.remove(row_data)
        print(f"Selected requests: {self._selected_requests}")

    def delete_row(self, row, row_data):
        """Delete a specific row."""
        key = row_data[0]
        print(f"Deleting row with key: {key}")

        self.table.remove_widget(row)

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
    
    def add_field_request(self, instance):
        """Opens a popup to add a new user."""
        popup_layout = BoxLayout(orientation="vertical")
        options_layout = BoxLayout(orientation="horizontal", spacing=300)
        
        key_input = TextInput(hint_text="Key name", multiline=False)

        def _save_user(instance):
            key = key_input.text.strip()
            if not key:
                return
            record = (key, )

            row = SelectableRow(
                *record,
                select_callback= lambda : ()
            )
            # Dummy delete button action
            row.delete_button.bind(on_press=lambda _: self.delete_row(row, record))
            self.table.add_widget(row)

            # Update height based on the number of rows
            self.table.height = ROW_HEIGHT * len(self.table.children)
            popup.dismiss()
        
        def _cancel_add(instance):
            popup.dismiss()

        save_btn = Button(text="Save", on_press=_save_user, size_hint=(0.3, 0.35))
        cancel_btn = Button(text="Cancel", on_press=_cancel_add, size_hint=(0.3, 0.35))
        popup_layout.add_widget(key_input)

        options_layout.add_widget(cancel_btn)
        options_layout.add_widget(save_btn)
        popup_layout.add_widget(options_layout)

        popup = Popup(title="Add Key", content=popup_layout, size_hint=(0.7, 0.4))
        popup.open()

    def send_request(self, instance):
        if not self.table.children:
            information_panel("Action: sending email", "Select at least one field to send.")
            return

        popup_layout = BoxLayout(orientation="vertical")
        options_layout = BoxLayout(orientation="horizontal", spacing=300)
        
        filename_input = TextInput(hint_text="file name")
        popup_layout.add_widget(filename_input)

        def _accept_send_email(instance):
            sender_email, sender_password = load_user_credentials()
            # Accessing 'user_input' TextInput from FirstScreen
            recipients = self.manager.get_screen("users").get_selected_emails()
            if not self.table.children:
                information_panel("Action: sending email", "Select at least one external user to send to.")
                return
            
            filename = filename_input.text.strip()
            if not filename:
                sender_name = sender_email.split("@")[0]
                filename = f"{MSG_DEFAULT_REQUEST_FILENAME}{sender_name}"
            filename += ".json"

            subject = f"Shary message with {len(self.table.children)} fields"
            message = build_email_html_body(
                sender_email, 
                recipients, 
                subject, 
                filename, 
                "json", 
                self.table.children,
                True,
                )

            return_message = send_email(sender_email, sender_password, message)

            if return_message == "":
                information_panel("Action: sending email", "Email sent successfully")
            elif return_message == "bad-format":
                information_panel("Action: sending email", "Bad format: email not sent")
            else:
                information_panel("Action: sending email", "Error at sending: " + str(return_message))

            popup.dismiss()
        
        def _cancel_send_email(instance):
            popup.dismiss()

        send_btn = Button(text="Send", on_press=_accept_send_email, size_hint=(0.3, 0.35))
        cancel_btn = Button(text="Cancel", on_press=_cancel_send_email, size_hint=(0.3, 0.35))

        options_layout.add_widget(cancel_btn)
        options_layout.add_widget(send_btn)
        popup_layout.add_widget(options_layout)

        popup = Popup(title="Set email", content=popup_layout, size_hint=(0.7, 0.4))
        popup.open()

    def go_to_users_screen(self, instance):
        self.manager.current = "users"

    def on_key_down(self, window, key, scancode, codepoint, modifier):
        """Handle Tab and Enter key behaviors."""
        if key == 9:  # Tab key
            self.focus_next_widget()
            return True
        return False

    def focus_next_widget(self):
        """Cycle focus between user's rows."""
        if self.manager.current != 'requests':  # Ensure you're on the right screen
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

def get_requests_screen():
    #Builder.load_string()
    return RequestsScreen()