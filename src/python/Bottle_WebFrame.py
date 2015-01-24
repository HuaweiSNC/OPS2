'''
Created on 2013-3-8

@author: m00147039
@improved:  y00226615
@author: x00106601
URL-->
     -->is Devices,and get device_id
         -->get device_id 's ip,user,passwd,type,and version,driver_name
            -->load_driver
               -->go
'''
#import sys
import config
from bottle import HTTPError, request,response
import bottle
import json
import sys
import time
import logging  
from plugin.bootle_sqlite import SQLitePlugin

from dao.driver_mgmt import driver_mgmt
from dao.device_mgmt import DevicesMgt
from xmlTojson import isdk_convert_xml2json
 

from cipher_mgmt import DecodePassword
from doc_oper import GetHelpDoc, GetLogDoc
from config_check import check_arg
from webapp_mgmt import webapp_general_process,database_general_process
from network_mgmt import NetworkM
from plugin.auth_backend import AuthBackend

main_app=bottle.Bottle()

#get dbfile's handle
dbfile=config.dbFile
sqlite_plugin=SQLitePlugin(dbfile)
network_devices=NetworkM()
g_enableAuth=False
g_enableWhiteList=False
g_channelnum=2
g_checkesn=False
g_aaa=AuthBackend(dbfile, True)

HTTP_UNAUTHORIZED_ACCESS = 401
HTTP_SERVER_ERROR = 500
HTTP_RESPONSE_OK = 200
HTTP_RESOURCE_EMPTY = 204
HTTP_RESOURCE_NOTFIND = 404
 
logger = logging.getLogger("ops.web") 

def myauth_basic(needrole, realm="login", text="Access denied"):
    ''' Callback decorator to require HTTP auth (basic).
        TODO: Add route(check_auth=...) parameter. '''
    def decorator(func):
        def wrapper(*a, **ka):
            #check whitelist of remoteip
            if g_enableWhiteList == True :
                remoteip = request.remote_addr
                if not g_aaa.checkipaddress(remoteip) :
                    response.headers['WWW-Authenticate'] = 'Basic realm="%s"' % realm
                    logger.error('The IP address %s is not in the whitelist of ipaddress, try to login failed'%(remoteip))
                    return HTTPError(HTTP_UNAUTHORIZED_ACCESS, 'Unauthorized access')
                
            #check username and password, role
            if g_enableAuth == True :
                user, password = request.auth or (None, None)
                if user is None or not g_aaa.login(user, password, needrole):
                    response.headers['WWW-Authenticate'] = 'Basic realm="%s"' % realm
                    #response.status = 401
                    if (user == None):
                        logger.error('The ip address %s use the empty user, Try to login failed'%(request.remote_addr))
                    else :
                        logger.error('The ip address %s, user %s login failed'%(request.remote_addr, user))
                    return HTTPError(HTTP_UNAUTHORIZED_ACCESS, 'Access denied')
                
            return func(*a, **ka)
        return wrapper
    return decorator

@main_app.route('/users', method='GET')
@myauth_basic(g_aaa.AUTH_ADMIN)
def query_users():
 
    try:
        return dict(users=g_aaa.show_user())
    except Exception, e:
        print repr(e)
        response.status = HTTP_SERVER_ERROR
        return dict(error=e.message)

@main_app.route('/whitelist', method='GET')
@myauth_basic(g_aaa.AUTH_ADMIN)
def query_whitelist():
 
    try:
        return dict(ipaddress=g_aaa.show_whitelist())
    except Exception, e:
        print repr(e)
        response.status = HTTP_SERVER_ERROR
        return dict(error=e.message)

@main_app.route('/whitelist', method='POST')
@myauth_basic(g_aaa.AUTH_ADMIN)
def add_whitelist():
    
    body= request.body
    ddict = body.read()
    try:
        whitelist = json.loads(ddict)
        ipaddress = whitelist.get('ipaddress')
        desc = whitelist.get('desc')
        
        if (ipaddress == None or ipaddress == '') : 
            return dict(error='need ipaddress')
        return dict(ok=g_aaa.add_whitelist(ipaddress, desc))
    
    except Exception, e:
        print repr(e)
        response.status = HTTP_SERVER_ERROR
        return dict(error=e.message)

@main_app.route('/whitelist', method='PUT')
@myauth_basic(g_aaa.AUTH_ADMIN)
def modify_whitelist():
    
    body= request.body
    ddict = body.read()
    try:
        whitelist = json.loads(ddict)
        ipaddress = whitelist.get('ipaddress')
        desc = whitelist.get('desc')
        if (ipaddress == None or ipaddress == '') : 
            return dict(error='need ipaddress')
        return dict(ok=g_aaa.modify_whitelist(ipaddress, desc))
    except Exception, e:
        print repr(e)
        response.status = HTTP_SERVER_ERROR
        return dict(error=e.message)

@main_app.route('/whitelist/<ipaddress>', method='DELETE')
@myauth_basic(g_aaa.AUTH_ADMIN)
def delete_whitelist(ipaddress):
    
    try:
        return dict(ok=g_aaa.delete_whitelist(ipaddress))
    except Exception, e:
        print repr(e)
        response.status = HTTP_SERVER_ERROR
        return dict(error=e.message)


@main_app.route('/users', method='POST')
@myauth_basic(g_aaa.AUTH_ADMIN)
def create_user():
    
    body= request.body
    ddict = body.read()
    try:
        userinfo = json.loads(ddict)
        username = userinfo.get('username')
        passwd = userinfo.get('passwd')
        role = int(userinfo.get('role'))
        desc = userinfo.get('desc')
        if (username ==None or username == '' or passwd ==None or passwd == '') : 
            return dict(error='need username and passwd')
        return dict(ok=g_aaa.add_user(username, passwd, role, desc))
    except Exception, e:
        print repr(e)
        response.status = HTTP_SERVER_ERROR
        return dict(error=e.message)


@main_app.route('/users', method='PUT')
@myauth_basic(g_aaa.AUTH_ADMIN)
def modify_user():
    
    body= request.body
    ddict = body.read()
    try:
        userinfo = json.loads(ddict)
        username = userinfo.get('username')
        passwd = userinfo.get('passwd')
        role = int(userinfo.get('role'))
        desc = userinfo.get('desc')
        if (username ==None or username == '' or passwd ==None or passwd == '') : 
            return dict(error='need username and passwd')
        return dict(ok=g_aaa.modify_user(username, passwd, role, desc))
    except Exception, e:
        print repr(e)
        response.status = HTTP_SERVER_ERROR
        return dict(error=e.message)
    
@main_app.route('/users/changepassword', method='PUT')
@myauth_basic(g_aaa.AUTH_USER)
def change_passwords():
    """Change password"""
    body= request.body
    ddict = body.read()
    try:
        userinfo = json.loads(ddict)
        newpasswd = userinfo.get('newpasswd')
        user, password = request.auth or (None, None)
        if user is not None:
            return dict(ok=g_aaa.reset_password(user, newpasswd))
    except Exception, e:
        print repr(e)
        response.status = HTTP_SERVER_ERROR
        return dict(error=e.message)

@main_app.route('/users/<username>', method='DELETE' )
@myauth_basic(g_aaa.AUTH_ADMIN)
def delete_user(username):
    try:
        return dict(ok=g_aaa.delete_user(username))
    except Exception, e:
        print repr(e)
        response.status = HTTP_SERVER_ERROR
        return dict(error=e.message)
    
    
@main_app.route('/roles', method='GET' )
@myauth_basic(g_aaa.AUTH_ADMIN)
def query_roles():
    try:
        return dict(ok=g_aaa.show_role())
    except Exception, e:
        print repr(e)
        response.status = HTTP_SERVER_ERROR
        return dict(error=e.message)
    
#===============================================================================
# Devices operation --------> data on device's level
#===============================================================================
@main_app.route('/devices', method='GET')
@myauth_basic(g_aaa.AUTH_USER)
def devices_all_get():
    return network_devices.getAllDeviceInfo()

@main_app.route('/subdevices/<deviceid>', method='POST',  apply=[sqlite_plugin])
@myauth_basic(g_aaa.AUTH_USER)
def subdevices_post(db, deviceid):
    body= request.body
    ddict = body.read()
    try:
        deviceinfo = json.loads(ddict)['device']
        ip = deviceinfo['ip']
        port = deviceinfo.get('port')
        username = deviceinfo['username']
        passwd = deviceinfo['passwd'] 
        if (port is None ):
            port = 22
        if (ip == '' or username ==''or port==''):
            response.status = HTTP_SERVER_ERROR
            return dict(error='must have the following data (ip, port, username)')
        
        device_db =  DevicesMgt(db)
        subid = device_db.add_subdevices(deviceid, ip, port, username, passwd )
        if subid == 0:
            response.status = HTTP_SERVER_ERROR
            return dict(error=('device id %s is not exist'%deviceid))
 
        deviceinfo["id"] = subid
        network_devices.addSubDevice(deviceid, deviceinfo)
        
        return dict(id=subid)
    
    except Exception as e:
        response.status = HTTP_SERVER_ERROR
        return dict(error=e.message)

@main_app.route('/subdevices/<deviceid>/<sid>', method='DELETE', apply=[sqlite_plugin])
@myauth_basic(g_aaa.AUTH_USER)
def subdevices_delete(db, deviceid, sid):
    try:
        devicedb = DevicesMgt(db)
        if (not devicedb.delete_subdevicebyid(sid)):
            response.status = HTTP_RESOURCE_EMPTY
        else:
            network_devices.deleteSubDevice(deviceid, sid)
            response.status = HTTP_RESPONSE_OK
            return dict(ok=True)
    except Exception, e:
        response.status = HTTP_SERVER_ERROR
        return dict(error=e.message)

@main_app.route('/subdevices/<deviceid>/<sid>', method='PUT', apply=[sqlite_plugin])
@myauth_basic(g_aaa.AUTH_USER)
def subdevices_put(db, deviceid, sid):
    body= request.body
    ddict = body.read()
    try:
        deviceinfo = json.loads(ddict)['device']
        ip = deviceinfo['ip']
        port = deviceinfo['port']
        username = deviceinfo['username']
        passwd = deviceinfo['passwd'] 
        
        if (ip == '' or username ==''or port==''):
            response.status = HTTP_SERVER_ERROR
            return dict(error='must have the following data (ip, port, username)')
        device_db = DevicesMgt(db)
        bret = device_db.update_subdevice( sid, ip, port, username, passwd)
        if (not bret):
            response.status = HTTP_SERVER_ERROR
            return dict(error='can not find the subdevice , detail: id=%s and ip=%s' %(sid, ip))
        else:
            response.status = HTTP_RESPONSE_OK
            network_devices.modifySubDevice(deviceid, sid, deviceinfo)
            return dict(ok=True)
    except Exception as e:
        response.status = HTTP_SERVER_ERROR 
        return dict(error='%s' % e)


## (/devices, POST)
@main_app.route('/devices', method='POST', apply=[sqlite_plugin])
@myauth_basic(g_aaa.AUTH_USER)
def devices_config_post(db):
    
    body= request.body
    ddict = body.read()
    try:
        deviceinfo = json.loads(ddict)['device']
        device_db =  DevicesMgt(db)
        devicename = deviceinfo['devicename']
        username = deviceinfo['username']
        ip = deviceinfo['ip']
        passwd = deviceinfo['passwd']
        productType = deviceinfo['productType']
        version = deviceinfo['version']
        port = deviceinfo.get('port')
        deviceiid = deviceinfo.get('id')
        subdevices = deviceinfo.get('subdevices')
        if (deviceiid is not None and 
            (not str(deviceiid).isdigit() or int(deviceiid) <= 0 or int(deviceiid) > sys.maxint )):
            response.status = HTTP_SERVER_ERROR
            return dict(error='The attribute ID is digital, greater than 0, and less than %s'% sys.maxint)
        
        if (ip == ''  or username ==''
        or productType=='' or devicename==''):
            response.status = HTTP_SERVER_ERROR
            return dict(error='must have the following data (ip, devicename, username, productType)')
          
        drivername = getDrivername(productType, version)
        if (drivername == None or drivername == ''):
            response.status = HTTP_SERVER_ERROR
            return dict(error='can not find the driver , detail: producttype=%s and version=%s' %(productType, version))
        
        #dectect if have sub devices
        if (subdevices is not None):
            for sudevice in subdevices:
                if (sudevice.get('ip') == '' or sudevice.get('ip') is None
                     or sudevice.get('username') =='' or sudevice.get('username') is None
                     or sudevice.get('port')=='' or sudevice.get('port') is None):
                    response.status = HTTP_SERVER_ERROR
                    return dict(error='subdevices must have the following data (ip, port, username)')      
        
        if (port == None):
            port = '22'
            deviceinfo['port']=port
            
        #add devices
        deviceid = device_db.add_devices(devicename, ip, str(port), username, passwd, productType, version, deviceiid)
        if deviceid == 0:
            response.status = HTTP_SERVER_ERROR
            return dict(error='device %s or id already exists' % devicename)
        
        deviceinfo["id"] = deviceid
        deviceinfo['driver']= drivername 
        deviceinfo['subdevices']= [] 
        network_devices.addDevice(deviceinfo)
        
        #add subdevices
        if (subdevices is not None):
            for sudevice in subdevices:
                ip = sudevice.get('ip') 
                username =  sudevice.get('username') 
                passwd =  sudevice.get('passwd') 
                port =  sudevice.get('port') 
                subid = device_db.add_subdevices(deviceid, ip, port, username, passwd )
                subdeviceinfo = {}
                subdeviceinfo['ip'] = ip
                subdeviceinfo['port'] = port
                subdeviceinfo['username'] = username
                subdeviceinfo['passwd'] = passwd
                subdeviceinfo["id"]  = subid
                network_devices.addSubDevice(str(deviceid), subdeviceinfo)
   
        return dict(id=deviceid)
    
    except Exception, e:
        response.status = HTTP_SERVER_ERROR
        return dict(error=e.message)
    
## (/devices, DELETE)
@main_app.route('/devices/<deviceid>',method='DELETE',apply=[sqlite_plugin])
@myauth_basic(g_aaa.AUTH_USER)
def devices_config_delete(db, deviceid):
    try:
        devicedb = DevicesMgt(db)
        if (not devicedb.delete_devicebyid(deviceid)):
            response.status = HTTP_RESOURCE_EMPTY
        else:
            devicedb.delete_subdevicebydeviceid(deviceid)
            network_devices.delDevice(deviceid)
            response.status = HTTP_RESPONSE_OK
            return dict(ok=True)
    except Exception as e:
        response.status = HTTP_SERVER_ERROR
        return dict(error=e.message)
    
## (/devices, PUT)
@main_app.route('/devices',method='PUT',apply=[sqlite_plugin])
@myauth_basic(g_aaa.AUTH_USER)
def devices_config_put(db):
    body= request.body
    ddict = body.read()   
    try:
        deviceinfo = json.loads(ddict)['device']
        device_db = DevicesMgt(db)
        devicename = deviceinfo['devicename']
        deviceid = str(deviceinfo['id'])
        ip = deviceinfo['ip']
        username = deviceinfo['username']
        passwd = deviceinfo['passwd']
        productType = deviceinfo['productType']
        version = deviceinfo['version']
        port = deviceinfo.get('port')
        subdevices = deviceinfo.get('subdevices')
        if (ip == ''  or username ==''
            or productType=='' or devicename==''):
            response.status = HTTP_SERVER_ERROR
            return dict(error='must have the following data (ip, devicename, username, productType)')

        if (subdevices is not None):
            for sudevice in subdevices:
                if (sudevice.get('id') == '' or sudevice.get('id') is None
                     or sudevice.get('ip') == '' or sudevice.get('ip') is None
                     or sudevice.get('username') =='' or sudevice.get('username') is None
                     or sudevice.get('port')=='' or sudevice.get('port') is None):
                    response.status = HTTP_SERVER_ERROR
                    return dict(error='subdevices must have the following data (ip, port, username)') 
                
        drivername = getDrivername(productType, version)
        if (drivername == None or drivername == ''):
            response.status = HTTP_SERVER_ERROR
            return dict(error='can not find the driver , detail: producttype=%s and version=%s' %(productType, version))
        
        # update device 
        ret = device_db.update_device(deviceid, devicename, ip, port, username, passwd, productType, version)
        if ret == False:
            response.status = HTTP_SERVER_ERROR
            return dict(error='id %s , device %s does not exist or devicename is repeat' % (deviceid, devicename))
        
        response.status = HTTP_RESPONSE_OK            
        deviceinfo['driver']= drivername 
        deviceinfo['subdevices'] = None
        network_devices.modifyDevice(deviceinfo)
        
        # update sudevice
        if (subdevices is not None):
            for sudevice in subdevices:
                sid = sudevice.get('id')
                ip = sudevice.get('ip') 
                username =  sudevice.get('username') 
                passwd =  sudevice.get('passwd') 
                port =  sudevice.get('port') 
                bret = device_db.update_subdevice( sid, ip, port, username, passwd)
                if (not bret):
                    response.status = HTTP_SERVER_ERROR
                    return dict(error='can not find the subdevice , detail: id=%s and ip=%s' %(sid, ip))
                else:
                    response.status = HTTP_RESPONSE_OK
                    network_devices.modifySubDevice(deviceid, sid, sudevice)
                    
        return dict(ok=True)
            
    except Exception as e:
        response.status = HTTP_SERVER_ERROR 
        return dict(error='%s' % e)

@main_app.route('/devices/<deviceid>', method='GET')
@myauth_basic(g_aaa.AUTH_USER)
def devices_getone(deviceid):  
    try:
        retvalue = network_devices.getDeviceInfoById(deviceid)
        response.status = HTTP_RESPONSE_OK
        if(retvalue == None):
            response.status = HTTP_RESOURCE_EMPTY
        return retvalue
    except Exception, e:
        response.status = HTTP_SERVER_ERROR
        return dict(error=e.message)
        
@main_app.route('/drivers', method='GET', apply=[sqlite_plugin])
@myauth_basic(g_aaa.AUTH_USER)
def drivers_get(db):
    #return showalldevices(db)
    dm2 = driver_mgmt(db=db)
    namelist = dm2.getAllDriverInfo()
    return {'drivers':namelist}
      
@main_app.route('/drivers', method='POST', apply=[sqlite_plugin])
@myauth_basic(g_aaa.AUTH_USER)
def drivers_post(db):
    
    body= request.body
    ddict = body.read()
    try:
        deviceinfo = json.loads(ddict)
        
        productType = deviceinfo['productType']
        version = deviceinfo['version']
        driverFile = deviceinfo['driverFile']
        
        dm2 = driver_mgmt(db=db)
        ret = dm2.add_driver(productType, version, driverFile)
  
        if ret == False:
            response.status = HTTP_SERVER_ERROR
            return dict(error='failed to create driver .')
        else:
            return dict(ok='ok')
    except Exception, e:
        response.status = HTTP_SERVER_ERROR
        return dict(error=e.message)

@main_app.route('/drivers/<driver_id>', method='DELETE', apply=[sqlite_plugin])
@myauth_basic(g_aaa.AUTH_USER)
def drivers_delete(db, driver_id):
    #return showalldevices(db)
    dm2 = driver_mgmt(db=db)
    ret = dm2.delete_driver_id(driver_id)
    if ret == False:
        response.status = HTTP_SERVER_ERROR
        return dict(error='failed to delete driver .')
    
    return dict(ok='ok')
         

#===============================================================================
# maintenance process
#===============================================================================        
## (/version, GET)
@main_app.route('/version', method='GET')
def opsversion_get():  
    return {'version':config.OPSVERSION }        
  
#===============================================================================
# docs help process   --->restful api docs in html
#===============================================================================
@main_app.route('/help/<path:path>',method='GET')
def Doc_Help(path):
    content = GetHelpDoc(path)
    return  content

#===============================================================================
# general process
#===============================================================================
#bind the URL and the methods(get/post/put/delete), and then operate the db by these.
@main_app.route('/devices/<device_id>/<path:path>', method='get')
@myauth_basic(g_aaa.AUTH_USER)
def devices_get(device_id, path):
    return general_process(device_id, path)

@main_app.route('/devices/<device_id>/<path:path>', method='post')
@myauth_basic(g_aaa.AUTH_USER)
def devices_post(device_id, path):
    return general_process(device_id, path)

@main_app.route('/devices/<device_id>/<path:path>', method='put')
@myauth_basic(g_aaa.AUTH_USER)
def devices_put(device_id, path):
    return general_process(device_id, path)

@main_app.route('/devices/<device_id>/<path:path>', method='delete')
@myauth_basic(g_aaa.AUTH_USER)
def devices_delete(device_id, path):
    return general_process(device_id, path)

#===============================================================================
# GUI application operation ------->
#===============================================================================

@main_app.route('/database/<path:path>', method='GET')
@main_app.route('/database/<path:path>', method='PUT')
@main_app.route('/database/<path:path>', method='POST')
@main_app.route('/database/<path:path>', method='DELETE')
@myauth_basic(g_aaa.AUTH_USER)
def database_get(path):
    prefix,dbpath=request.url.split('/database/')
    ret = database_general_process(dbpath, request.method, request.body.read(request.MEMFILE_MAX))
    return ret

@main_app.route('/<path:path>', method='GET')
@main_app.route('/<path:path>', method='POST')
@myauth_basic(g_aaa.AUTH_SPECIAL)
def webapp_Proc(path):
    #print path 
    ret = webapp_general_process(path, request.method)
    if ret == None:
        response.status = HTTP_RESOURCE_NOTFIND
    return ret

def general_process(device_id, path):
    
    if (device_id is not None and 
        (not str(device_id).isdigit() or int(device_id) < 0 or int(device_id) > sys.maxint )):
        response.status = HTTP_SERVER_ERROR
        return dict(error='deivce id is digital, greater than 0, and less than %s'% sys.maxint)
    
    begin = time.time()
    strMethod = request.method
    strMethod = strMethod.upper()
    ## get resource's schemapath in URI
    urlfull = request.url
    prefix,schemapath=urlfull.split('/devices/')
    recordpath =  '/devices/'+schemapath  
    logger.info('Start Message Proc -- %s %s', strMethod, recordpath)
    network_device = network_devices.getDevice(device_id)
    if network_device == None:
        response.status = HTTP_SERVER_ERROR
        errorinfo = "can not find device id : %s" % (device_id)
        return errorinfo
    
    isWrite = True
    if strMethod == 'GET':
        isWrite = False
    
    connectOne = None
    try:
        connectOne = network_device.getFreeConnect(isWrite)
    except Exception as e:
        logger.error('Exception when get a free connection : %s %s error:%s', strMethod, recordpath, e)
        response.status = HTTP_SERVER_ERROR
        return ('%s' % e.message)
   
    try:
        
        if connectOne == None:
            response.status = HTTP_SERVER_ERROR
            errorinfo = "can not find free connection on device id : %s" % (device_id)
            return errorinfo
        
        if connectOne.getStatus() == False:
            response.status = HTTP_SERVER_ERROR
            errorinfo = connectOne.errorinfo
            connectOne.free()
            return errorinfo
    except Exception as e:
        connectOne.free()
        logger.error('Exception when find free connection : %s %s error:%s', strMethod, recordpath, e)
        logger.exception(e)
        response.status = HTTP_SERVER_ERROR
        return e.message
        
    try:
        dInputBody = {
        'json_array' : None,
        'xml_input'  : None
        }

        ## get request messege's body
        read_http_body_strategy(dInputBody)
    
        ## if the xpath has suffix, you need to split it.
        lpath = schemapath.split('/')
        if (lpath[len(lpath) - 1] == 'xml' or lpath[len(lpath) - 1] == 'json'):
            lastElem = lpath.pop(-1)
        else:
            lastElem = lpath[len(lpath) - 1]
            
        ## remove the data type and compose the real schema path
        delimiter = '/'
        schemapath =  delimiter.join(lpath)
    
        #  print dInputBody, schemapath
        #  India's interfaces, return the xml data whatever it is.
        if (strMethod == 'GET'): 
            #temp3= time.time()          
            dataObj = connectOne.get_rest_api_handle(dInputBody, schemapath)
            #temp4= time.time()
            #print 'get info:',(temp4-temp3)
        elif (strMethod == 'DELETE'):
            #print dInputBody
            dataObj = connectOne.delete_rest_api_handle(dInputBody, schemapath)
        elif (strMethod == 'PUT'):
            dataObj = connectOne.put_rest_api_handle(dInputBody, schemapath)
        elif (strMethod == 'POST'):
            dataObj = connectOne.post_rest_api_handle(dInputBody, schemapath)
        else:
            ## there may be some other operators extended
            pass
    except Exception as e:
        logger.error('Exception when executing rest operation : %s %s error:%s', strMethod, recordpath, e)
        logger.exception(e)
        response.status = HTTP_SERVER_ERROR
        return e.message
    finally:
         connectOne.free()
         
    if dataObj == None :
        response.status = HTTP_SERVER_ERROR
        return 
    elif dataObj.startswith('<rpc-error') :
        response.status = HTTP_SERVER_ERROR
        
    ## do convert or not by judging the suffix
    if ("json" == lastElem):
        dataObj = isdk_convert_xml2json(dataObj)
    else:
        dataObj = str(dataObj)
    ## delete the netconf session object.
    end = time.time()
    diff = end-begin
    logger.info('End Message Proc -- %s %s , process time = %fs ', strMethod, recordpath, diff)
    
    #print dataObj
    if (dataObj == None):
        response.status = HTTP_RESOURCE_EMPTY
        
    return dataObj


def read_http_body_strategy(dInputBody):
    body = request.body
    body_input = body.read().strip()
    flag_char = get_first_char_in_string(body_input)
    
    if (flag_char == '['):
        dInputBody['json_array'] = json.loads(body_input)
    elif (flag_char == '<'):
        dInputBody['xml_input'] = body_input
 
    

def get_first_char_in_string(strcontent):
    index = 0
    if (strcontent is not None and strcontent != ''):
        while True:
            if (strcontent[index] != ' '):
                return strcontent[index]
            index += 1
    return ''

def adddevices():
    pass
    #dm1 = DevicesMgt(None,dbfile)   
#    dm1.delete_alldevices()
#    dm1.delete_device('10.137.210.122')
    #dm1.add_devices('10.137.210.122', '10.137.210.122', 'netconf', '!QAZ2wsx#', 'NE5000E', '1.0')    
    #dm1.show_devices()     

def adddriverall():
    dm2 = driver_mgmt(None,dbfile)
    dm2.add_driver('NE5000E', '1.0', 'generalDriver.py')
    dm2.add_driver('NE5000E', '2.0', 'generalDriver.py')
    dm2.add_driver('NE5000E', '3.0', 'generalDriver.py')
    dm2.add_driver('NE5000E', 'V800R005', 'generalDriver.py')
    dm2.add_driver('NE5000E', 'V800R006', 'generalDriver.py')
    dm2.add_driver('NE5000E', 'V800R007', 'generalDriver.py')
    dm2.add_driver('NE5000E', 'V800R008', 'generalDriver.py')
    dm2.add_driver('CE5800', 'V100R003', 'generalDriver.py')
    dm2.add_driver('CE6800', 'V100R003', 'generalDriver.py')
    dm2.add_driver('CE12800', 'V100R003', 'generalDriver.py')
    dm2.add_driver('CX600', 'V100R003', 'generalDriver.py')
    dm2.add_driver('NE40E', '1.0', 'telnet_Client.py')  
    dm2.add_driver('AgileController', '1.0', 'generalDriver.py')  
    #dm2.show_drivers()          

def getDrivername(productType, version):
    driverMgmt = driver_mgmt(None,dbfile)
    driverret = driverMgmt.find_driver(productType, version)
    if (driverret == None) : 
        drivername = ''
    else : 
        drivername = driverret[3]
        drivername = drivername.split('.')[0]
    return drivername
        
def initNetworkDevice():
    #get all devices list
    devicedbMgmt = DevicesMgt(None,dbfile)
    #deviceList = devicedbMgmt.show_devices()
    #Init Connect device    
    deviceList = devicedbMgmt.get_deviceinfos()
    devicedbMgmt.record_all_deviceid()
    
    driverListFinal = []
    for elem in deviceList:
        productType = elem.get('productType')
        version = elem.get('version')
        passwd = elem.get('passwd')
        passwd=DecodePassword(passwd) 
        elem['passwd'] = passwd
        elem["id"] = str(elem["id"])
        otherconnect = elem.get('subdevices')
        newotherconnect = []
        if (otherconnect != None):
            for subelem in otherconnect:
                passwd=subelem.get('passwd')
                passwd=DecodePassword(passwd) 
                newotherconnect.append({'id': subelem.get('id'), 'ip': subelem.get('ip'), 'port': subelem.get('port'), 'username':subelem.get('username'), 'passwd':passwd})
            
        elem["subdevices"]= newotherconnect
        drivername = getDrivername(productType, version)
        elem['driver']= drivername
       
        driverListFinal.append(elem)

    network_devices._channelnum = g_channelnum
    network_devices._opsesn = g_checkesn
    network_devices.initConnectDevice(driverListFinal)
    network_devices.threadstart()
    
from SocketServer import ThreadingMixIn
from wsgiref.simple_server import WSGIServer,WSGIRequestHandler

# To solve the problem of multi thread service reception
class ThreadingWSGIServer(ThreadingMixIn,WSGIServer):
    pass

#To solve some cases to obtain domain slow problem
class MyWSGIRequestHandler(WSGIRequestHandler):
    def address_string(self):
        return '%s'%self.client_address[0]
    def log_message(self, format, *args):
        logger.info("Response %s - %s" %
                 (self.address_string(),format%args))
    
if __name__ == '__main__':

    ##the following code just does one business, to start up the http server
    #===============================================================================
    # Configuration 
    #===============================================================================
    ## checking for the proper command line argument pattern 
    #defaule configure    

    g_host=''
    g_port = 8080  
    g_certfile = ''  
    
    #get ip and port if config
    iret = check_arg()   
    if 0 == iret:
        print 'default: host=%s, port=%s'%('localhost', g_port)  
        if config.DUSER_INPUT['input_serverip'] != '':  
            g_host=config.DUSER_INPUT['input_serverip'] 
        if config.DUSER_INPUT['input_port'] != '':  
            g_port=int(config.DUSER_INPUT['input_port'])
            print 'configured: host=%s, port=%s'%(g_host, g_port)
        if config.DUSER_INPUT['cert_file'] != '':  
            g_certfile=config.DUSER_INPUT['cert_file']
        if config.DUSER_INPUT['auth_basic'] != '':  
            g_enableAuth=config.DUSER_INPUT['auth_basic']
        if config.DUSER_INPUT['white_list'] != '':  
            g_enableWhiteList=config.DUSER_INPUT['white_list']  
        if config.DUSER_INPUT['channel_num'] != '':  
            g_channelnum=int(config.DUSER_INPUT['channel_num'])  

        # setting if check esn string
        g_checkesn=config.DUSER_INPUT['check_esn'] 
        
        # setting logging level 
        config.setOpsLoggingLevel(config.DUSER_INPUT['input_loglevle'])       
    else:     
        exit()
    
    
        
    ##create the Device table in DB, and add a device into the table
    adddevices()
    
    ##add a driver to DB.
    adddriverall()    
    
    #init network device
    initNetworkDevice() 
    
    #one server contains: 
    from wsgiref.simple_server import make_server
    server = make_server(g_host, g_port, main_app, handler_class=MyWSGIRequestHandler, server_class=ThreadingWSGIServer)
    protocol = 'http'
    if (g_certfile != None and g_certfile != '' ) :
        protocol = 'https'
        import ssl
        server.socket = ssl.wrap_socket (                      
           server.socket,
           certfile = g_certfile,  # path to certificate
           server_side = True)
        
    serverhost=g_host
    if g_host =='':
        serverhost = 'localhost'
    
    print """Huawei OPS v2.01 server starting up (using WSGIRefServer())...
    Listening on %s://%s:%s/
    Hit Ctrl-C to quit."""%(protocol,serverhost,g_port)
    
    logger.debug("Huawei OPS v2.01 server starting up, Listening on %s://%s:%s/" %(protocol,serverhost,g_port))
    
    #staying on the running status
    try:   
        server.serve_forever() 
    except:
        print 'quit from bottle'

