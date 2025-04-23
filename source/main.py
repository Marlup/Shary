# --- main.py ---

from kivy.core.window import Window

from app.app import SharyApp
from core.functions import resource_path

Window.icon = resource_path("assets/favicon.ico")


SharyApp().run()