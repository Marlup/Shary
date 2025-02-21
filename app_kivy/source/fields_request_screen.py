from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.uix.screenmanager import Screen
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.togglebutton import ToggleButton
from kivy.core.window import Window


class SelectableButton(RecycleDataViewBehavior, ToggleButton):
    """Selectable button to mimic ListItemButton behavior in RecycleView."""
    index = None

    def refresh_view_attrs(self, rv, index, data):
        """Catch and handle the view changes."""
        self.index = index
        return super(SelectableButton, self).refresh_view_attrs(rv, index, data)

    def on_release(self):
        """Toggle selection on button press."""
        self.parent.parent.toggle_selection(self.index)


class SelectableButton(RecycleDataViewBehavior, ToggleButton):
    """Selectable button to mimic ListItemButton behavior in RecycleView."""
    index = None

    def refresh_view_attrs(self, rv, index, data):
        """Handle view changes."""
        self.index = index
        return super(SelectableButton, self).refresh_view_attrs(rv, index, data)

class FieldsRecycleView(RecycleView):
    """RecycleView customized for displaying fields with selection support."""

    def __init__(self, **kwargs):
        super(FieldsRecycleView, self).__init__(**kwargs)
        self.viewclass = 'SelectableButton'
        self.data = []

        # ✅ The layout manager must be added as a child
        self.add_widget(RecycleBoxLayout(
            default_size=(None, 48),
            default_size_hint=(1, None),
            size_hint_y=None,
            height=self.minimum_height,
            orientation='vertical'
        ))

    def add_field(self, field_name):
        """Adds a new field to the RecycleView."""
        self.data.append({'text': field_name})

    def delete_selected_fields(self):
        """Deletes selected fields from the RecycleView."""
        selected_indices = [index for index, item in enumerate(self.data) if item.get('selected', False)]
        for index in reversed(selected_indices):
            del self.data[index]


class FieldsRequestScreen(Screen):
    """Main screen for managing field requests."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = BoxLayout(orientation='vertical')

        self.header = Label(text='Fields Request Management', size_hint_y=None, height=50, bold=True)
        layout.add_widget(self.header)

        # Button layout
        button_layout = BoxLayout(size_hint_y=None, height=50)

        self.add_button = Button(text='Add Field')
        self.add_button.bind(on_press=self.add_field)

        self.delete_selected_button = Button(text='Delete Selection', disabled=True)
        self.delete_selected_button.bind(on_press=self.delete_selected_fields)

        self.back_button = Button(text='Back to Users')
        self.back_button.bind(on_press=self.go_to_users_screen)

        button_layout.add_widget(self.back_button)
        button_layout.add_widget(self.add_button)
        button_layout.add_widget(self.delete_selected_button)

        layout.add_widget(button_layout)
        self.add_widget(layout)

    def add_field(self, instance):
        """Adds a new field entry via popup."""
        popup = Popup(title='New Field', size_hint=(0.75, 0.5))
        content = BoxLayout(orientation='vertical')
        text_input = TextInput(hint_text='Enter key details')

        def add_to_list(instance):
            text = text_input.text.strip()
            if text:
                self.list_view.add_field(text)
                popup.dismiss()

        submit_button = Button(text='Add', on_press=add_to_list)
        content.add_widget(text_input)
        content.add_widget(submit_button)
        popup.content = content
        popup.open()

    def delete_selected_fields(self, instance):
        """Deletes selected fields from the list."""
        self.list_view.delete_selected_fields()
        self.toggle_delete_button()

    def toggle_delete_button(self, *args):
        """Enables or disables the delete button based on selection."""
        selected = any(item.get('selected', False) for item in self.list_view.data)
        self.delete_selected_button.disabled = not selected

    def go_to_users_screen(self, instance):
        """Navigates back to the users screen."""
        self.manager.current = 'users_screen'

    def on_enter(self):
        """Bind key event when this screen becomes active."""
        print(f"Screen '{self.name}' active: Key events bound.")
        Window.bind(on_key_down=self.on_key_down)

    def on_leave(self):
        """Unbind key event when leaving this screen."""
        print(f"Screen '{self.name}' inactive: Key events unbound.")
        Window.unbind(on_key_down=self.on_key_down)

def get_fields_request_screen():
    """Returns an instance of FieldsRequestScreen."""
    return FieldsRequestScreen()