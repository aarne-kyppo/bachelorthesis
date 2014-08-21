from servicebase import ServiceBase
from servicefield import ServiceField
from django import forms
from django.core.exceptions import ObjectDoesNotExist
from updatefunctions import updateQuotalimit
from users.models import ServiceType, Service
class QuotaService(ServiceBase):
    def __init__(self):
        self.fields = (ServiceField('Quota softlimit','softlimit',self,forms.IntegerField(label="Quota softlimit"),updateQuotalimit),ServiceField('Quota hardlimit','hardlimit',self,forms.IntegerField(label="Quota hardlimit"),updateQuotalimit))
    def initService(self,request,mountpoint='/home'):
        #Before running this install quota and add usrquota to partition(in which you want quotas to work) options in /etc/fstab.
        try:
            quotacheck("-vgum", mountpoint)
            
            try:
                quotaon("av")
            except ErrorReturnCode:
                messages.error(request,'QuotaError: Failed to enable diskquota.')
                return False
        
        except ErrorReturnCode:
            messages.error(request,'QuotaError: Failed to make initial quotacheck')
            return False
        if not self.serviceTypeExists():
            tmp = ServiceType.objects.create(name='quota',state='a')
            tmp.save()
        return True
    
    
    def initServiceToUser(self,request,user,**kw):
        """
        try:
            hardlimit_as_kB = hardlimit*1024
            softlimit_as_kB = softlimit*1024
            username = user.username
            setquota("-u",username,softlimit_as_kB,hardlimit_as_kB,0,0,"-a")
        except ErrorReturnCode:
            messages.error(request,'QuotaError: Failed to set quota for user.')"""
        hardlimit = kw['hardlimit']
        softlimit = kw['softlimit']
        print "sdofksdpofk " + str(hardlimit)
    
    def lockServiceFromUser(self,request,user):
        pass
    
    def unlockServiceFromUser(self,request,user):
        pass
    
    def resetUsersPassword(self,request,user,password):
        pass
    
    def disableServiceFromUser(self,request,user):
        pass
    
    def getServiceOfUser(self,user,fieldname=None):
        try:
            servicetypeobject = ServiceType.objects.get(name=self.servicetype)
            service = user.quota_set.get(servicetype=servicetypeobject)
        except ObjectDoesNotExist:
            if fieldname:
                return None
            return [None, None]
        if fieldname:
            if fieldname is 'hardlimit':
                return service.hardlimit
            elif fieldname is 'softlimit':
                return service.softlimit
        values = []
        values = [service.softlimit, service.hardlimit]
        print "Quota: " + str(type(values))
        return values
    
    def getUserDataFields(self,user):
        initial_limits = self.getServiceOfUser(user)
        if not initial_limits[1]:
            initial_limits[1] = 0
        if not initial_limits[0]:
            initial_limits[0] = 0
        return [['softlimit',initial_limits[0]],['hardlimit',initial_limits[1]]]
    
    def deleteService(self,request):
        if self.serviceTypeExists():
            ServiceType.objects.get(name="quota").delete()
            try:
                quotaoff("av")
            except ErrorReturnCode:
                messages.error(request,'QuotaError: Failed to disable diskquota.')
                return False
            if not self.serviceTypeExists():
                ServiceType.objects.get(name='quota').delete()
            return True
        return True
    import re

def editfstab(usrquota,grpquota,partitionmountpoint = "/"):
    f = open("/etc/fstab","r")
    rows = []
    for line in f:
        rows.append(line)
    f.close()
    selectedrow = None
    selectedrowindex = None
    for i, row in enumerate(rows):
        m = re.match("^[^#].+\s+%s\s+.+" % (partitionmountpoint),row)
        if m:
            selectedrow = row
            selectedrowindex = i
    if selectedrow:
        columns = re.search("^(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\d)\s+(\d)$",selectedrow)
        print columns.groups()
        device = columns.group(1)
        mountpoint = columns.group(2)
        fs = columns.group(3) 
        options = columns.group(4)
        backup = columns.group(5)
        priority = columns.group(6)
        if "usrquota" not in options and usrquota:
            options = options + ",usrquota"
        if "usrquota" in options and not usrquota:
            if ",usrquota" in options:
                options = options.replace(",usrquota","")
            elif "usrquota," in options:
                options = options.replace("usrquota,","")
        if "grpquota" not in options and grpquota:
            options = options + ",grpquota"
        if "grpquota" in options and not grpquota:
            if ",grpquota" in options:
                print "sdfsdfsdf"
                options = options.replace(",grpquota","")
            elif "grpquota," in options:
                options = options.replace("grpquota,","")
        line = " ".join([device,mountpoint,fs,options,backup,priority])
        
        f = open("/etc/fstab","w")
        for i, row in enumerate(rows):
            if i == selectedrowindex:
                rowtext = line + "\n"
            else:
                rowtext = row
            f.write(rowtext)
        f.close()
    else:
        print "No enabled fs in given mountpoint"