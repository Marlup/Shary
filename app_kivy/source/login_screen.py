import os
from dotenv import load_dotenv
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivymd.uix.textfield import MDTextField
from kivy.uix.label import Label
from kivymd.toast import toast
from kivy.utils import platform
from kivy.core.window import Window

load_dotenv(".env")

if platform == 'android':
    from jnius import autoclass
    PythonActivity = autoclass('org.kivy.android.PythonActivity')
    Context = autoclass('android.content.Context')
else:
    print("Running on non-Android platform.")

FINGERPRINT_AVAILABLE = False


class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(name="login", **kwargs)
        self.build_ui()

    def build_ui(self):
        layout = BoxLayout(orientation="vertical", padding=20, spacing=20)

        self.label = Label(text="Shary Login", halign="center")
        self.username_input = MDTextField(hint_text="Username", multiline=False)
        self.password_input = MDTextField(hint_text="Password", password=True, multiline=False)

        self.login_button = Button(text="Login", on_release=self.check_login)
        self.biometric_button = Button(text="Use Fingerprint", on_release=self.biometric_auth)

        # ✅ Widgets added in tab order (Only MDTextFields)
        self.widgets_list = [self.username_input, self.password_input]

        # Adding widgets to layout
        layout.add_widget(self.label)
        layout.add_widget(self.username_input)
        layout.add_widget(self.password_input)
        layout.add_widget(self.login_button)
        if FINGERPRINT_AVAILABLE:
            layout.add_widget(self.biometric_button)

        self.add_widget(layout)


    def focus_next_mdtextfield(self):
        """Cycle focus between MDTextFields only."""
        if self.manager.current != 'login':  # Ensure you're on the correct screen
            return

        focused_widget = next((w for w in self.widgets_list if getattr(w, 'focus', False)), None)
        if focused_widget:
            current_index = self.widgets_list.index(focused_widget)
            next_index = (current_index + 1) % len(self.widgets_list)
        else:
            next_index = 0

        # ✅ Set focus to the next MDTextField
        if hasattr(self.widgets_list[next_index], 'focus'):
            self.widgets_list[next_index].focus = True

    def check_login(self, instance):
        """Check credentials and navigate if valid."""
        username = self.username_input.text.strip()
        password = self.password_input.text.strip()

        if username == os.getenv("SHARY_USERNAME") and password == os.getenv("SHARY_PASSWORD"):
            self.manager.current = "fields"
        else:
            toast("Invalid credentials")

    def biometric_auth(self, instance):
        """Simulated biometric authentication handler."""
        if FINGERPRINT_AVAILABLE:
            activity = PythonActivity.mActivity
            keyguard_manager = activity.getSystemService(Context.KEYGUARD_SERVICE)
            if keyguard_manager.isKeyguardSecure():
                toast("Biometric authentication successful")
                self.manager.current = "fields"
            else:
                toast("Biometric authentication failed or not set up")
        else:
            toast("Biometric authentication not available on this device")

    def on_key_down(self, window, key, scancode, codepoint, modifier):
        """Handle Tab and Enter key behaviors."""
        if key == 9:  # Tab key     
            self.focus_next_mdtextfield()
            return True
        elif key == 13:  # Enter key
            self.check_login(None)
            return True
        return False

    def on_enter(self):
        """Bind key event when this screen becomes active."""
        print(f"Screen '{self.name}' active: Key events bound.")
        Window.bind(on_key_down=self.on_key_down)

    def on_leave(self):
        """Unbind key event when leaving this screen."""
        print(f"Screen '{self.name}' inactive: Key events unbound.")
        Window.unbind(on_key_down=self.on_key_down)

def get_login_screen():
    """Returns the login screen instance."""
    return LoginScreen()
