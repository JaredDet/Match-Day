import injector

from core.dependencies import CoreModule

injector_instance = injector.Injector([CoreModule()], auto_bind=False)
