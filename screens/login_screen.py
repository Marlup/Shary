# --- source/login_screen.py ---

from kivy.uix.screenmanager import Screen
from kivy.utils import platform
from kivymd.uix.snackbar import MDSnackbar
from kivymd.uix.label import MDLabel
from kivy.clock import Clock
import keyring
import bcrypt

from core.constant import SCREEN_NAME_LOGIN

from core.dtos import OwnerDTO

if platform == "android":
    from jnius import autoclass
    PythonActivity = autoclass("org.kivy.android.PythonActivity")
    Context = autoclass("android.content.Context")
else:
    print("Running on non-Android platform.")

FINGERPRINT_AVAILABLE = False

class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(name=SCREEN_NAME_LOGIN, **kwargs)

    def focus_next_mdtextfield(self):
        if self.manager.current != SCREEN_NAME_LOGIN:
            return

        focused_widget = next((w for w in self.children if getattr(w, "focus", False)), None)
        if focused_widget:
            current_index = self.children.index(focused_widget)
            next_index = (current_index + 1) % len(self.children)
        else:
            next_index = 0

        if hasattr(self.children[next_index], "focus"):
            self.children[next_index].focus = True

    def check_login(self, instance):
        username = self.ids.username_input.text.strip()
        password = self.ids.password_input.text.strip()
        
        stored_username = keyring.get_password("shary_app", "owner_username")
        stored_safe_password = keyring.get_password("shary_app", "owner_safe_password")
        safe_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        
        if username == stored_username \
        and safe_password == stored_safe_password:
            # Remove the user creation screen after successful registration
            self._load_other_screens()

            # Remove the login screen after validating credentials and 
            # pressing the login button
            self._go_to_field_screen()
        else:
            #toast("Invalid credentials")
            MDSnackbar("Invalid credentials").open()
            pass

        # Load super user
        self._get_owner()

    def biometric_auth(self, instance):
        # Remove the user creation screen after successful registration
        
        MDSnackbar(
            MDLabel(
                text="Biometric authentication successful",
                theme_text_color="Custom",
                text_color=(1, 1, 1, 1),
                text_size=(self.width, None),  # make it wrap
                ),
            size_hint_x=None,
            width="280dp",
            pos_hint={"center_x": 0.5},
            y="40dp"
        ).open()

        self._load_other_screens()    
        Clock.schedule_once(lambda _: self.go_field_screen(), 1)

        if FINGERPRINT_AVAILABLE:
            activity = PythonActivity.mActivity
            keyguard_manager = activity.getSystemService(Context.KEYGUARD_SERVICE)
            if keyguard_manager.isKeyguardSecure():
                MDSnackbar(
                    MDLabel(
                        text="Biometric authentication successful",
                        theme_text_color="Custom",
                        text_color=(1, 1, 1, 1),
                    ),
                    size_hint_x=None,
                    width="280dp",
                    pos_hint={"center_x": 0.5},
                    y="40dp",
                ).open()

                # Remove the login screen after validating biometrical-credentials and 
                # pressing the login button
                self._go_to_field_screen()
            else:
                MDSnackbar(
                    MDLabel(
                        text="Biometric authentication failed or not set up",
                        theme_text_color="Custom",
                        text_color=(1, 1, 1, 1),
                        ),
                        size_hint_x=None,
                        width="280dp",
                        snackbar_x="20dp",
                        snackbar_y="40dp"
                        ).open()
                pass
        else:
            #MDSnackbar("Biometric authentication not available on this device").open()
            pass

        # Load super user
        self._get_owner()
    
    def _load_other_screens(self):
        self.manager.load_other_screens()
    
    def _go_to_field_screen(self):
        self.manager.go_to_field_screen("left")

    def _get_owner(self):
        self.manager.get_owner()

    def _set_owner(self, username, email, safe_password):
        self.manager.set_owner(username, email, safe_password)

    def on_leave(self):
        # Load the services
        self.manager.load_services()
        