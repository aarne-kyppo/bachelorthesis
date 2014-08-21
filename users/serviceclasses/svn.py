from servicebase import ServiceBase
from servicefield import ServiceField
from updatefunctions import updateStateField
from django import forms
STATES = (
        ('d','disabled'),
        ('l','locked'),
        ('a','active')
    )
class Svn(ServiceBase):
    servicetype = "svn"
    def __init__(self):
        self.fields = (ServiceField("SVN","svn",self,forms.ChoiceField(choices=STATES),updateStateField,forms.BooleanField(label="SVN")),)
    def initServiceToUser(self,request,user):
        pass
    
    def lockServiceFromUser(self,request,user):
        pass
    
    def unlockServiceFromUser(self,request,user):
        pass
    
    def resetUsersPassword(self,request,user,password):
        pass
    
    def disableServiceFromUser(self,request,user):
        pass