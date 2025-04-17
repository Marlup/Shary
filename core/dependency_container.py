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
        from services.cloud_service import CloudService
        from services.email_service import EmailService
        from controller.app_controller import AppController

        # Services
        cloud = CloudService()
        email = EmailService()
        
        cls.register("cloud", cloud)
        cls.register("email", email)
        
        # Controller
        controller: AppController = AppController(cloud, email)
        
        cls.register("controller", controller)
