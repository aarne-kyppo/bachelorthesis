__all__ = ['services', 'ssh', 'servicebase', 'mysql']
import pyclbr
import inspect
from servicebase import ServiceBase
from . import *
import os, sys


def getServices(servicecl):
    """
    Getting available services. At first classes of this package are imported.
    """
    path = os.path.dirname(os.path.abspath(__file__))
    for module in [f[:-3] for f in os.listdir(path) if f.endswith('.py') and f != '__init__.py']:
        mod = __import__('.'.join([__name__, module]), fromlist=[module])
        classes = [getattr(mod, x) for x in dir(mod)]
        for cls in classes:
            try:
                if issubclass(cls, ServiceBase) and inspect.isclass(ServiceBase):
                    print cls
                    setattr(sys.modules[__name__], cls.__name__, cls)
            except TypeError:
                pass

    services = inspect.getmembers(servicecl, inspect.isclass)
    filteredservices = [service[1] for service in services if service[0] is not "ServiceBase"]
    return filteredservices