from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.screen  import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout


class Utils():
    @staticmethod
    def remove_table(func):
        """Removes the table from 'table_container' layout."""
        def wrapper(self, *args, **kwargs):
            func_results = func(self, *args, **kwargs)
            self.ids.table_container.remove_widget(self.table)
            return func_results
        return wrapper

class EnhancedMDScreen(MDScreen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.checked_rows = []
    
    def on_row_check(self, instance_table, current_row):
        """Manually track selected rows when checkboxes are clicked."""
        if current_row in self.checked_rows:
            self.checked_rows.remove(current_row)  # Uncheck → Remove from list
        else:
            self.checked_rows.append(current_row)  # Check → Add to list
        #logging.debug(f"Manually Tracked Checked Rows: {len(self.checked_rows)}")

class UserDialog(MDBoxLayout):
    pass

class RequestFieldDialog(MDBoxLayout):
    pass

class FieldDialog(MDBoxLayout):
    pass

class SendEmailDialog(MDBoxLayout):
    pass

class SendToFirebaseDialog(MDBoxLayout):
    pass

class SelectChannel(MDBoxLayout):
    pass