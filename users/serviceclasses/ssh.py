from servicebase import ServiceBase
from servicefield import ServiceField
from django import forms
from updatefunctions import updateStateField
from django.conf import settings
from sh import ErrorReturnCode, gpasswd, groups
from django.contrib import messages
from users.models import Service
STATES = (
        ('d','disabled'),
        ('l','locked'),
        ('a','active')
    )
class Ssh(ServiceBase):
    servicetype = 'ssh'
    def __init__(self):
        self.fields = (ServiceField("SSH/SFTP","ssh",self,forms.ChoiceField(choices=STATES),updateStateField,forms.BooleanField(label="SSH/SFTP",initial=True)),)
    def initServiceToUser(self,request,user):
        sshgroup = settings.SSH_USER_GROUP
        try:
            gpasswd("-a",user.username,sshgroup)
            if self.getServiceType():
                tmp = Service.objects.create(user=user,servicetype=self.getServiceType(),state='a')
                messages.success(request,"SSH service initialized for user.")
                return True
            else:
                messages.error(request,"Activate SSH service first.")
                return False
        except ErrorReturnCode:
            messages.error(request,"SSHError: Couldn't add user to group of SSH users.")
            return False
    
    def lockServiceFromUser(self,request,user):
        sshgroup = settings.SSH_USER_GROUP
        groupsofuser = groups(user.username)
        user_not_in_ssh_group = False
        if sshgroup not in groupsofuser:
            messages.success(request,"SSH service already locked from user.")
            user_not_in_ssh_group = True
        try:
            if not user_not_in_ssh_group:
                gpasswd("-d",user.username,sshgroup)
            if self.getServiceType():
                tmp = Service.objects.get(user=user,servicetype=self.getServiceType())
                tmp.state = 'l'
                tmp.save()
                if not user_not_in_ssh_group:
                    messages.success(request,"SSH service locked from user.")
            else:
                messages.error(request,"Activate SSH service first.")
        except ErrorReturnCode:
            messages.error(request,"SSHError: Couldn't remove user from group of SSH users.")
    
    def unlockServiceFromUser(self,request,user):
        sshgroup = settings.SSH_USER_GROUP
        groupsofuser = groups(user.username)
        user_in_ssh_group = False
        if sshgroup in groupsofuser:
            messages.success(request,"SSH service already unlocked for user.")
            user_in_ssh_group = True
        try:
            if not user_in_ssh_group:
                gpasswd("-a",user.username,sshgroup)
            if self.getServiceType():
                tmp = Service.objects.get(user=user,servicetype=self.getServiceType())
                tmp.state = 'a'
                tmp.save()
                if not user_in_ssh_group:
                    messages.success(request,"SSH service unlocked for user.")
            else:
                messages.error(request,"Activate SSH service first.")
        except ErrorReturnCode:
            messages.error(request,"SSHError: Couldn't add user to group of SSH users.")
    
    def resetUsersPassword(self,request,user,password):
        pass
    
    def disableServiceFromUser(self,request,user):
        sshgroup = settings.SSH_USER_GROUP
        groupsofuser = groups(user.username)
        user_not_in_ssh_group = False
        if sshgroup not in groupsofuser:
            messages.success(request,"SSH service already disabled from user.")
            user_not_in_ssh_group = True
        try:
            if not user_not_in_ssh_group:
                gpasswd("-d",user.username,sshgroup)
            if self.getServiceType():
                tmp = Service.objects.get(user=user,servicetype=self.getServiceType())
                tmp.delete()
                if not user_not_in_ssh_group:
                    messages.success(request,"SSH service locked from user.")
            else:
                messages.error(request,"Activate SSH service first.")
        except ErrorReturnCode:
            messages.error(request,"SSHError: Couldn't remove user from group of SSH users.")