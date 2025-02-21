from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.label import Label
from kivy.uix.behaviors import ButtonBehavior
from kivy.properties import ListProperty, BooleanProperty

class SelectableRow(ButtonBehavior, BoxLayout, RecycleDataViewBehavior):
    """Row that can be selected, highlighted, and deselected."""
    selected = BooleanProperty(False)  # Tracks if the row is selected
    index = None  # Index of the row in the RecycleView

    def refresh_view_attrs(self, rv, index, data):
        """Refresh row attributes and apply selection color if needed."""
        self.index = index
        self.selected = data.get('selected', False)
        self.ids.label.text = data['text']
        self.update_background()
        return super().refresh_view_attrs(rv, index, data)

    def on_press(self):
        """Toggle row selection on click."""
        self.selected = not self.selected
        self.update_background()
        self.parent.parent.toggle_selection(self.index, self.selected)

    def update_background(self):
        """Highlight the row if selected."""
        self.ids.label.color = (1, 1, 1, 1) if self.selected else (0, 0, 0, 1)
        self.canvas.before.clear()
        with self.canvas.before:
            from kivy.graphics import Color, Rectangle
            Color(0, 0.5, 1, 0.3 if self.selected else 0)  # Blue highlight if selected
            Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self.update_background_size, size=self.update_background_size)

    def update_background_size(self, *args):
        """Ensure the background rectangle resizes with the widget."""
        self.canvas.before.children[-1].pos = self.pos
        self.canvas.before.children[-1].size = self.size


class RowRecycleView(RecycleView):
    """RecycleView that handles row selection and storage."""
    selected_fields = ListProperty([])  # Stores selected row data

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.data = [{'text': f'Row {i + 1}', 'selected': False} for i in range(10)]

    def toggle_selection(self, index, is_selected):
        """Add or remove rows from the selected list based on selection."""
        row_data = self.data[index]['text']
        if is_selected:
            if row_data not in self.selected_fields:
                self.selected_fields.append(row_data)
        else:
            if row_data in self.selected_fields:
                self.selected_fields.remove(row_data)
        print(f"Selected fields: {self.selected_fields}")


class MainLayout(BoxLayout):
    """Main layout containing the selectable RecycleView."""
    pass

class RowSelectionApp(App):
    def build(self):
        return MainLayout()

if __name__ == '__main__':
    RowSelectionApp().run()
