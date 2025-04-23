from kivy.metrics import dp
from kivy.logger import Logger
from kivymd.uix.snackbar import MDSnackbar
from kivymd.uix.menu import MDDropdownMenu

from core.functions import (
    get_json_files,
    load_file_of_fields,
    check_new_json_files
)

from core.classes import (
    EnhancedTableMDScreen
)

from core.constant import (
    DEFAULT_ROW_KEY_WIDTH,
    DEFAULT_ROW_VALUE_WIDTH,
    SCREEN_NAME_FILES_VISUALIZER,
)

class FilesVisualizerScreen(EnhancedTableMDScreen):
    def __init__(self, **kwargs):
        super().__init__(name=SCREEN_NAME_FILES_VISUALIZER, **kwargs)

        self.dialog = None
        self.selected_file = ""
        self.json_files = []
        self.menu = None  # Don't create menu here!
    
    def show_menu(self):
        """Display the dropdown menu."""
        self.menu.open()

    def update_table_from_file(self, filename):
        """Load data from the selected JSON file and update the table."""
        # Check whether same file was selected
        if filename == self.selected_file:
            MDSnackbar("Same file selected. No changes made.")
            return

        self.selected_file = filename
        try:
            raw_data: dict[str, str] = load_file_of_fields(filename)
            data = raw_data.get("data", {})

            self._update_table(data)
        except Exception as e:
            Logger.error(f"Error loading JSON: {e}")
            MDSnackbar("Error loading file.")

    # Screen transitions
    def go_to_fields_screen(self):
        self.manager.go_to_fields_screen("left")

    # Screens callback
    def on_enter(self):
        """Called when the screen is entered, ensuring UI is loaded before creating menu."""
        self._initialize_empty_table()
        if check_new_json_files(self.json_files):
            self.json_files = get_json_files()

        # Ensure menu is only created once after UI loads
        if self.menu is None:
            self.menu = self._create_menu()

    def on_leave(self):
        self.selected_file = ""

    # ----- Internal methods -----
    def _initialize_empty_table(self):
        """Initialize an empty table with Key-Value columns."""
        
        column_data = [
            ("Key", dp(DEFAULT_ROW_KEY_WIDTH)),
            ("Value", dp(DEFAULT_ROW_VALUE_WIDTH)),  # Wider column
            ]
        
        self._initialize_table(column_data)

    def _create_menu(self):
        """Create a dropdown menu with available JSON files."""
        if not hasattr(self.ids, "menu_button"):
            Logger.error("menu_button is missing in self.ids!")
            return None

        menu_items = [
            {
                "text": f,
                "viewclass": "OneLineListItem",
                "on_release": lambda x=f: self.update_table_from_file(x),
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