from kivy.lang import Builder
from kivymd.uix.screen import MDScreen
#from kivymd.toast import toast
from kivymd.uix.datatables import MDDataTable
from kivymd.uix.snackbar import MDSnackbar
from kivymd.uix.dialog import MDDialog
from kivymd.uix.menu import MDDropdownMenu
from kivy.metrics import dp
from kivy.uix.screenmanager import SlideTransition
from kivy.logger import Logger
import json
import os

from core.constant import (
    DEFAULT_ROW_KEY_WIDTH,
    DEFAULT_ROW_VALUE_WIDTH,
    DEFAULT_ROW_REST_WIDTH,
    DEFAULT_NUM_ROWS_PAGE,
    DEFAULT_USE_PAGINATION,
    PATH_FILE_STORAGE,
    SCREEN_NAME_FIELD,
    SCREEN_NAME_FILE_VISUALIZER,
)

class FileVisualizerScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(name=SCREEN_NAME_FILE_VISUALIZER, **kwargs)
        
        self.main_table = None
        self.dialog = None
        self.selected_file = None
        self.json_files = self._get_json_files()
        self.menu = None  # Don't create menu here!
        
    def _initialize_table(self):
        """Initialize an empty table with Key-Value columns."""
        if self.main_table:
            self.ids.table_container.remove_widget(self.main_table)

        self.main_table = MDDataTable(
            size_hint=(1, 0.8),
            check=True,
            column_data=[
                ("Key", dp(DEFAULT_ROW_KEY_WIDTH)),
                ("Value", dp(DEFAULT_ROW_VALUE_WIDTH)),
            ],
            row_data=[],
            use_pagination=DEFAULT_USE_PAGINATION,
            rows_num=DEFAULT_NUM_ROWS_PAGE,
            pagination_menu_height=dp(300),  # Set dropdown menu height
        )
        
        self.ids.table_container.add_widget(self.main_table)
    
    def _get_json_files(self):
        """Retrieve available JSON files from a directory."""
        if not os.path.exists(PATH_FILE_STORAGE):
            os.makedirs(PATH_FILE_STORAGE)
        
        downloaded_files = os.listdir(PATH_FILE_STORAGE)
        return [f for f in downloaded_files if f.endswith(".json")]

    def on_enter(self):
        """Called when the screen is entered, ensuring UI is loaded before creating menu."""
        self._initialize_table()
        self.json_files = self._get_json_files()

        # Ensure menu is only created once after UI loads
        if self.menu is None:
            self.menu = self._create_menu()

    def _create_menu(self):
        """Create a dropdown menu with available JSON files."""
        if not hasattr(self.ids, "menu_button"):
            Logger.error("menu_button is missing in self.ids!")
            return None

        menu_items = [
            {
                "text": f,
                "viewclass": "OneLineListItem",
                "on_release": lambda x=f: self.load_json_data(x),
            }
            for f in self.json_files
        ]
        return MDDropdownMenu(
            caller=self.ids.menu_button,  # Now it will be available
            items=menu_items,
            width_mult=4,
        )
    
    def show_menu(self):
        """Display the dropdown menu."""
        self.menu.open()

    def load_json_data(self, filename):
        """Load data from the selected JSON file and update the table."""
        if filename == self.selected_file:
            #toast("Same file selected. No changes made.")
            MDSnackbar("Same file selected. No changes made.")
            return

        self.selected_file = filename
        file_path = os.path.join(PATH_FILE_STORAGE, filename)
        
        try:
            with open(file_path, "r") as f:
                data = json.load(f)
                self._update_table(data.get("data", {}))
        except Exception as e:
            Logger.error(f"Error loading JSON: {e}")
            #toast("Error loading file.")
            MDSnackbar("Error loading file.")

    def _update_table(self, data):
        """Update the table with new data."""
        self.main_table.row_data = []
        for key, value in data.items():
            self.main_table.add_row((key, str(value)))

    def on_enter(self):
        self._initialize_table()
        self.json_files = self._get_json_files()
        self.menu = self._create_menu()

    def go_to_fields_screen(self):
        self.manager.transition = SlideTransition(direction="left", duration=0.4)
        self.manager.current = SCREEN_NAME_FIELD