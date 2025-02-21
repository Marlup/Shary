from kivy.uix.dropdown import DropDown
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics import Color, Rectangle
from kivy.uix.togglebutton import ToggleButton

from source.constant import (
    ROW_HEIGHT
)

class ComboBoxCell(BoxLayout):
    """Custom ComboBox equivalent for a Kivy table cell."""
    def __init__(self, options, selected_value='', on_select_callback=None, **kwargs):
        super().__init__(orientation='horizontal', **kwargs)
        self.options = options
        self.selected_value = selected_value
        self.on_select_callback = on_select_callback
        
        self.label = Label(text=selected_value if selected_value else 'Select an option')
        self.dropdown_button = Button(text='▼', size_hint=(0.2, 1))
        
        self.dropdown_button.bind(on_release=self.open_dropdown)
        self.add_widget(self.label)
        self.add_widget(self.dropdown_button)

    def open_dropdown(self, instance):
        dropdown = DropDown()
        
        for option in self.options:
            btn = Button(text=option, size_hint_y=None, height=44)
            btn.bind(on_release=lambda btn: self.select_option(dropdown, btn.text))
            dropdown.add_widget(btn)

        dropdown.open(self.dropdown_button)

    def select_option(self, dropdown, value):
        """Handles option selection and updates the label."""
        self.label.text = value
        self.selected_value = value
        dropdown.dismiss()
        if self.on_select_callback:
            self.on_select_callback(value)

class ComboBoxTable(GridLayout):
    """Table component with ComboBox cells."""
    def __init__(self, headers, rows, options, **kwargs):
        super().__init__(cols=len(headers), size_hint_y=None, **kwargs)
        self.bind(minimum_height=self.setter('height'))
        self.headers = headers
        self.options = options
        self.rows = rows

        # Render headers
        for header in headers:
            self.add_widget(Label(text=header, bold=True))
        
        # Render rows
        for row_data in rows:
            for i, cell_data in enumerate(row_data):
                if isinstance(cell_data, list):
                    # If cell data should be a ComboBox
                    self.add_widget(ComboBoxCell(self.options, selected_value=cell_data[0]))
                else:
                    self.add_widget(TextInput(text=cell_data))

    def get_table_data(self):
        """Retrieves the current data from the table."""
        data = []
        for row_index in range(len(self.rows)):
            row = []
            for col_index in range(len(self.headers)):
                widget = self.children[(len(self.headers) * (len(self.rows)-row_index-1)) + col_index]
                if isinstance(widget, ComboBoxCell):
                    row.append(widget.selected_value)
                elif isinstance(widget, TextInput):
                    row.append(widget.text)
                else:
                    row.append('')
            data.append(row)
        return data

class SelectableRow(BoxLayout):
    """Row with a round toggle button for selection and highlighting."""

    #def __init__(self, key, value, date, select_callback, **kwargs):
    def __init__(self, *values, select_callback=None, **kwargs):
        super().__init__(orientation='horizontal', size_hint_y=None, height=ROW_HEIGHT, **kwargs)
        #self.key = key
        #self.value = value
        #self.date = date
        self.field_data = values[:-1]
        self.field_date = values[-1]
        if select_callback is None:
            self.select_callback = lambda x: ()
        else:
            self.select_callback = select_callback
        self.selected = False

        # ✅ Round selection button
        self.select_button = ToggleButton(
            text="✔", size_hint=(None, None), width=40, height=40,
            background_normal='',
            background_color=[0.7, 0.7, 0.7, 1],
            border=(20, 20, 20, 20)
        )
        self.select_button.bind(on_press=self.toggle_selection)
        self.add_widget(self.select_button)

        # ✅ Row data fields
        for data in self.field_data:
            text_input_widget = TextInput(text=data, readonly=True, size_hint_y=None, height=ROW_HEIGHT)
            self.add_widget(text_input_widget)
        date_label = Label(text=str(self.field_date), size_hint_y=None, height=ROW_HEIGHT, color=(0, 0, 0, 1))
        self.add_widget(date_label)

        # ✅ Delete button
        self.delete_button = Button(
            text="🗑️",
            size_hint=(None, None),
            width=40,
            height=40,
            background_color=[0.8, 0, 0, 0.8]
        )
        self.add_widget(self.delete_button)

    def toggle_selection(self, instance):
        """Handle row selection toggle."""
        self.selected = instance.state == 'down'
        self.highlight(self.selected)
        self.select_callback(self, self.selected)

    def highlight(self, selected):
        """Highlight row when selected."""
        self.canvas.before.clear()
        with self.canvas.before:
            Color(0, 0.5, 1, 0.3 if selected else 0)  # Blue highlight
            rect = Rectangle(pos=self.pos, size=self.size)
            self.bind(pos=lambda *args: setattr(rect, 'pos', self.pos))
            self.bind(size=lambda *args: setattr(rect, 'size', self.size))