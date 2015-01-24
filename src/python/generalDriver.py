##----------------------------------------------------------------------------------------------------------------------
##-- Copyright (C) Huawei Technologies Co., Ltd. 2008-2011. All rights reserved.
##----------------------------------------------------------------------------------------------------------------------
##----------------------------------------------------------------------------------------------------------------------
##--Project Code    : VRPV8
##--File name       : generalDriver.py
##--Author          :
##--Description     : Consist of Class which contains handler for REST api's, and managing NETCONF session over SSH
##----------------------------------------------------------------------------------------------------------------------
##--History:
##--Date                 Author                 Modification
##--04-03-2013             Ganesh                 created file.
##--10-07-2013            azam                    modified for the lsvs access
##--15-07-2013            azam                    added new function to support for Action Schema
##----------------------------------------------------------------------------------------------------------------------

import isdklib
from ncclient import manager
# import json
import selflearn
from rest_adapter import Rest_Adapter
import logging 
# create logger 
logger = logging.getLogger("ops.netconf")  

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

    _m = None
    mainDevice = {'ip':'0.0.0.0','port':'22','username':'None','passwd':'None'}
    devices = []
    connected = None
    status = False
    def __init__(self,ip,port=22,username="root123",password="Root@123"):
        
        self._m = None
        self.mainDevice = {}
        self.devices = []
        self.connected = None
        self.status = False
        self.errorinfo = ''
        
        self.ip = ip
        self.port = port
        self.username = username
        self.password = password
        
        self.mainDevice['ip'] = self.ip
        self.mainDevice['port'] = self.port
        self.mainDevice['username'] = self.username
        self.mainDevice['passwd'] = self.password 
        #manager.logging.basicConfig(filename='e:/ncclient.log', level=manager.logging.DEBUG)
        logger.debug('client session request initiated ')     
        try:   
            self._m = manager.connect_ssh(ip, port = port,username=username,password=password, allow_agent=False,look_for_keys=False)
            self.status = self._m.connected
            logger.debug('client session creation is successful ')
        except Exception as e: 
            self.status = False
            self.errorinfo = e
            logger.error('client session creation is failed. error: %s ', self.errorinfo)        
        
    def __exit__(self):
#         print '__exit__'
        logger.debug('client session closing is initiated ')
        self._m.close_session()
        logger.debug('client session closing successfully ')
        pass
    
    def getStatus(self):
        if self._m != None:
            self.status = self._m.connected
        return self.status
    
    def close(self):
        if self.getStatus() == True:
            try: 
                self._m.close_session()
            except Exception as e: 
                logger.error( '[%s] client session close failed. msg: %s ' % (self.ip , e))
		
##-------------------------------------------------------------------------------
##-- Class Name      : reconnect_ssh
##-- Date Created    : 02-06-2014
##-- Author          : vikash kumar
##-- Description     : This function will try to connect with the input devices and once it succeeds then it will return else it will
##--                    go on trying till the last device
##-- Caution         :
##------------------------------------------------------------------------------ 
    def reconnect(self):    
        """subdevices list must be there,
        loop to subdevices ,and try to connect each first succes connection will return
        """
        
        # reconnect main device
        if self.getStatus() == False:
            try:
                self.ip = self.mainDevice['ip']
                self.port = self.mainDevice['port']
                self.username = self.mainDevice['username']
                self.password = self.mainDevice['passwd']
                self._m = manager.connect_ssh(self.ip, port =self.port, username=self.username, password=self.password,allow_agent=False,look_for_keys=False)
                if self._m is not None :
                    self.status = self._m.connected
                    logger.info('Client session is created by ip:%s, port:%s, username:%s'%(self.ip,self.port,self.username))
                    return self._m.connected
            except Exception as e:
                    self.status = False
                    self.errorinfo = e
                    logger.debug('client session creation failed. ip:%s, port:%s, username:%s error: %s ',self.ip, self.port,self.username, self.errorinfo)
                    #logger.exception(e)
        goToNextDevice = True
        if self.getStatus() == False:
            if not self.devices:
                logger.debug('DeviceList is Empty')
                return None
            for subDevices in self.devices:
                goToNextDevice = True
                if not subDevices:
                    logger.debug('No sub device present')
                    return None
                for keys,values in subDevices.iteritems():
                    if not values:
                        goToNextDevice=False
                        logger.debug('Invalid or empty parameter')
                        break  
                try:
                    self.ip = subDevices.get('ip')
                    self.port = subDevices.get('port')
                    self.username = subDevices.get('username')
                    self.password = subDevices.get('passwd')
                    
                    connected = manager.connect_ssh(self.ip, port = self.port ,username = self.username, password = self.password, allow_agent=False,look_for_keys=False)
                    if connected is not None :
                        self._m = connected 
                        logger.info('Client session is created by ip:%s, port:%s, username:%s'%(self.ip,self.port,self.username))
                        self.status = self._m.connected
                        return self._m.connected
                    
                except Exception as e:
                    self.status = False
                    
                    self.errorinfo = e
                    logger.debug('client session creation failed. ip:%s, port:%s, username:%s, error: %s ', self.ip,self.port,self.username, self.errorinfo)
                    #logger.exception(e)
            return None 
        return None
        
    def set_main_device(self, ipaddress, port, username , password):
        """ update the main device details
        """
         
        connectdevice = { 'ip' : self.ip, 'port' : self.port, 'username' : self.username, 'passwd' : self.password}
        
        isclosessh = False
        ismaindevicerun = False

        # we run connect on main device
        if (self.mainDevice == connectdevice):
            ismaindevicerun = True

        self.mainDevice['ip'] = ipaddress
        self.mainDevice['port'] = port
        self.mainDevice['username'] = username
        self.mainDevice['passwd'] = password 

        # we not modify main device .
        if (ismaindevicerun and self.mainDevice != connectdevice):
            isclosessh = True
 
        if isclosessh and self.getStatus() == True:
            self.close()

        return
    
    def post_rest_api_handle(self, dInputBody, schemapath):
        logger.debug('post_rest_api_handle: XPATH:%s', schemapath)
        
        ##  <device id>/_action/ftpc/ftpcTransferFiles/ftpcTransferFile
        lschema = schemapath.split('/')
        sactionflag = lschema[1]
        if '_action' == sactionflag:
            return self.action_rest_api_handle(dInputBody, lschema)
        elif sactionflag.find('copy-config') != -1 :
            return self.copyconfig_rest_api_handle(dInputBody, lschema)
        elif sactionflag.find('delete-config') != -1 :
            return self.deleteconfig_rest_api_handle(dInputBody, lschema)
        elif sactionflag.find('kill-session') != -1 :
            return self.killsession_rest_api_handle(dInputBody, lschema)
        
        for k,v in dInputBody.items():
            logger.debug('post_rest_api_handle: dInputBody key:%s Value: %s', k, v)
        sactionflag = ''
        schemapath = '/'.join(lschema)
        lrpcAndHw = isdklib.isdk_convert_restapi2rpc(dInputBody, schemapath, 'POST')
        
        if lrpcAndHw == []:
            logger.debug('POST REST API to RPC conversion failed: Return NIL value')
            return ''
        
        srpc = lrpcAndHw[0]
        shwcontext = lrpcAndHw[1]
        sRollback = lrpcAndHw[2]        
        if srpc == '':
            logger.debug('POST REST API to RPC conversion failed: Return NIL value')
            return ''
        
        if shwcontext == '':
            logger.debug('POST REST API hwcontext: not available')
#             return ''
        
        logger.debug('Edit-config(create) RPC request generated: %s',srpc)
        logger.debug('Edit-config(create) hwcontext: %s',shwcontext)
        srpcstring = '&'.join([sRollback,srpc])
        srpcreplystring = isdklib.isdk_sendrecv_ncclient(self._m, srpcstring,shwcontext,'POST')
        if srpcreplystring == '':
            logger.debug('Edit-config (create) rpc send request and receive reply  failed')
            return ''
        logger.debug('Edit-config (create) rpc reply: %s',srpcreplystring)    
        return isdklib.isdk_convert_rpc2restapi(srpcreplystring, schemapath, 'POST') 

    def put_rest_api_handle(self, dInputBody, schemapath):
        logger.debug('put_rest_api_handle: XPATH:%s', schemapath)
        for k,v in dInputBody.items():
            logger.debug('put_rest_api_handle: dInputBody key:%s Value: %s', k, v)
        
        lrpcAndHw = isdklib.isdk_convert_restapi2rpc(dInputBody, schemapath, 'PUT')
        
        if lrpcAndHw == []:
            logger.debug('POST REST API to RPC conversion failed: Return NIL value')
            return ''
        
        srpc = lrpcAndHw[0]
        shwcontext = lrpcAndHw[1]
        sRollback = lrpcAndHw[2]        
        if srpc == '':
            logger.debug('PUT REST API to RPC conversion failed: Return NIL value')
            return ''
        
        if shwcontext == '':
            logger.debug('PUT hwcontext: not available')
#             return ''
        
        logger.debug('Edit-config(merge) RPC request generated: %s',srpc)
        logger.debug('Edit-config(merge) hwcontext: %s',shwcontext)
        srpcstring = '&'.join([sRollback,srpc])
        srpcreplystring = isdklib.isdk_sendrecv_ncclient(self._m, srpcstring,shwcontext,'PUT')
        if srpcreplystring == '':
            logger.debug('Edit-config (merge) rpc send request and receive reply  failed')
            return ''
        logger.debug('Edit-config (merge) rpc reply: %s',srpcreplystring)
        return isdklib.isdk_convert_rpc2restapi(srpcreplystring, schemapath, 'PUT') 

    def delete_rest_api_handle(self, dInputBody, schemapath):
        logger.debug('delete_rest_api_handle: XPATH:%s JSON_ARRAY: %s', schemapath, dInputBody)
        lrpcAndHw = isdklib.isdk_convert_restapi2rpc(dInputBody, schemapath, 'DELETE')
        
        if lrpcAndHw == []:
            logger.debug('POST REST API to RPC conversion failed: Return NIL value')
            return ''
        
        srpc = lrpcAndHw[0]
        shwcontext = lrpcAndHw[1]
        sRollback = lrpcAndHw[2]        
        
        if srpc == '':
            logger.debug('DELETE REST API to RPC conversion failed: Return NIL value')
            return ''
        
        if shwcontext == '':
            logger.debug('DELETE REST API hwcontext: not available')
#             return ''
        
        logger.debug('DELETE RPC request generated: %s',srpc)
        logger.debug('DELETE ,hwcontext : %s',shwcontext)
        srpcstring = '&'.join([sRollback,srpc])
        srpcreplystring = isdklib.isdk_sendrecv_ncclient(self._m, srpcstring,shwcontext,'DELETE')
        if srpcreplystring == '':
            logger.debug('Edit-config (delete) rpc send request and receive reply  failed')
            return ''
        logger.debug('Edit-config (delete) rpc reply: %s',srpcreplystring)
        return isdklib.isdk_convert_rpc2restapi(srpcreplystring, schemapath, 'DELETE') 
    
    def get_rest_api_handle(self, dInputBody, schemapath):

        if schemapath.find('_restping')!= -1:
            logger.debug('get_rest_api_handle : REST PING TEST')               
            if not self._m.session_id is None:
                logger.debug('get_rest_api_handle: Session_ID : %s , ', self._m.session_id)
                logger.debug('get_rest_api_handle : REST PING TEST : success')                      
                return '<restping>pinging success</restping>'
            logger.debug('get_rest_api_handle : REST PING TEST : failed')
            return '<restping>pinging failed</restping>'
        
        ltemp = schemapath.split('/')
        sdiscoverFlag = ltemp[len(ltemp)-1]
        if 'discover-enable' == sdiscoverFlag:
            ltemp.pop()
            schemapath = '/'.join(ltemp)
        else:
            schemapath = '/'.join(ltemp)
        lrpcAndHw = isdklib.isdk_convert_restapi2rpc(dInputBody, schemapath, 'GET')
        
        if lrpcAndHw == []:
            logger.debug('POST REST API to RPC conversion failed: Return NIL value')
            return ''
        
        srpcstring = lrpcAndHw[0]
        shwcontext = lrpcAndHw[1]
        
        if srpcstring == '':
            logger.debug('get_rest_api_handle, REST API TO RPC Request conversion failed: Return NIL value')
            return ''
        
        if shwcontext == '':
            logger.debug('GET, hwcontext: not available')
        
        logger.debug('GET,  RPC request generated: %s',srpcstring)
        logger.debug('GET,  hwcontext value: %s',shwcontext)
        
        

        srpcreplystring = isdklib.isdk_sendrecv_ncclient(self._m, srpcstring,shwcontext,'GET')
        if srpcreplystring == '':
            logger.debug('get_rest_api_handle, GET rpc send request and receive reply  failed')
            return ''
        
        if 'discover-enable' == sdiscoverFlag:
            return selflearn.isdk_process_rpcreply(srpcreplystring,schemapath)
        else:
            return isdklib.isdk_convert_rpc2restapi(srpcreplystring, schemapath, 'GET')

    def getconfig_rest_api_handle(self, dInputBody, schemapath):
        logger.debug('getconfig_rest_api_handle: XPATH:%s JSON_ARRAY: %s', schemapath, dInputBody)
        srpcstring = ''
        shwcontext = ''
        lrpcAndHw = isdklib.isdk_convert_restapi2rpc(dInputBody, schemapath, 'GETCONFIG')
        if lrpcAndHw == []:
            logger.debug('POST REST API to RPC conversion failed: Return NIL value')
            return ''
        srpcstring = lrpcAndHw[0]
        shwcontext = lrpcAndHw[1]
        if srpcstring == '':
            logger.debug('getconfig_rest_api_handle, REST API TO RPC Request conversion failed: Return NIL value')
            return ''
        if shwcontext == '':
            logger.debug('GETCONFIG, hwcontext: not available')
        logger.debug('GETCONFIG,  RPC request generated: %s',srpcstring)
        logger.debug('GETCONFIG,  hwcontext value: %s',shwcontext)
        srpcreplystring = isdklib.isdk_sendrecv_ncclient(self._m, srpcstring,shwcontext,'GETCONFIG')
        if srpcreplystring == '':
            logger.debug('getconfig_rest_api_handle, GET rpc send request and receive reply  failed')
            return ''
        return isdklib.isdk_convert_rpc2restapi(srpcreplystring, schemapath, 'GETCONFIG') 

    def action_rest_api_handle(self, dInputBody, lschema): 
        
        lschema.pop(1)
        schemapath = '/'.join(lschema)
        logger.debug('action_rest_api_handle: XPATH:%s', schemapath)
        for k,v in dInputBody.items():
            logger.debug('action_rest_api_handle: dInputBody key:%s Value: %s', k, v)
        srpcstring = ''
        shwcontext = ''
        lrpcAndHw = isdklib.isdk_convert_restapi2rpc(dInputBody, schemapath,'ACTION')
        
        if lrpcAndHw == []:
            logger.debug('ACTION SCHEMA REST API to RPC conversion failed: Return NIL value')
            return ''
        
        srpcstring = lrpcAndHw[0]
        shwcontext = lrpcAndHw[1]        
        
        if srpcstring == '':
            logger.debug('ACTION SCHEMA REST API to RPC conversion failed: Return NIL value')
            return ''
        
        if shwcontext == '':
            logger.debug('ACTION SCHEMA REST API hwcontext:not available')
        
        logger.debug('ACTION SCHEMA  RPC request generated: %s',srpcstring)
        logger.debug('ACTION SCHEMA  hwcontext value: %s',shwcontext)
        
        
        srpcreplystring = isdklib.isdk_sendrecv_ncclient(self._m, srpcstring,shwcontext,'ACTION')
        if srpcreplystring == '':
            logger.debug('ACTION SCHEMA rpc send request and receive reply  failed')
            return ''
        logger.debug('ACTION SCHEMA (create) rpc reply: %s',srpcreplystring)    
        return isdklib.isdk_convert_rpc2restapi(srpcreplystring, schemapath, 'ACTION') 

    def copyconfig_rest_api_handle(self, dInputBody, lschema):
        schemapath = '/'.join(lschema) 
        logger.debug('copyconfig_rest_api_handle: XPATH:%s', schemapath)
        for k,v in dInputBody.items():
            logger.debug('copyconfig_rest_api_handle: dInputBody key:%s Value: %s', k, v)
        srpcTarget = ''
        srpcSource = ''
        shwcontext = ''
        
        lrpcAndHw = isdklib.isdk_convert_restapi2rpc(dInputBody, schemapath,'COPYCONFIG')
        
        if lrpcAndHw == []:
            logger.debug('COPY-CONFIG REST API to RPC conversion failed: Return NIL value')
            return ''

        srpcTarget = lrpcAndHw[0]
        srpcSource = lrpcAndHw[1]
        shwcontext = lrpcAndHw[2]        
        
        if srpcTarget == '' and srpcSource == '':
            logger.debug('COPY-CONFIG REST API to RPC conversion failed: Return NIL value')
            return ''
        
        if shwcontext == '':
            logger.debug('COPY-CONFIG REST API hwcontext:not available')
        
        logger.debug('COPY-CONFIG  RPC request generated: %s',srpcTarget)
        logger.debug('COPY-CONFIG  RPC request generated: %s',srpcSource)
        logger.debug('COPY-CONFIG  hwcontext value: %s',shwcontext)
        
        srpcstring = '&'.join([srpcTarget,srpcSource])
        srpcreplystring = isdklib.isdk_sendrecv_ncclient(self._m, srpcstring,shwcontext,'COPYCONFIG')
        if srpcreplystring == '':
            logger.debug('COPY-CONFIG rpc send request and receive reply  failed')
            return ''
        logger.debug('COPY-CONFIG (save) rpc reply: %s',srpcreplystring)    
        return isdklib.isdk_convert_rpc2restapi(srpcreplystring, schemapath, 'COPYCONFIG') 

    def deleteconfig_rest_api_handle(self, dInputBody, lschema):
        schemapath = '/'.join(lschema) 
        logger.debug('deleteconfig_rest_api_handle: XPATH:%s', schemapath)
        for k,v in dInputBody.items():
            logger.debug('deleteconfig_rest_api_handle: dInputBody key:%s Value: %s', k, v)
        srpcTarget = ''
        srpcSource = ''
        shwcontext = ''
        
        lrpcAndHw = isdklib.isdk_convert_restapi2rpc(dInputBody, schemapath,'DELETECONFIG')
        
        if lrpcAndHw == []:
            logger.debug('DELETE-CONFIG REST API to RPC conversion failed: Return NIL value')
            return ''

        srpcTarget = lrpcAndHw[0]
        shwcontext = lrpcAndHw[1]

        if srpcTarget == '':
            logger.debug('DELETE-CONFIG REST API to RPC conversion failed: Return NIL value')
            return ''
        
        if shwcontext == '':
            logger.debug('DELETE-CONFIG REST API hwcontext:not available')
        
        logger.debug('DELETE-CONFIG  RPC request generated: %s',srpcTarget)
        logger.debug('DELETE-CONFIG hwcontext value: %s',shwcontext)
        
        srpcreplystring = isdklib.isdk_sendrecv_ncclient(self._m, srpcTarget,shwcontext,'DELETECONFIG')

        if srpcreplystring == '':
            logger.debug('DELETE-CONFIG rpc send request and receive reply  failed')
            return ''
        logger.debug('DELETE-CONFIG (save) rpc reply: %s',srpcreplystring)    
        return isdklib.isdk_convert_rpc2restapi(srpcreplystring, schemapath, 'DELETECONFIG') 

    def killsession_rest_api_handle(self, dInputBody, lschema):

        schemapath = '/'.join(lschema) 
        logger.debug('killsession_rest_api_handle: XPATH:%s', schemapath)
        for k,v in dInputBody.items():
            logger.debug('killsession_rest_api_handle: dInputBody key:%s Value: %s', k, v)
        srpcsessId = ''
        srpcSource = ''
        shwcontext = ''
        
        lrpcAndHw = isdklib.isdk_convert_restapi2rpc(dInputBody, schemapath,'KILLSESSION')
        
        if lrpcAndHw == []:
            logger.debug('KILL-SESSION REST API to RPC conversion failed: Return NIL value')
            return ''

        srpcsessId = lrpcAndHw[0]
        shwcontext = lrpcAndHw[1]
        
        if srpcsessId == '':
            logger.debug('KILL-SESSION REST API to RPC conversion failed: Return NIL value')
            return ''
        
        if shwcontext == '':
            logger.debug('KILL-SESSION REST API hwcontext:not available')
        
        logger.debug('KILL-SESSION  RPC request generated: %s',srpcsessId)
        logger.debug('KILL-SESSION  hwcontext value: %s',shwcontext)
        
        srpcreplystring = isdklib.isdk_sendrecv_ncclient(self._m, srpcsessId,shwcontext,'KILLSESSION')
        if srpcreplystring == '':
            logger.debug('KILL-SESSION rpc send request and receive reply  failed')
            return ''
        logger.debug('KILL-SESSION (save) rpc reply: %s',srpcreplystring)    
        return isdklib.isdk_convert_rpc2restapi(srpcreplystring, schemapath, 'KILLSESSION') 

##-------------------------------------------------------------------------------
##-- Class Name      : Process_Rest_Api
##-- Date Created    : 02-06-2014
##-- Author          : Vikash Kumar
##-- Description     : This  method will add the devices passed as parameter to the list.If all parameters and attributes are right
##--                   then it will return OK else NOT_OK
##-- Caution         :
##------------------------------------------------------------------------------
    def set_multi_ipaddress(self, deviceList):
        """
            Here We are first checking whether any connection already exists there or not
            If connection already exists then it will first close the connection else no problem
        """

        connectdevice = {'ip' : self.ip,
                'port' : self.port,
                'username' : self.username,
                'passwd' : self.password}


        isclosessh = True
        if (self.mainDevice == connectdevice):
            isclosessh = False

        for dDict in deviceList:
            if connectdevice == dDict :
                isclosessh = False

        if isclosessh and self.getStatus() == True:
            self.close()

        self.devices = []
        
        """
            If device list is empty or subdevices are not present or data type of elements in device list is
            not of dictionary type then return proper comment else add it in list
        """
        if not deviceList:
            logger.debug('Device List is empty ')       
            return None
        for dictionaries in deviceList:
            if not dictionaries:
                logger.debug('No dictionary present inside the device list ')   
                continue
            if not all(isinstance(dictionaries, dict) for elem in deviceList):
                logger.debug('Data type inside list is not same as dictionary ')
                return None
            self.devices.append(dictionaries)
            logger.debug(self.devices)     
        return "OK"
        
##-------------------------------------------------------------------------------
##-- Class Name      : Process_Rest_Api
##-- Date Created    : 02-06-2014
##-- Author          : Vikash Kumar
##-- Description     : This method will try to get ESN value of particular device if that value is present
##-- Caution         :
##------------------------------------------------------------------------------
    def get_esn(self):
        """
        Here we are getting rpc reply and from that reply we are calling isdk_ESN_parse_reply to get ESN Value
        """
        sUri = '/system'
        dInputBody = None
        srpcreplystring = self.get_rest_api_handle(dInputBody, sUri)
        sEsn = isdklib.isdk_ESN_parse_reply(srpcreplystring)
        if sEsn == 'error' or sEsn == "":
            logger.debug('NULL value or empty')
            return None
        else:
            logger.debug('ESN for the device : %s',sEsn)
            return sEsn
        return None
    
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



