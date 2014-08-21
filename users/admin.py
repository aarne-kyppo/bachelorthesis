from django.contrib import admin
from users.models import ServiceType, Service, Quota

admin.site.register(ServiceType)
admin.site.register(Service)
admin.site.register(Quota)