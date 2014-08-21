from abc import ABCMeta, abstractmethod
from django.core.exceptions import ObjectDoesNotExist
from users.models import ServiceType, Service
from django.db import connection
from django.conf import settings
class ServiceBase:
    __metaclass__ = ABCMeta
    servicetype = None #For getUserDataFields. Form field instance. Used to build form in views.py getUsers()-method
    fields = None #For getUserDataFields. Form field instance. Used to build form in views.py getUsers()-method
    
    def initService(self):
        if not self.serviceTypeExists():
            tmp = ServiceType.objects.create(name=self.type)
            tmp.save()
        return True
    
    @abstractmethod
    def initServiceToUser(self,request,user,kw):
        pass
    
    @abstractmethod
    def lockServiceFromUser(self,request,user):
        pass
    
    @abstractmethod
    def unlockServiceFromUser(self,request,user):
        pass
    
    @abstractmethod
    def disableServiceFromUser(self,request,user):
        pass
    
    @abstractmethod
    def resetUsersPassword(self,request,user,password):
        pass
    
    def serviceTypeExists(self):#POISTA
        cur = connection.cursor()
        cur.execute("USE %s" % (settings.DATABASES['default']['NAME']))
        return ServiceType.objects.filter(name=self.servicetype).exists()
    
    def getServiceType(self):#POISTA
        if self.serviceTypeExists():
            return ServiceType.objects.get(name=self.servicetype)
        return None
    
    def hasUserThisService(self,user):#POISTA
        state = user.service_set.filter(servicetype=self.getServiceType()).exists()
        return state
    def getServiceOfUser(self,user,fieldname=None): #If many fields like in quota. Don't use this. Implement this function to serviceclass that you are making.
        try:
            servicetypeobject = ServiceType.objects.get(name=self.servicetype)
            service = user.service_set.get(servicetype=servicetypeobject)
        except ObjectDoesNotExist:
            return 'd'
        return service.state
    
    def getUserDataFields(self,user): #If many fields like in quota. Don't use this. Implement this function to serviceclass that you are making.
        value = self.getServiceOfUser(user)
        if not value:
            value = 'd'
        return [[self.servicetype,value]]
    
    def deleteService(self):
        if self.serviceTypeExists():
            ServiceType.objects.get(name=self.servicetype).delete()
    
    def toggleService(self):#POISTA TILALLE UPDATESERVICE()
        if self.serviceTypeExists():
            self.deleteService()
        else:
            self.initService()
    def update(self,request,user,fieldname,value,**kw):
        if fieldname not in [field.name for field in self.fields]:
            return None
        for field in self.fields:
            if fieldname is field.name:
                if 'newuser' in kw.keys():
                    field.update(request,user,None,value,newuser=True)
                else:
                    field.update(request,user,self.getServiceOfUser(user,fieldname),value)
                return None