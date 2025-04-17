import os
import json

from kivy.metrics import dp
from kivy.uix.screenmanager import SlideTransition
from kivy.logger import Logger
from kivymd.uix.screen import MDScreen
from kivymd.uix.datatables import MDDataTable
from kivymd.uix.snackbar import MDSnackbar
from kivymd.uix.menu import MDDropdownMenu

from controller.app_controller import AppController
from core.functions import (
    get_json_files,
)

from core.constant import (
    DEFAULT_ROW_KEY_WIDTH,
    DEFAULT_ROW_VALUE_WIDTH,
    DEFAULT_NUM_ROWS_PAGE,
    DEFAULT_USE_PAGINATION,
    PATH_DATA_DOWNLOAD,
    SCREEN_NAME_FILES_VISUALIZER,
)

class FilesVisualizerScreen(MDScreen):
    def __init__(self, controller: AppController, **kwargs):
        super().__init__(name=SCREEN_NAME_FILES_VISUALIZER, **kwargs)
        self.controller = controller

        self.main_table = None
        self.dialog = None
        self.selected_file = None
        self.json_files = get_json_files()
        self.menu = None  # Don't create menu here!
    
    def show_menu(self):
        """Display the dropdown menu."""
        self.menu.open()

    def load_json_data(self, filename):
        """Load data from the selected JSON file and update the table."""
        # Check whether same file was selected
        if filename == self.selected_file:
            MDSnackbar("Same file selected. No changes made.")
            return
        self.selected_file = filename

        path_current_file = os.path.join(PATH_DATA_DOWNLOAD, filename)
        try:
            with open(path_current_file, "r") as f:
                data: dict = json.load(f)
                self._update_table(data.get("data", {}))

        except Exception as e:
            Logger.error(f"Error loading JSON: {e}")
            MDSnackbar("Error loading file.")

    # Screen transitions
    def go_to_fields_screen(self):
        self.manager.go_to_fields_screen("left")

    # Screens callback
    def on_enter(self):
        """Called when the screen is entered, ensuring UI is loaded before creating menu."""
        self._initialize_table()
        self.json_files = get_json_files()

        # Ensure menu is only created once after UI loads
        if self.menu is None:
            self.menu = self._create_menu()

    def on_leave(self):
        self.selected_file = ""

    # ----- Internal methods -----
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
    
    def _update_table(self, data: dict):
        """Update the table with new data."""
        self.main_table.row_data = []
        for key, value in data.items():
            self.main_table.add_row((key, str(value)))