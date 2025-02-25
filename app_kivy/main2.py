"""from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button

class PaddingSpacingDemo(App):
    def build(self):
        # Root layout to hold all examples vertically.
        root = BoxLayout(orientation="vertical", spacing=20, padding=20)
        
        # Example 1: No padding, no spacing.
        example1 = BoxLayout(orientation="vertical", size_hint_y=None, height=150)
        example1.add_widget(Label(text="No padding, no spacing", size_hint_y=0.4))
        layout1 = BoxLayout(orientation="horizontal", spacing=0, padding=0)
        layout1.add_widget(Button(text="Cancel"))
        layout1.add_widget(Button(text="Ok"))
        example1.add_widget(layout1)
        
        # Example 2: Moderate padding and spacing.
        example2 = BoxLayout(orientation="vertical", size_hint_y=None, height=150)
        example2.add_widget(Label(text="Padding=0, Spacing=10", size_hint_y=0.4))
        layout2 = BoxLayout(orientation="horizontal", spacing=10, padding=0)
        layout2.add_widget(Button(text="Cancel"))
        layout2.add_widget(Button(text="Ok"))
        example2.add_widget(layout2)
        
        # Example 3: Larger padding and spacing.
        example3 = BoxLayout(orientation="vertical", size_hint_y=None, height=150)
        example3.add_widget(Label(text="Padding=10, Spacing=0", size_hint_y=0.4))
        layout3 = BoxLayout(orientation="horizontal", spacing=0, padding=10)
        layout3.add_widget(Button(text="Cancel"))
        layout3.add_widget(Button(text="Ok"))
        example3.add_widget(layout3)
        
        
        # Add all examples to the root layout.
        root.add_widget(example1)
        root.add_widget(example2)
        root.add_widget(example3)
        
        return root

if __name__ == '__main__':
    PaddingSpacingDemo().run()
"""

"""from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button

class EqualHalfDemo(App):
    def build(self):
        layout = BoxLayout(orientation='horizontal')
        btn1 = Button(text='Button 1', size_hint=(2, 1))
        btn2 = Button(text='Button 2', size_hint=(2, 1))
        layout.add_widget(btn1)
        layout.add_widget(btn2)
        return layout

if __name__ == '__main__':
    EqualHalfDemo().run()
"""
"""
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.uix.label import Label

class FileUploadDemo(App):
    def build(self):
        # Main layout with vertical orientation
        self.root_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Label to display the selected file path
        self.path_label = Label(text="No file selected", size_hint=(1, 0.2))
        self.root_layout.add_widget(self.path_label)
        
        # Button to open the file chooser popup
        upload_button = Button(text="Upload File", size_hint=(1, 0.2))
        upload_button.bind(on_release=self.open_filechooser)
        self.root_layout.add_widget(upload_button)
        
        return self.root_layout

    def open_filechooser(self, instance):
        # Create a layout to hold the FileChooser and control buttons
        popup_content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        
        # FileChooser widget: using list view for a familiar file explorer look
        self.filechooser = FileChooserListView(path='.', filters=['*.*'])
        popup_content.add_widget(self.filechooser)
        
        # Layout for the action buttons
        btn_layout = BoxLayout(size_hint_y=0.2, spacing=10)
        select_btn = Button(text="Select")
        cancel_btn = Button(text="Cancel")
        btn_layout.add_widget(cancel_btn)
        btn_layout.add_widget(select_btn)
        popup_content.add_widget(btn_layout)
        
        # Create and open the popup
        self.popup = Popup(title="Select a file", content=popup_content, size_hint=(0.9, 0.9))
        self.popup.open()
        
        # Bind the buttons to their actions
        select_btn.bind(on_release=self.select_file)
        cancel_btn.bind(on_release=lambda *args: self.popup.dismiss())

    def select_file(self, instance):
        # Get the selection list from the file chooser widget
        selection = self.filechooser.selection
        if selection:
            selected_path = selection[0]
            # Update the label text with the selected file path
            self.path_label.text = f"Selected: {selected_path}"
        self.popup.dismiss()

if __name__ == '__main__':
    FileUploadDemo().run()"""

"""import tkinter as tk
from tkinter import filedialog

def open_native_file_dialog():
    # Create a root window and hide it since we don't need it.
    root = tk.Tk()
    root.withdraw()
    
    # Open the native file dialog and capture the selected file path.
    file_path = filedialog.askopenfilename(title="Select a file")
    
    # Optionally, print or process the file_path.
    if file_path:
        print(f"Selected file: {file_path}")
    else:
        print("No file selected.")

if __name__ == '__main__':
    open_native_file_dialog()"""


from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button

try:
    from plyer import filechooser
    plyer_available = True
except ImportError:
    plyer_available = False

class OSFileExplorerDemo(App):
    def build(self):
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        self.path_label = Label(text="No file selected", size_hint=(1, 0.2))
        layout.add_widget(self.path_label)
        upload_button = Button(text="Upload File", size_hint=(1, 0.2))
        upload_button.bind(on_release=self.open_native_filechooser)
        layout.add_widget(upload_button)
        return layout

    def open_native_filechooser(self, instance):
        if plyer_available:
            print("Opening native file chooser...")
            filechooser.open_file(callback=self.handle_selection)
        else:
            self.path_label.text = "Plyer is not available."
            print("Plyer not available.")

    def handle_selection(self, selection):
        print("handle_selection called with:", selection)
        if selection:
            self.path_label.text = "Selected: " + selection[0]
        else:
            self.path_label.text = "No file selected"

if __name__ == '__main__':
    OSFileExplorerDemo().run()

