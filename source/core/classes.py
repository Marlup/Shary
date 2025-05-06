import logging
from kivy.uix.screenmanager import ScreenManager
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.screen  import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.datatables import MDDataTable
from kivymd.app import MDApp
from kivy.metrics import dp

from core.constant import (
    DEFAULT_NUM_ROWS_PAGE,
    DEFAULT_USE_PAGINATION,
)

class Utils():
    @staticmethod
    def remove_table(func):
        """Removes the table from 'table_container' layout."""
        def wrapper(self, *args, **kwargs):
            func_results = func(self, *args, **kwargs)
            self.ids.table_container.remove_widget(self.table)
            return func_results
        return wrapper

class EnhancedScreenManager(ScreenManager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_app(self):
        return MDApp.get_running_app()
    
    def get_manager(self):
        return self

class EnhancedMDScreen(MDScreen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_app(self):
        return MDApp.get_running_app()

class EnhancedTableMDScreen(EnhancedMDScreen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.main_table = None
        self.checked_rows = []
    
    def on_row_check(self, instance_table, current_row):
        """Manually track checked rows when checkboxes are clicked."""
        if current_row in self.checked_rows:
            self.checked_rows.remove(current_row)  # Uncheck → Remove from list
        else:
            self.checked_rows.append(current_row)  # Check → Add to list
        #logging.debug(f"Manually Tracked Checked Rows: {len(self.checked_rows)}")

    def _get_checked_rows(self) -> list[str]:
        # Avoid copy by reference
        return [] or self.checked_rows
    
    def _clear_checked_rows(self):
        self.checked_rows.clear()

    def _delete_rows(self) -> list[str]:
        checked_rows = self._get_checked_rows()
        if checked_rows is None:
            return
        
        rows_pk_keys = []
        for checked_row in checked_rows:
            logging.info(f"Row removed from table: {checked_row}")
            self.main_table.remove_row(tuple(checked_row))

            rows_pk_key = self._get_checked_cell(checked_row, 0, True)
            rows_pk_keys.append(rows_pk_key)
        
        self._clear_checked_rows()

        return rows_pk_keys
    
    def _get_checked_cell(self, row, index=0, cell_as_tuple=False) -> tuple[str] | None:
        # Return checked cell
        return (row[index], ) if cell_as_tuple else row[index]
    
    def _get_checked_cells(self, index=0, cell_as_tuple=False) -> list[tuple[str]] | None:
        rows = self._get_checked_rows()
        if not rows:
            return

        # Return checked cells
        return [self._get_checked_cell(r, index, cell_as_tuple) for r in rows]

    def _add_row(self, row_data):
        self.main_table.add_row(row_data)
    
    def _initialize_table(self, column_data, row_data=[]):
        if self.main_table:
            return
        
        self.main_table = MDDataTable(
            size_hint=(1, 0.8),
            pos_hint={"center_x": 0.5, "center_y": 0.5},  # Ensure centering
            check=True,
            column_data=column_data,
            row_data=row_data,
            use_pagination=DEFAULT_USE_PAGINATION,
            rows_num=DEFAULT_NUM_ROWS_PAGE,
            pagination_menu_height=dp(300),  # Set dropdown menu height
        )

        # Bind checkbox selection event
        self.main_table.bind(on_check_press=self.on_row_check)
        self.ids.table_container.add_widget(self.main_table)

class UserDialog(MDBoxLayout):
    pass

class RequestFieldDialog(MDBoxLayout):
    pass

class FieldDialog(MDBoxLayout):
    pass

class SendEmailDialog(MDBoxLayout):
    pass

class SelectChannel(MDBoxLayout):
    pass