#!/usr/bin/env python  
# -*- coding: utf-8 -*-  
# Autor: xielequan

import config
import logging 
import inspect 
import sys
import threading
from networkdevice_mgmt import NetworkDeviceM
import ThreadStacktracer
from rest_adapter import Rest_Adapter
logger = logging.getLogger("ops.hack")  
import time
reload(sys)   
sys.setdefaultencoding('utf8')  
    
##-------------------------------------------------------------------------------
##-- Class Name      : Process_Rest_Api
##-- Date Created    : 04-03-2013
##-- Author          :
##-- Description     : Class contains
##--                    a. Methods to open and close NETCONF session over SSH
##--                    b. Methods to handle REST api's (POST, PUT, DELETE GET)
##--                    c. Methods to handle REST API`s for Action schema 
##--                    d. Methods to handle GET-CONFIG protocol operation
##--                    e. Methods to handle COPY-CONFIG protocol operation
##--                    f. Methods to handle DELETE-CONFIG protocol operation
##--                    g. Methods to handle KILL-SESSION protocol operation
##-- Caution         :
##------------------------------------------------------------------------------
class Process_Rest_Api(Rest_Adapter): 

    createid = 0
    def __init__(self,ip,port=22,username="root123",password="Root@123"):
        self.ip = ip
        self.port = port
        self.username = username
        self.password = password
        self.createid = self.createid+1
        self.cid = self.createid
        self.status = True
        
        #manager.logging.basicConfig(filename='e:/ncclient.log', level=manager.logging.DEBUG)
        logger.debug('[Hack] __init__ cid:%s, ip:%s, port:%s, username:%s, password:%s '% (self.cid ,self.ip, self.port, self.username, self.password ))     

    def __exit__(self):
#         print '__exit__'
        logger.debug('[Hack] __exit__ cid:%s, ip:%s, port:%s, username:%s, password:%s '% (self.cid ,self.ip, self.port, self.username, self.password ))   
    
    def getStatus(self):
        logger.debug('[Hack] getStatus() cid:%s '% (self.cid))   
        return self.status
    def close(self):
        pass
    
    def reconnect(self): 
        return True
    
    def close_ssh(self):
        logger.debug('[Hack] close_ssh() cid:%s '% (self.cid))
    
    def reconnect_ssh(self):
        logger.debug('[Hack] reconnect_ssh() cid:%s '% (self.cid))
        return True
 
    def post_rest_api_handle(self, dInputBody, schemapath):
        logger.debug('[Hack] post_rest_api_handle(): cid:%d, XPATH:%s, body:%s'% (self.cid, schemapath, dInputBody))
 
        ##  <device id>/_action/ftpc/ftpcTransferFiles/ftpcTransferFile
        lschema = schemapath.split('/')
        sactionflag = lschema[1]
        if '_action' == sactionflag:
            logger.debug('[Hack] post_rest_api_handle(): cid:%s, sactionflag:%s'% (self.cid, '_action'))
            return 'self.action_rest_api_handle(dInputBody, lschema)'
        elif sactionflag.find('copy-config') != -1 :
            logger.debug('[Hack] post_rest_api_handle(): cid:%s, sactionflag:%s'% (self.cid, 'copy-config'))
            return 'self.copyconfig_rest_api_handle(dInputBody, lschema)'
        elif sactionflag.find('delete-config') != -1 :
            logger.debug('[Hack] post_rest_api_handle(): cid:%s, sactionflag:%s'% (self.cid, 'delete-config'))
            return 'self.deleteconfig_rest_api_handle(dInputBody, lschema)'
        elif sactionflag.find('kill-session') != -1 :
            logger.debug('[Hack] post_rest_api_handle(): cid:%s, sactionflag:%s'% (self.cid, 'kill-session'))
            return 'self.killsession_rest_api_handle(dInputBody, lschema)'
        
        logger.debug('[Hack] cid:%d isdk_convert_rpc2restapi()'% (self.cid))
        return "isdklib.isdk_convert_rpc2restapi(srpcreplystring, schemapath, 'POST') "

    def put_rest_api_handle(self, dInputBody, schemapath):
        
        logger.debug('[Hack] put_rest_api_handle(): cid:%s, XPATH:%s, body:%s '% (self.cid, schemapath, dInputBody))
        return "isdklib.isdk_convert_rpc2restapi(srpcreplystring, schemapath, 'PUT')"

    def delete_rest_api_handle(self, dInputBody, schemapath):
        logger.debug('[Hack]delete_rest_api_handle() cid:%s,: XPATH:%s JSON_ARRAY: %s'% (self.cid, schemapath, dInputBody))
       
        return "isdklib.isdk_convert_rpc2restapi(srpcreplystring, schemapath, 'DELETE') "
    
    def get_rest_api_handle(self, dInputBody, schemapath):
        
        logger.debug('[Hack]get_rest_api_handle() cid:%s,: XPATH:%s JSON_ARRAY: %s'% (self.cid, schemapath, dInputBody))
        #network = Bottle_WebFrame.network_devices
        stack = inspect.stack()
        #print '=%s' % stack
        
        stacklocal = stack[2][0]
        #print '==%s' % stacklocal
        #stackinspect = stack[2][0].f_locals["network_devices"]
        #print '===%s' % stacklocal.f_globals
        stackinspect = stacklocal.f_globals['network_devices']
        #print '====%s' % stackinspect
        #username = stackinspect.username
        
        threadlist = None
        deviceListTmp = []
        import encodings.utf_8
        import base64
        try:
            devicedict = stackinspect.devicedict
            for elem in devicedict:              
                networkDevice = devicedict[elem]
                deviceListTmp.append('networkDevic==id: %s '% networkDevice.deviceid)
                #logger.info('networkDevic==id: %s '% networkDevice.deviceid)
                for name,value in vars(networkDevice).items():
                    #logger.info('  networkDevice local  %s=%s'%(name,value))
                    deviceListTmp.append('  networkDevice local  %s=%s'%(name,value))
                for name,value in vars(NetworkDeviceM).items():
                    #logger.info('  networkDevice  %s=%s'%(name,value))
                    deviceListTmp.append('  networkDevice  %s=%s'%(name,value))
                for elem in networkDevice.connlist:  
                    #logger.info('  connection==sid: %s' % elem.sid)
                    deviceListTmp.append('  connection==sid: %s' % elem.sid)
                    for name,value in vars(elem).items():
                         #logger.info('    conn  %s=%s'%(name,value))
                         deviceListTmp.append('    conn  %s=%s'%(name,value))
                    classObj = elem.classObj
                    if (classObj != None):
                        for name,value in vars(classObj).items():
                            #logger.info('     netconf  %s=%s'%(name,value))
                            deviceListTmp.append('     netconf  %s=%s'%(name,value))
            
            threadlist = threading.enumerate()
            threadcount = threading.activeCount()
            deviceListTmp.append('\n\n ')
            for thre in threadlist:
                #logger.error('thread id == start ')
                deviceListTmp.append('#thread id ==')
                for name,value in vars(thre).items():
                    #logger.error('   thread  %s=%s'%(name,value))
                    valuetmp = value
                    try:
                        if (name == 'host_key' or name == 'H' or name=='session_id' or name == '\x14'):
                            valuetmp = ''
                            valuetmp = '   thread  %s=%s' %(name,valuetmp)
                        #valuetmp = encodings.utf_8.decode(str(value))
                    except Exception as e:
                        print repr(e)
                        print value

                    deviceListTmp.append(str(valuetmp))
     
            mystr = '\n'.join(deviceListTmp) 
            ThreadStacktracer.trace_start("trace.log", mystr, threadlist)
        except Exception as e:
            print repr(e)
            logger.exception(e)
        return "<ok>  caller name:%s</ok>" % (threadlist)
       
    def set_main_device(self, ipaddress, port, username , password):
        pass
    
    def get_esn(self):
        return ''
    
    def set_multi_ipaddress(self, deviceList):
        pass

if __name__ == '__main__':
    s='10.137.209.45'
    s1='182.7.9.40'
    classObj = Process_Rest_Api(s1) 
      
    schemapath = '1/ifm/interfaces/interface/ifIndex/discover-enable'
      
#===============================================================================
#     dInputBody = { 
#                   'json_array':[
#                                 {"session-id":"163"},
#                                 ]
#                   ,
#     'xml_input' :None
# #                     'xml_input' : '''<target>
# #                                          <candidate/>
# #                                      </target>
# #                                      <source>
# #                                          <running/>
# #                                      </source>'''
# #                     
#     }
#                    
# #     schemapath = '1/ntp/ntpAuthKeyCfgs/ntpAuthKeyCfg?keyId=2005'
# #     
# #     dInputBody = { 
# #     'json_array':[
# #                   {"keyId":"2005"},
# #                   {"mode":"MD5"},
# #                   {"keyVal":"password"},
# #                   {"isReliable":"true"}
# #                   ],
# #     'xml_input' : None
# #     }
# #   
#     dInputBody ={'json_array':None,
#                  'xml_input':None
#                  }
#===============================================================================

    dInputBody ={'json_array':None,
               'xml_input':None
               }
    jsonObj = classObj.get_rest_api_handle(dInputBody, schemapath) 
#     jsonObj = classObj._m.poweroff_machine()

    print '\n POST Output JSON object:\n',jsonObj

    
    classObj.__exit__()



