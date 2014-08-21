def updateStateField(serviceobject,request,user,prev_state,new_state,newuser=False):
    if newuser:
        prev_state = 'd'
        if new_state:
            new_state = 'a'
        else:
            new_state = 'd'
    if new_state == 'd' and prev_state != 'd':
            serviceobject.service.disableServiceFromUser(request,user)
    elif prev_state == 'd':
        if new_state == 'a' or new_state == 'l':
            if serviceobject.service.initServiceToUser(request,user) and new_state == 'l':
                serviceobject.service.lockServiceFromUser(request,user)
    elif prev_state == 'a' and new_state == 'l':
        print "lalalalala"
        serviceobject.service.lockServiceFromUser(request,user)
    elif prev_state == 'l' and new_state == 'a':
        serviceobject.service.unlockServiceFromUser(request,user)


def updateQuotalimit(quotafieldobject, request,user,prev_limit,new_limit, newuser=False):
    softlimit = new_limit if quotafieldobject.name is 'softlimit' else None
    hardlimit = new_limit if quotafieldobject.name is 'hardlimit' else None
    quotafieldobject.service.initServiceToUser(request,user,hardlimit=hardlimit,softlimit=softlimit)