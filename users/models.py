from django.db import models
from django.contrib.auth.models import User

class ServiceType(models.Model):
    STATES = (
        ('a','active'),
        ('d','disabled')
    )
    name = models.CharField(max_length=20)
    state = models.CharField(max_length=1,choices=STATES)

class Service(models.Model):
    STATES = (
        ('a','active'),
        ('l','locked')
    )
    servicetype = models.ForeignKey(ServiceType)
    user = models.ForeignKey(User)
    state = models.CharField(max_length=1, choices=STATES)
    
class Quota(Service):
    hardlimit = models.FloatField()
    softlimit = models.FloatField()