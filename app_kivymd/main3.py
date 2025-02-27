from kivy.metrics import dp
from kivymd.app import MDApp
from kivymd.uix.datatables import MDDataTable
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.button import MDRaisedButton


class SelectableTableApp(MDApp):
    data_tables = None

    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Orange"

        layout = MDFloatLayout()  # root layout
        # Creating control buttons.
        button_box = MDBoxLayout(
            pos_hint={"center_x": 0.5, "y": 0.05},
            adaptive_size=True,
            padding="24dp",
            spacing="24dp",
        )

        button_box.add_widget(
            MDRaisedButton(
                text="Add row", on_release=self.add_row
            )
        )
        button_box.add_widget(
            MDRaisedButton(
                text="Delete Selected", on_release=self.delete_selected_rows
            )
        )

        # Create a table with selectable rows.
        self.data_tables = MDDataTable(
            pos_hint={"center_y": 0.5, "center_x": 0.5},
            size_hint=(0.9, 0.6),
            use_pagination=False,
            check=True,  # Enable row selection with checkboxes
            column_data=[
                ("No.", dp(30)),
                ("Column 1", dp(40)),
                ("Column 2", dp(40)),
                ("Column 3", dp(40)),
            ],
            row_data=[("1", "1", "2", "3")],
        )
        self.data_tables.bind(on_check_press=self.on_check_press)

        # Adding a table and buttons to the root layout.
        layout.add_widget(self.data_tables)
        layout.add_widget(button_box)

        return layout

    def add_row(self, instance) -> None:
        """Add a new row to the data table."""
        last_num_row = int(self.data_tables.row_data[-1][0]) if self.data_tables.row_data else 0
        self.data_tables.add_row((str(last_num_row + 1), "1", "2", "3"))

    def delete_selected_rows(self, instance) -> None:
        """Delete selected rows from the data table."""
        print(f"self.data_tables.get_row_checks() - {self.data_tables.get_row_checks()}")
        selected_rows = [
            row for row in self.data_tables.get_row_checks()
        ]
        print(f"selected_rows - {selected_rows}")
        selected_rows
        for row in selected_rows:
            self.data_tables.remove_row(tuple(row))
        
        

    def on_check_press(self, table_instance, row_data):
        print(f"\nrow_data - {row_data[0]}")
        print(f"table_instance.get_row_checks() - {table_instance.get_row_checks()}")

    def on_row_press(self):
        print(self)

if __name__ == "__main__":
    SelectableTableApp().run()
