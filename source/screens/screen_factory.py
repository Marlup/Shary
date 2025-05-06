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
        session = DependencyContainer.get("session")
        security = DependencyContainer.get("security_service")
        cloud = DependencyContainer.get("cloud_service")

        return UserCreationScreen(session, security, cloud)

    @staticmethod
    def create_fields_screen():
        field = DependencyContainer.get("field_service")
        session = DependencyContainer.get("session")
        cloud = DependencyContainer.get("cloud_service")
        email = DependencyContainer.get("email_service")

        return FieldsScreen(field, session, email, cloud)

    @staticmethod
    def create_users_screen():
        user = DependencyContainer.get("user_service")
        session = DependencyContainer.get("session")

        return UsersScreen(user, session)

    @staticmethod
    def create_login_screen():
        session = DependencyContainer.get("session")
        security = DependencyContainer.get("security_service")
        cloud = DependencyContainer.get("cloud_service")

        return LoginScreen(session, security, cloud)

    @staticmethod
    def create_files_visualizer_screen():
        return FilesVisualizerScreen()

    @staticmethod
    def create_requests_screen():
        request = DependencyContainer.get("request_service")
        session = DependencyContainer.get("session")
        email = DependencyContainer.get("email_service")

        return RequestsScreen(request, session, email)
