# core/dependency_container.py

class DependencyContainer:
    _services = {}

    @classmethod
    def register(cls, name, instance):
        cls._services[name] = instance

    @classmethod
    def get(cls, name):
        return cls._services[name]

    @classmethod
    def init_all(cls):
        from core.session import Session

        from services.security_service import SecurityService
        from services.cloud_service import CloudService
        from services.field_service import FieldService
        
        from services.user_service import UserService
        from services.request_service import RequestService
        from services.email_service import EmailService

        from repositories.user_repository import UserRepository
        from repositories.field_repository import FieldRepository
        from repositories.request_repository import RequestRepository
        
        from controller.app_controller import AppController

        # Security
        security = SecurityService()

        # Session
        session = Session(security)
        cls.register("session", session)

        # Repository Services
        field = FieldService(FieldRepository(), security)
        user = UserService(UserRepository())
        request = RequestService(RequestRepository())

        cls.register("field_service", field)
        cls.register("user_service", user)
        cls.register("request_service", request)

        # Action Services
        cloud = CloudService(security)
        email = EmailService(session)

        cls.register("security_service", security)
        cls.register("cloud_service", cloud)
        cls.register("email_service", email)
        
        # Controller
        controller: AppController = AppController(session, security, cloud, email)
        
        cls.register("controller", controller)
