from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.db import connection

from users.serviceclasses.services import sendInfoMaterial
from users.forms import NewUserForm, UserForm, ServiceForm
from users.models import Service, ServiceType, Quota

from MySQLdb import IntegrityError

import re
import sys
import subprocess
import os
import sh
import string
import random
from users.serviceclasses import getServices as getAllServices
from users import serviceclasses
from sh import userdel, useradd, cd, ErrorReturnCode, tar, rm, chpasswd, touch, chown, mv, mysqldump


def index(request):
    if not request.user.is_authenticated():
        return render(request, 'users/login.html', {})
    else:
        errors = messages.get_messages(request)
        erroruser = None
        user = None
        for error in errors:
            user = error
        if 'erroruser' in request.session:
            erroruser = request.session['erroruser']
            del request.session['erroruser']
            messages.error(request, "Fix values")
        data, headers = getUsers(erroruser)
        print "headers: {}".format(headers)

        return render(request, 'users/index.html', {'users': data, 'erroruser': user, 'headers': headers})


def logout_function(request):
    logout(request)
    return HttpResponseRedirect("/")


def getUsers(erroruser=None):
    errorusername = None
    if erroruser:
        print "ErrorUser: " + str(erroruser)
        errorusername = erroruser['username'].value()
    services = getAllServices(serviceclasses)
    servicetypes = ServiceType.objects.all()
    data = []
    formheaders = {}
    if erroruser:
        if 'username' in erroruser.cleaned_data:
            erroruser_username = erroruser.cleaned_data['username']
    else:
        erroruser_username = None
    if len(servicetypes) > 0:
        users = User.objects.all()
        formfields = getFields()
        formheaders = [field['header'] for field in formfields]
        formheaders.insert(0, 'Username')
        for i, user in enumerate(users):
            if erroruser and errorusername == user.username:
                print user.username
                form = erroruser
            else:
                formdata = {}
                formdata['username'] = user
                for service in services:
                    service = service()
                    print "ServiceType" + str(service.servicetype)
                    fields = service.getUserDataFields(user)
                    if fields:
                        for i, field in enumerate(fields):
                            fieldtitle = field[0]
                            value = field[1]
                            formdata[fieldtitle] = value
                form = UserForm(formdata, fields=formfields)
                print formdata
            # print form.as_table()
            data.append(form)

    return data, formheaders


def getFields(newuser=False):
    services = getAllServices(serviceclasses)
    formfields = []
    for service in services:
        service = service()
        for field in service.fields:
            if newuser:
                formfield = field.newuserfield if hasattr(field, 'newuserfield') else field.field
            else:
                formfield = field.field
            field_dict = {'name': field.name, 'fieldobject': formfield, 'header': field.header}
            formfields.append(field_dict)
    return formfields


def login_function(request):
    if request.method == "POST":
        username = request.POST['username']
        passwd = request.POST['password']
        print "salasana on     " + str(passwd)
        if username and passwd:
            user = authenticate(username=username, password=passwd)
            if user != None:
                login(request, user)
                return HttpResponseRedirect("/")
            else:
                errormsg = "Username or password is incorrect."
                return render(request, 'users/login.html',
                              {"error": errormsg})  # Inform user to insert correct login details
        else:
            errormsg = "Username or password is not given."
            return render(request, 'users/login.html', {"error": errormsg})  # Inform user to fill all fields
    return HttpResponseRedirect("/")


@login_required
def reset_password(request, userid):
    errormsg = None
    successmsg = None
    username = get_user_by_id(int(userid))
    if username:
        errormsg, password = set_password_for_user(username)
        if not errormsg:
            successmsg = "Password has been successfully reset."
    else:
        errormsg = "No such user."
    return redirect("/", {'success': successmsg, 'error': errormsg})


@login_required
def deleteuser(request):
    if request.method == 'POST':
        username = request.POST['username']
        user = User.objects.get(username=username)
        services = Service.objects.filter(user=user)
        servicenames = []
        for service in services:
            servicenames.append(service.servicetype.name)
        if 'mysql' in servicenames:
            mysql = MySQL()
            mysql.disableServiceFromUser(request, user)
        if 'ssh' in servicenames:
            ssh = Ssh()
            ssh.disableServiceFromUser(request, user)
        if 'svn' in servicenames:
            svn = Svn()
            svn.disableServiceFromUser(request, user)
        if 'localaccount' in servicenames:
            local = LocalAccount()
            local.disableServiceFromUser(request, user)
    return redirect("/")


@login_required
def resetpasswords(request):
    if request.method == 'POST':
        try:
            user = User.objects.get(username=request.POST["username"])

        except ObjectDoesNotExist:
            addError(request, "Couldn't find user %s" % (data['username']))
            return redirect("/")

        newpassword = generate_password(8)
        services = [service() for service in getAllServices(serviceclasses)]
        for service in services:
            if service.hasUserThisService(user):
                service.resetUsersPassword(request, user, newpassword)
        services = None

        sendInfoMaterial(None, "Your passwords have been reseted", user, password=newpassword)
    return redirect("/")


@login_required
def lockuser(request):
    if request.method == 'POST':
        username = request.POST['username']
        user = User.objects.get(username=username)
        services = Service.objects.filter(user=user)
        servicenames = []
        for service in services:
            servicenames.append(service.servicetype.name)
        if 'mysql' in servicenames:
            mysql = MySQL()
            mysql.lockServiceFromUser(request, user)
        if 'ssh' in servicenames:
            ssh = Ssh()
            ssh.lockServiceFromUser(request, user)
        if 'svn' in servicenames:
            svn = Svn()
            svn.lockServiceFromUser(request, user)
        if 'localaccount' in servicenames:
            local = LocalAccount()
            local.lockServiceFromUser(request, user)
    return redirect("/")


@login_required
def unlockuser(request):
    if request.method == 'POST':
        username = request.POST['username']
        user = User.objects.get(username=username)
        services = Service.objects.filter(user=user)
        servicenames = []
        for service in services:
            servicenames.append(service.servicetype.name)
        if 'mysql' in servicenames:
            mysql = MySQL()
            mysql.unlockServiceFromUser(request, user)
        if 'ssh' in servicenames:
            ssh = Ssh()
            ssh.unlockServiceFromUser(request, user)
        if 'svn' in servicenames:
            svn = Svn()
            svn.unlockServiceFromUser(request, user)
        if 'localaccount' in servicenames:
            local = LocalAccount()
            local.unlockServiceFromUser(request, user)
    return redirect("/")


def get_user_by_id(id):
    users = os.popen("awk -F : '{ if ($3 >= 1000) print $1,$3}' /etc/passwd").readlines()
    userarray = []
    for user in users:
        details = user[:-1].split(' ')
        print details
        if int(details[1]) == id:
            return str(details[0])
    return ""


@login_required
def confirm(request, username):
    return render(request, "users/confirm.html", {'user': username})


@login_required
def createuser(request):
    password = None
    if request.method == 'POST':
        form = NewUserForm(request.POST)
        if form.is_valid():

            username = form.cleaned_data['username']
            email = form.cleaned_data['email']

            password = generate_password(8)
            newuser = User.objects.create_user(username, email, password)

            data = form.cleaned_data
            del data['email']
            del data['username']
            services = [service() for service in getAllServices(serviceclasses)]
            for k, v in data.items():
                for service in services:
                    service.update(request, newuser, k, v)
                    service.resetUsersPassword(request, newuser, password)

            return redirect("/")

    else:
        form = NewUserForm(fields=getFields(True))
    return render(request, 'users/newuser.html', {'form': form})


def generate_password(size):
    chars = string.ascii_letters + string.digits
    password = ''.join(random.choice(chars) for x in range(size))
    return password


@login_required
def modify_user(request):
    data = None
    if request.method == 'POST':
        form = UserForm(request.POST, fields=getFields())

        if form.is_valid():

            data = form.cleaned_data
            print data

            try:
                user = User.objects.get(username=data['username'])

            except ObjectDoesNotExist:
                addError(request, "Couldn't find user %s" % (data['username']))
                return redirect("/")
            services = [service() for service in getAllServices(serviceclasses)]
            for key, value in data.items():
                for service in services:
                    service.update(request, user, key, value)
            services = None

            # #MySQL operations
            # service = MySQL()
            #new_state = data['mysql']
            #try:
            #    previous_state = user.service_set.filter(user=user,servicetype=service.getServiceType())
            #    if previous_state:
            #        prev_state = previous_state[0].state
            #    else:
            #        prev_state = 'd'
            #except ObjectDoesNotExist:
            #    prev_state = 'd'
            #service.updateServiceToUser(request,user,prev_state,new_state)
            #
            ##Svn operations
            #service = Svn()
            #new_state = data['svn']
            #try:
            #    previous_state = user.service_set.filter(user=user,servicetype=service.getServiceType())
            #    if previous_state:
            #        prev_state = previous_state[0].state
            #    else:
            #        prev_state = 'd'
            #except ObjectDoesNotExist:
            #    prev_state = 'd'
            #service.updateServiceToUser(request,user,prev_state,new_state)
            #
            ##Ssh operations
            #service = Ssh()
            #new_state = data['ssh']
            #try:
            #    previous_state = user.service_set.filter(user=user,servicetype=service.getServiceType())
            #    if previous_state:
            #        prev_state = previous_state[0].state
            #    else:
            #        prev_state = 'd'
            #    
            #except ObjectDoesNotExist:
            #    prev_state = 'd'
            #service.updateServiceToUser(request,user,prev_state,new_state)
            #
            ##Quota operations
            #service = QuotaService()
            #quotahardlimit = data['quota_hardlimit']
            #quotasoftlimit = data['quota_softlimit']
            #service.updateServiceToUser(request,user,'d','a',hardlimit=quotahardlimit,softlimit=quotasoftlimit)
            #            
            return redirect("/")

        else:
            if form.errors:
                print form.errors
                request.session['erroruser'] = form
            return redirect("/")
    return redirect("/")


@login_required
def manage_services(request):
    data = {}
    prev_mysql = MySQL().serviceTypeExists()
    data['mysql'] = prev_mysql
    prev_svn = Svn().serviceTypeExists()
    data['svn'] = prev_svn
    prev_ssh = Ssh().serviceTypeExists()
    data['ssh'] = prev_ssh
    prev_quota = QuotaService().serviceTypeExists()
    data['quota'] = prev_quota

    if request.method == 'POST':
        form = ServiceForm(request.POST)
        if form.is_valid():
            mysql = form.cleaned_data['mysql']
            svn = form.cleaned_data['svn']
            ssh = form.cleaned_data['ssh']
            quota = form.cleaned_data['quota']
            if mysql != prev_mysql:
                print "Current %s" % (str(mysql))
                print "previous %s" % (str(prev_mysql))
                m = MySQL()
                m.toggleService()
            if svn != prev_svn:
                print "Current %s" % (str(svn))
                print "previous %s" % (str(prev_svn))
                m = Svn()
                m.toggleService()
            if ssh != prev_ssh:
                m = Ssh()
                m.toggleService()
            if quota != prev_quota:
                m = QuotaService()
                m.toggleService()
            return redirect("/")
    else:
        form = ServiceForm(data)
    return render(request, 'users/services.html', {'form': form})
