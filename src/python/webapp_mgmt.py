'''
Created on 2013-11-30

'''

import os
from bottle import request
from webappdb_mgmt import WebAppDBMgt

class MyUserData():
    
    username = ""
    infoname = ""
    datatype = ""
    datainfo = ""
    def __init__(self):
        pass
         
    def __exit__(self):
        pass
           


 

def file_read_html(path):
    filepath="webapps/"+path
    print "open file: %s"%filepath   
    if os.path.isfile(filepath) == 0:
        print "the file %s does not exist"%filepath
        return
    if path.endswith('.db') == True:
        return ''
    file = open(filepath, "rb");    
    if file == None:
        print "open file %s failed"%filepath
        return
    content=file.read()      
    print "get file content OK"
    file.close()
    #print content    
    return content
    
def login_submit(path):     
    if path == 'dc/sdncui.html':        
        name     = request.forms.get('name')     
        password = request.forms.get('password')     
        if check_login(name, password):         
            filepath="webapps/"+path  
            print "open file: %s"%filepath      
            file = open(filepath, "rb");    
            if file == None:
                print "open file %s failed"%filepath
                return
            content=file.read()      
            print "get file content OK"
            file.close() 
            return content  
        else:         
            return "<p>Login failed</p>"  
    else:
        return
        
def check_login(name, password):     
    if name == 'root' and password == 'root':         
        return True 
    
def fileget_proc(path):
    return file_read_html(path)

def filepost_proc(path):
    return login_submit(path)
    
def webapp_general_process(path,method):
    if method == 'GET':
        ret = fileget_proc(path)
    elif method == 'POST':
        ret = filepost_proc(path)
    else:
        pass
    
    return ret

def getuserdbfileBypath(path): 
    if path.find('/') != -1:
        temp = path.split('/')
        app=temp[0]
    elif path.find('?') != -1:
        temp = path.split('?')
        app=temp[0]
        
    dbfile='/'+app+'.db'
    dbpath="webapps/"+ dbfile
    return dbpath

def getuserdbBypath(path):
    dbfile = getuserdbfileBypath(path)
    #print 'dbfile:',dbfile
    try:
        dm=WebAppDBMgt(None,dbfile)
        return dm
    except:
        print 'fail to open file', dbfile
        return   

def getuserinfoBypath(path):
    temp = path.split('?')
    templen = len(temp)
    userdata = MyUserData()
    userinfo = temp[templen-1]
    userinfo_temp = userinfo.split('&')
    datatype=''
    datainfo=''
    #print path
    for elem in userinfo_temp:
        elem_tmp = elem.split('=')
        if elem_tmp[0] == 'username':
            userdata.username=elem_tmp[1]
        if elem_tmp[0] == 'infoname':
            userdata.infoname=elem_tmp[1]
        if elem_tmp[0] == 'datatype':
            userdata.datatype=elem_tmp[1]
        if elem_tmp[0] == 'data':
            userdata.datainfo=elem_tmp[1]
    #print 'userinfo:',username,infoname,datatype,datainfo
    return userdata

def check_userPsd(inputPsd, storePsd):
    #print 'inputPsd',inputPsd
    #print 'storePsd',storePsd
    if inputPsd == storePsd:
        return True
    else:
        return False

def database_get(path):  
     
    userdata = getuserinfoBypath(path)
    #print 'get input userinfo:',username,infoname,datatype,datainfo
    dm=getuserdbBypath(path)
    if dm == None:
        return '<error>unsupported<error>'
    try:
        data = ""
        ret = dm.get_userdata(userdata.username,userdata.infoname)        
        if path.find('checkresult') != -1:
            if check_userPsd(userdata.datainfo, ret[3])==True:
                return '<ok></ok>'
            #print 'check password'
          #  print  check_userPsd(userdata.datainfo, ret[3])
#            return check_userPsd(userdata.datainfo, ret[3])    
             
                 
        if ret != None and ret[2] != 'password':
            data = ret[3]
        return data
    except Exception as e:
        return '<error>%s<error>'%e

def database_post(path,body):
    userdata = getuserinfoBypath(path)    
    dm=getuserdbBypath(path)
    if dm == None:
        return '<error>unsupported<error>'
    #print 'get input userinfo:',username,infoname,datatype,datainfo
    if body == None or body == '':
        body =userdata.datainfo
    try:
        ret = dm.add_userdata(userdata.username,userdata.infoname,userdata.datatype,body)
        if ret == True:
            return '<ok></ok>'
    except Exception as e:
        return '<error>%s<error>'%e

def database_put(path,body):    
    userdata = getuserinfoBypath(path)    
    dm=getuserdbBypath(path)
    if dm == None:
        return '<error>unsupported<error>'
    if body == None or body == '':
        body = userdata.datainfo
     
    try:
        ret = dm.update_userdata(userdata.username,userdata.infoname,userdata.datatype,body)
        if ret == True:
            return '<ok></ok>'
    except Exception as e:
        return '<error>%s<error>'%e

def database_delete(path):
    userdata = getuserinfoBypath(path)    
    dm=getuserdbBypath(path)
    if dm == None:
        return '<error>unsupported<error>'
    
    try:
        ret = dm.delete_userdata(userdata.username,userdata.infoname)
        if ret == True:
            return '<ok></ok>'
    except Exception as e:
        return '<error>%s<error>'%e

def database_general_process(path, method, body=None):
    if method == 'GET':
        ret = database_get(path)
    elif method == 'POST':
        ret = database_post(path,body)
    elif method == 'PUT':
        ret = database_put(path,body)
    elif method == 'DELETE':
        ret = database_delete(path)
    else:
        pass
    
    return ret


if __name__ == '__main__':
    database_general_process('dc?username=admin&infoname=userdata&datatype=password&data=admin', 'POST')
    database_general_process('dc?username=admin&infoname=userpage&datrdatype=data&data=xxxxxxxxxxxxx', 'POST')
    ret = database_general_process('dc?username=admin&infoname=userpage', 'GET')
    print ret
    ret = database_general_process('dc/checkresult?username=admin&infoname=userdata&data=abcd', 'GET')
    print ret    
    ret = database_general_process('dc/checkresult?username=admin&infoname=userdata&data=admin', 'GET')
    print ret
    
    