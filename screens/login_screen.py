# --- source/login_screen.py ---

from kivy.uix.screenmanager import Screen
from kivy.utils import platform
from kivymd.uix.snackbar import MDSnackbar
from kivymd.uix.label import MDLabel
from kivy.clock import Clock
from kivy.logger import Logger


from controller.app_controller import AppController

from core.constant import SCREEN_NAME_LOGIN

from core.session import CurrentSession

if platform == "android":
    from jnius import autoclass
    PythonActivity = autoclass("org.kivy.android.PythonActivity")
    Context = autoclass("android.content.Context")
else:
    print("Running on non-Android platform.")

FINGERPRINT_AVAILABLE = False

class LoginScreen(Screen):
    def __init__(self, controller: AppController, **kwargs):
        super().__init__(name=SCREEN_NAME_LOGIN, **kwargs)
        
        self.controller = controller
        self.session: CurrentSession = CurrentSession.get_instance()

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

    def check_login(self):
        # Get credentials from UI
        username = self._get_ui_username()
        password = self._get_ui_password()

        # Try login
        login_succesful = self.session.try_login(username, password)

        if login_succesful:
            Logger.info(f"User logged-in by input credentials.")

            # Load cryptographic keys
            self.session.load_cryptographic_keys()
            
            # Remove the user creation screen after successful registration
            self._load_other_screens()

            # Remove the login screen after validating credentials and 
            # pressing the login button
            self._go_to_fields_screen()
        else:
            MDSnackbar("Invalid credentials").open()
    
    # TODO Bring the logic to session class
    def biometric_auth(self):
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

        # todo remove next 3 lines as they are meant to be used for testing
        self._load_other_screens()    
        # Load cryptographic keys
        self.session.load_cryptographic_keys()
        Clock.schedule_once(lambda _: self._go_to_fields_screen(), 1)
        
        Logger.info(f"Entered biometrics mode.")
        Logger.info(f"User logged-in by input biometrics.")

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

                Logger.info(f"User logged-in by input biometrics.")

                # Load cryptographic keys
                self.session.load_cryptographic_keys()

                # Remove the login screen after validating credentials and 
                # pressing the login button
                self._go_to_fields_screen()
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
    
    #  ----- UI entrypoints -----
    # UI Getters
    def _get_ui_username(self) -> str:
        return self.ids.username_input.text.strip()

    def _get_ui_password(self) -> str:
        return self.ids.password_input.text.strip()

    # Screen Manager
    def _load_other_screens(self):
        self.manager.load_other_screens()
    
    def _go_to_fields_screen(self):
        self.manager.go_to_fields_screen("left")

    # callbacks current screen events
    def on_leave(self):
        # Load the services
        #self.manager.load_services()
        pass