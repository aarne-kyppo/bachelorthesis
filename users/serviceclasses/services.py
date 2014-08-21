#from django.contrib.auth.models import User
from MySQLdb import IntegrityError
from django import forms
from django.contrib import messages
from django.db import connection
from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import EmailMessage
from users.models import ServiceType, Service
import string
import random
import pyclbr
import sys
from sh import useradd, chown, ErrorReturnCode, deluser, rm, quotacheck, quotaon, setquota,chpasswd,tar,cd, mysqldump,gpasswd,passwd,usermod,deluser, groups

def getServices():
    services = pyclbr.readmodule("users.serviceclasses")
    return services

def sendInfoMaterial(service,subject,user,**kw):
    print "osdfksdopfkpodskfposdkfpodskpof"
    print kw
    if 'body' not in kw:
        username = "Username: {}\n".format(user.username)
        if 'password' in kw:
            password = "Password: {}\n".format(kw['password'])
        else:
            password = ""
        body = "{}{}Host: srv.plab.fi".format(username,password)
    fromfield = u'kyppoa@gmail.com'
    print "USER EMAIL: {}".format(user.email)
    tofield = (user.email,)
    cc = []
    bcc = []
    
    email = EmailMessage(subject,body,fromfield,tofield,bcc)
    if hasattr(service,'infomaterial'):
        email.attach_file(service.infomaterial)
    email.send()


STATES = (
        ('d','disabled'),
        ('l','locked'),
        ('a','active')
    )

def generate_password():
    size = 8
    chars = string.ascii_letters + string.digits
    password = ''.join(random.choice(chars) for x in range(size))
    return password
    
