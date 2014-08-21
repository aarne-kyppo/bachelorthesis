from servicebase import ServiceBase
from servicefield import ServiceField
from django import forms
from sh import ErrorReturnCode
from updatefunctions import updateStateField
from sh import chpasswd, usermod, useradd, chown
from users.models import Service
from django.contrib import messages

STATES = (
    ('d', 'disabled'),
    ('l', 'locked'),
    ('a', 'active')
)


class LocalAccount(ServiceBase):
    servicetype = 'localaccount'

    def __init__(self):
        self.fields = (
        ServiceField("OS account", "localaccount", self, forms.ChoiceField(choices=STATES), updateStateField,
                     forms.CharField(widget=forms.HiddenInput)),)

    def initServiceToUser(self, request, user):
        try:
            username = user.username
            homedirectory = '/home/%s' % (username)
            useradd(username, '-m')
            chown('-R', username, homedirectory)

        except ErrorReturnCode:
            messages.error(request,
                           "LocalAccountError: User creation failed. Check if user has sudo rights, that runs this application.")
            user.delete()
            return False
        local = LocalAccount()
        tmp = Service.objects.create(user=user, servicetype=local.getServiceType(), state='a')
        tmp.save()
        messages.success(request, "User is successfully created.")
        return True

    def lockServiceFromUser(self, request, user):
        try:
            usermod("-L", "-e", "1", user.username)
            print "sdfgdfg"
            local = LocalAccount()
            localservice = local.getServiceType()
            if localservice:
                tmp = Service.objects.get(user=user, servicetype=localservice)
                tmp.state = 'l'
                tmp.save()
                messages.success(request, "Localaccount of the user is locked.")
            else:
                messages.error(request, "Activate LocalAccount service first.")
        except ErrorReturnCode:
            messages.error(request, "LocalAccountError: Couldn't lock local user account.")

    def unlockServiceFromUser(self, request, user):
        try:
            usermod("-U", "-e", "99999", user.username)
            local = LocalAccount()
            localservice = local.getServiceType()
            if localservice:
                tmp = Service.objects.get(user=user, servicetype=localservice)
                tmp.state = 'a'
                tmp.save()
                messages.success(request, "Localaccount of the user is unlocked.")
        except ErrorReturnCode:
            messages.error(request, "LocalAccountError: Couldn't unlock local user account.")

    def resetUsersPassword(self, request, user, password):
        try:
            chpasswd(_in="%s:%s" % (user.username, password))
            messages.success(request, "Password for local user changed")
        except ErrorReturnCode:
            messages.error(request, "LocalAccountError: Couldn't change user's password")

    def disableServiceFromUser(self, request, user):
        try:

            username = user.username
            deluser(username)

            try:
                cd("/home")
                tar("cjf", "%s.tar.bz2" % (username), "%s/" % (username))

                try:
                    rm("-R", "/home/%s" % (username))
                except ErrorReturnCode:
                    messages.error(request, "LocalAccountError: Removing homedirectory failed.")
                    return False

            except ErrorReturnCode:
                messages.error(request, "LocalAccountError: Archiving homedirectory failed.")
                return False

        except ErrorReturnCode:
            messages.error(request, 'LocalAccountError: Failed to remove user.')
            return False
        local = LocalAccount()
        localaccount = Service.objects.get(user=user, servicetype=local.getServiceType())
        localaccount.delete()
        user.delete()
        messages.success(request, "User is successfully removed.")
        return True