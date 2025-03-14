# --- source/login_screen.py ---
import os
from dotenv import load_dotenv
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen
#from kivymd.toast import toast
from kivymd.uix.snackbar import MDSnackbar
from kivy.utils import platform

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

    def focus_next_mdtextfield(self):
        if self.manager.current != 'login':
            return

        focused_widget = next((w for w in self.children if getattr(w, 'focus', False)), None)
        if focused_widget:
            current_index = self.children.index(focused_widget)
            next_index = (current_index + 1) % len(self.children)
        else:
            next_index = 0

        if hasattr(self.children[next_index], 'focus'):
            self.children[next_index].focus = True

    def check_login(self, instance):
        username = self.ids.username_input.text.strip()
        password = self.ids.password_input.text.strip()

        if username == os.getenv("SHARY_ROOT_USERNAME") and password == os.getenv("SHARY_ROOT_PASSWORD"):
            # Remove the login screen after validating credentials and 
            # pressing the login button
            self.manager.current = "field"
        else:
            #toast("Invalid credentials")
            MDSnackbar("Invalid credentials").open()
            pass

    def biometric_auth(self, instance):
        self.manager.current = "field"
        
        if FINGERPRINT_AVAILABLE:
            activity = PythonActivity.mActivity
            keyguard_manager = activity.getSystemService(Context.KEYGUARD_SERVICE)
            if keyguard_manager.isKeyguardSecure():
                #toast("Biometric authentication successful")
                MDSnackbar("Biometric authentication successful").open()
                # Remove the login screen after validating biometrical-credentials and 
                # pressing the login button
                self.manager.current = "field"
            else:
                #toast("Biometric authentication failed or not set up")
                MDSnackbar("Biometric authentication failed or not set up").open()
                pass
        else:
            #toast("Biometric authentication not available on this device")
            MDSnackbar("Biometric authentication not available on this device").open()
            pass

    def on_enter(self):
        load_dotenv(".env")

def get_login_screen():
    Builder.load_file("widget_schemas/login.kv")
    return LoginScreen()
