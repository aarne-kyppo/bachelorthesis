from django import forms
from users.fields import UserNameField
from django.contrib.auth.models import User
import re

STATES = (
        ('d','disabled'),
        ('l','locked'),
        ('a','active')
    )

class UserForm(forms.Form):
    username = forms.CharField(widget=forms.HiddenInput)
    def __init__(self,*args,**kwargs):
        formfields = kwargs.pop('fields',{})
        super(UserForm,self).__init__(*args,**kwargs)
        for field in formfields:
            fieldobject = field['fieldobject']
            fieldname = field['name']
            self.fields[fieldname] = fieldobject
    
    
    def addField(self,initialvalue, field):
        self.fields[initialvalue] = field
    #localaccount = forms.CharField(widget=forms.HiddenInput)
    #mysql = forms.ChoiceField(choices=STATES)
    #svn = forms.ChoiceField(choices=STATES)
    #ssh = forms.ChoiceField(choices=STATES)
    #quota_hardlimit = forms.IntegerField()
    #quota_softlimit = forms.IntegerField()

class NewUserForm(UserForm):
    username = UserNameField()
    email = forms.EmailField()
    #mysql = forms.BooleanField(required=False,label="MySQL")
    #svn = forms.BooleanField(required=False,label="Subversion")
    #ssh = forms.BooleanField(required=False,label="SSH")
    #quota_softlimit = forms.IntegerField(label="Quota softlimit(MB)")
    #quota_hardlimit = forms.IntegerField(label="Quota hardlimit(MB)")

class ServiceForm(forms.Form):
    mysql = forms.BooleanField(required=False)
    svn = forms.BooleanField(required=False)
    ssh = forms.BooleanField(required=False)
    quota = forms.BooleanField(required=False)
    