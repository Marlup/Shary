# core/screen_factory.py

# Screens
from screens.fields_screen import FieldsScreen
from screens.user_creation_screen import UserCreationScreen
from screens.users_screen import UsersScreen
from screens.files_visualizer_screen import FilesVisualizerScreen
from screens.login_screen import LoginScreen
from screens.requests_screen import RequestsScreen

# Dependency inyection
from core.dependency_container import DependencyContainer

class ScreenFactory():
    @staticmethod
    def create_user_creation_screen():
        controller = DependencyContainer.get("controller")
        return UserCreationScreen(controller=controller)

    @staticmethod
    def create_fields_screen():
        controller = DependencyContainer.get("controller")
        return FieldsScreen(controller=controller)

    @staticmethod
    def create_users_screen():
        controller = DependencyContainer.get("controller")
        return UsersScreen(controller=controller)

    @staticmethod
    def create_login_screen():
        controller = DependencyContainer.get("controller")
        return LoginScreen(controller=controller)

    @staticmethod
    def create_files_visualizer_screen():
        controller = DependencyContainer.get("controller")
        return FilesVisualizerScreen(controller=controller)

    @staticmethod
    def create_requests_screen():
        controller = DependencyContainer.get("controller")
        return RequestsScreen(controller=controller)
