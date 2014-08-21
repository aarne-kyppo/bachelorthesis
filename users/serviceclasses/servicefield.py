class ServiceField:
    def __init__(self,header,name,service,field,updatefunction,newuserfield=None):
        self.name = name
        self.service = service
        self.field = field
        self.header = header
        if newuserfield:
            self.newuserfield = newuserfield
        self.updatefunction = updatefunction
    def update(self,request,user,prev_value,newvalue,**kw):
        if 'newuser' in kw:
            self.updatefunction(self,request,user,prev_value,newvalue,newuser=True)
        else:
            self.updatefunction(self,request,user,prev_value,newvalue)