#!/usr/bin/env python  
# -*- coding: utf-8 -*-  
# Autor: xielequan

import config
import logging 
from rest_adapter import Rest_Adapter
logger = logging.getLogger("ops.testEngine")  

import json
try:
    from lxml import etree
except ImportError:
    import xml.etree.ElementTree as etree
    
from testcontroller import TestEngineController

##-------------------------------------------------------------------------------
##-- Class Name      : Process_Rest_Api
##-- Date Created    : 04-03-2013
##-- Author          : x00302603
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
        self.testEngine = TestEngineController(ip, port=port) 
        
        logger.info('add testEngine %s, ip:%s, port:%s, username:%s '% (self.cid ,self.ip, self.port, self.username))     

    def __exit__(self):
#         print '__exit__'
        logger.debug(' __exit__ cid:%s, ip:%s, port:%s, username:%s '% (self.cid ,self.ip, self.port, self.username))   
    
    def getStatus(self):
        logger.debug('getStatus() cid:%s '% (self.cid))   
        return self.status
    
    def close(self):
        pass
    
    def reconnect(self): 
        return True
    
    def post_rest_api_handle(self, dInputBody, schemapath):
        
        logger.debug('post: cid:%d, XPATH:%s, body:%s'% (self.cid, schemapath, dInputBody))
 
        ##  <device id>/_action/ftpc/ftpcTransferFiles/ftpcTransferFile
        sactionflag, testApi = schemapath.split('/')
        lrestApiPath = schemapath.split('/')
        lrestApiPath.pop(0)   
      
        isIpBodyJsonType = False
        isIpBodyXMLType = False 
        for k,v in dInputBody.items():
            if k == config.ISDK_JSON_IP_BODY:
                if v != None:
                    isIpBodyJsonType = True
            elif k == config.ISDK_XML_IP_BODY:
                if v != None:
                    isIpBodyXMLType = True
  
    
        if  testApi == None or testApi == None:
            raise Exception('only accept URL path /apiname .')
        
        successReport = etree.Element('success')
        errorReport = etree.Element('rpc-error')
        errorCfgElement = None
        result = None
        bret = 1
        
        tsuid = None
        tsuPort = None
        fixed_params = []
        option_params = {}
        for uiCount in range(len(lrestApiPath)):
            lelement = lrestApiPath[uiCount].split('?')
            if len(lelement) == 2:
                testApi = lelement[0]
                lqueryElem = lelement[1].split('&')
                ##print(lqueryElem)
                for liter in lqueryElem:
                    litems = liter.split('=')
                    tsuArgName = litems[0] 
                    tsuArgValue = litems[1] 
                    if (tsuArgName == 'port'):
                        tsuPort = tsuArgValue
                    elif (tsuArgName == 'fixed_params'):
                        arrfixeds = tsuArgValue.split(',')
                        for liter in arrfixeds:
                            fixed_params.append(liter)
                    elif (tsuArgName == 'tsuid'):
                        tsuid = tsuArgValue
                    else:
                        option_params[tsuArgName] = tsuArgValue
                
                
            elif len(lelement) == 1:
                testApi = lrestApiPath[uiCount]
            else:
                pass     
            
        
        lcontent={}
        
        if isIpBodyJsonType == True:
                json_array = dInputBody[config.ISDK_JSON_IP_BODY]
                for lcontent in json_array:
                    tsuid = lcontent.get('tsuid') 
                    tsuPort = lcontent.get('port')  
                    fixed_params = lcontent.get('fixed_params') 
                    option_params = lcontent.get('option_params') 
                    bret, result = self.testEngine.send(testApi, tsuid,  tsuPort, fixed_params, option_params)
                    if bret != '0' :
                        errorCfgElement = etree.SubElement(errorReport, 'error-type')
                        errorCfgElement.text = 'application'
                        errorCfgElement = etree.SubElement(errorReport, 'error-message')
                        errorCfgElement.text = result
        
        elif isIpBodyXMLType == True:
                sXmlInput = dInputBody[config.ISDK_XML_IP_BODY]
                raise Exception('only accept JSON Format body .')
         
        logger.debug('cid:%d isdk_convert_rpc2restapi()'% (self.cid))
         
        if (errorCfgElement != None):
            return etree.tostring(errorReport, pretty_print=True)
       
        retCfgElement = etree.SubElement(successReport, 'response')
        retCfgElement.text = result
        return etree.tostring(successReport, pretty_print=True)

    def put_rest_api_handle(self, dInputBody, schemapath):
        return self.post_rest_api_handle(dInputBody, schemapath)

    def delete_rest_api_handle(self, dInputBody, schemapath):
        
        logger.debug('post: cid:%d, XPATH:%s, body:%s'% (self.cid, schemapath, dInputBody))
 
        ##  <device id>/_action/ftpc/ftpcTransferFiles/ftpcTransferFile
        lschema, testApi = schemapath.split('/')
        lrestApiPath = schemapath.split('/')
        lrestApiPath.pop(0)   
        if testApi == None:
            raise Exception('only accept URL path /stream/apiname?arg1=xxx&arg2=yyy .')
    
        tsuid = None
        tsuPort = None
        fixed_params = []
        option_params = {}
        
        for uiCount in range(len(lrestApiPath)):
            lelement = lrestApiPath[uiCount].split('?')
            if len(lelement) == 2:
                testApi = lelement[0]
                lqueryElem = lelement[1].split('&')
                ##print(lqueryElem)
                for liter in lqueryElem:
                    litems = liter.split('=')
                    tsuArgName = litems[0] 
                    tsuArgValue = litems[1] 
                    if (tsuArgName == 'port'):
                        tsuPort = tsuArgValue
                    elif (tsuArgName == 'fixed_params'):
                        arrfixeds = tsuArgValue.split(',')
                        for liter in arrfixeds:
                            fixed_params.append(liter)
                    elif (tsuArgName == 'tsuid'):
                        tsuid = tsuArgValue
                    else:
                        option_params[tsuArgName] = tsuArgValue
            elif len(lelement) == 1:
                testApi = lrestApiPath[uiCount]
            else:
                pass     
            
        if testApi == None:
            raise Exception('only accept URL path /stream/apiname?arg1=xxx&arg2=yyy .')
    
        if (testApi.find("Clear") ==-1 
             and testApi.find("Remove") == -1 
             and testApi.find("Del") == -1 
             and testApi.find("Disable") == -1 
             and testApi.find("Disconnect") == -1 
             and testApi.find("Delete") == -1) :
            raise Exception('only accept URL path  *Clear* | *Remove* | *Delete* | *Disable* | *Del* | *Disconnect*') 
    
        # send request to testEngine
        bret, result = self.testEngine.send(testApi, tsuid, tsuPort, fixed_params, option_params)
        
        successReport = etree.Element('success')
        errorReport = etree.Element('rpc-error')
        if (bret != '0'):
            errorCfgElement = etree.SubElement(errorReport, 'error-type')
            errorCfgElement.text = 'application'
            errorCfgElement = etree.SubElement(errorReport, 'error-message')
            errorCfgElement.text = result
            return etree.tostring(errorReport, pretty_print=True)

        retCfgElement = etree.SubElement(successReport, 'response')
        retCfgElement.text = result
        return etree.tostring(successReport, pretty_print=True)

        
    def get_rest_api_handle(self, dInputBody, schemapath):
        
        logger.debug('post: cid:%d, XPATH:%s, body:%s'% (self.cid, schemapath, dInputBody))
 
        ##  <device id>/_action/ftpc/ftpcTransferFiles/ftpcTransferFile
        lschema, testApi = schemapath.split('/')
        lrestApiPath = schemapath.split('/')
        lrestApiPath.pop(0)   
        if testApi == None:
            raise Exception('only accept URL path /stream/apiname?arg1=xxx&arg2=yyy .')
    
        tsuid = None
        tsuPort = None
        fixed_params = []
        option_params = {}
        
        for uiCount in range(len(lrestApiPath)):
            lelement = lrestApiPath[uiCount].split('?')
            if len(lelement) == 2:
                testApi = lelement[0]
                lqueryElem = lelement[1].split('&')
                ##print(lqueryElem)
                for liter in lqueryElem:
                    litems = liter.split('=')
                    tsuArgName = litems[0] 
                    tsuArgValue = litems[1] 
                    if (tsuArgName == 'port'):
                        tsuPort = tsuArgValue
                    elif (tsuArgName == 'fixed_params'):
                        arrfixeds = tsuArgValue.split(',')
                        for liter in arrfixeds:
                            fixed_params.append(liter)
                    elif (tsuArgName == 'tsuid'):
                        tsuid = tsuArgValue
                    else:
                        option_params[tsuArgName] = tsuArgValue
                
                
            elif len(lelement) == 1:
                testApi = lrestApiPath[uiCount]
            else:
                pass     
            
        if testApi == None:
            raise Exception('only accept URL path /stream/apiname?arg1=xxx&arg2=yyy .')
        
        if (testApi == "example"):
            return self.get_example_str()
    
        # send request to testEngine
        bret, result = self.testEngine.send( testApi, tsuid, tsuPort, fixed_params, option_params)
        
        successReport = etree.Element('success')
        errorReport = etree.Element('rpc-error')
        if (bret != '0'):
            errorCfgElement = etree.SubElement(errorReport, 'error-type')
            errorCfgElement.text = 'application'
            errorCfgElement = etree.SubElement(errorReport, 'error-message')
            errorCfgElement.text = result
            return etree.tostring(errorReport, pretty_print=True)

        retCfgElement = etree.SubElement(successReport, 'response')
        retCfgElement.text = result
        return etree.tostring(successReport, pretty_print=True)
       
    def set_main_device(self, ipaddress, port, username , password):
        pass
    
    def get_esn(self):
        return ''
    
    def set_multi_ipaddress(self, deviceList):
        pass

    def get_example_str(self):
        
        examples = etree.Element('examples')
        # example of  tsu add 
        cfgElement = etree.SubElement(examples, 'example')
        childCfgElement = etree.SubElement(cfgElement, 'URL')
        childCfgElement.text = "/TgTsuAdd"
        childCfgElement = etree.SubElement(cfgElement, 'Method')
        childCfgElement.text = "POST"
        json_array = [
            {
                "tsuid" : None,
                "port": None,
                "fixed_params": [
                    "LAN-1002",
                    "10.137.222.217" 
                ],
                "option_params": {}
            }
        ]
        childCfgElement = etree.SubElement(cfgElement, 'Body')
        childCfgElement.text = json.dumps(json_array,sort_keys=True,indent=4)
        childCfgElement = etree.SubElement(cfgElement, 'Description')
        childCfgElement.text = "Add a new Test Unit "
        
        # example of Connect tsu
        cfgElement = etree.SubElement(examples, 'example')
        childCfgElement = etree.SubElement(cfgElement, 'URL')
        childCfgElement.text = "/TgTsuConnect"
        childCfgElement = etree.SubElement(cfgElement, 'Method')
        childCfgElement.text = "POST"
        json_array = [
            {
                "tsuid" : None 
            }
        ]
        childCfgElement = etree.SubElement(cfgElement, 'Body')
        childCfgElement.text = json.dumps(json_array,sort_keys=True,indent=4)
        childCfgElement = etree.SubElement(cfgElement, 'Description')
        childCfgElement.text = "Connect a tsu "
        
        # example of TgTsuGetAll 
        cfgElement = etree.SubElement(examples, 'example')
        childCfgElement = etree.SubElement(cfgElement, 'URL')
        childCfgElement.text = "/TgTsuGetAll"
        childCfgElement = etree.SubElement(cfgElement, 'Method')
        childCfgElement.text = "Get"
        childCfgElement = etree.SubElement(cfgElement, 'Body')
        childCfgElement.text = "NA"
        childCfgElement = etree.SubElement(cfgElement, 'Description')
        childCfgElement.text = "Get List of TSU id "
        
        # example of TgTsuGet 
        cfgElement = etree.SubElement(examples, 'example')
        childCfgElement = etree.SubElement(cfgElement, 'URL')
        childCfgElement.text = "/TgTsuGetIpAddr?tsuid=1"
        childCfgElement = etree.SubElement(cfgElement, 'Method')
        childCfgElement.text = "Get"
        childCfgElement = etree.SubElement(cfgElement, 'Body')
        childCfgElement.text = "NA"
        childCfgElement = etree.SubElement(cfgElement, 'Description')
        childCfgElement.text = "Get TSU information "
        
        # example of TgTsuGet 
        cfgElement = etree.SubElement(examples, 'example')
        childCfgElement = etree.SubElement(cfgElement, 'URL')
        childCfgElement.text = "/TgTsuDisconnect?tsuid=1"
        childCfgElement = etree.SubElement(cfgElement, 'Method')
        childCfgElement.text = "DELETE"
        childCfgElement = etree.SubElement(cfgElement, 'Body')
        childCfgElement.text = "NA"
        childCfgElement = etree.SubElement(cfgElement, 'Description')
        childCfgElement.text = "Disconnect TSU information "
        
        # example of  tsu add 
        cfgElement = etree.SubElement(examples, 'example')
        childCfgElement = etree.SubElement(cfgElement, 'URL')
        childCfgElement.text = "/TgTsuSetEthernetLinkData"
        childCfgElement = etree.SubElement(cfgElement, 'Method')
        childCfgElement.text = "POST"
        json_array = [
            {
                "tsuid" : 1,
                "port": 1,
                "fixed_params": [ "60.1.1.2","60.1.1.1","24"],
                "option_params": {"ArpReply":"FALSE", "ArpKeepalive":"FALSE"}
            }
        ]
        childCfgElement = etree.SubElement(cfgElement, 'Body')
        childCfgElement.text = json.dumps(json_array,sort_keys=True,indent=4)
        childCfgElement = etree.SubElement(cfgElement, 'Description')
        childCfgElement.text = "Set Ethernet Link  "
        
        return etree.tostring(examples, pretty_print=True)
    
if __name__ == '__main__':
    s1='10.138.91.247'
    classObj = Process_Rest_Api(s1, port=55555) 
      
    #schemapath = '6/TgTsuAdd?fixed_params=LAN-1002,10.137.222.217'
    schemapath = '6/TgTsuConnect'
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

    json_array = [
            { 
                "tsuid": "1"
            }
        ]
#     json_array = [
#         {
#             "tsuid" : "1",
#             "port": "1",
#             "fixed_params": [
#                 "60.1.1.2",
#                 "60.1.1.1",
#                 "24"
#             ],
#             "option_params": {
#                 "ArpReply": "FALSE",
#                 "ArpKeepalive": "FALSE"
#             }
#         }
#     ]

    dInputBody ={'json_array':json_array,
               'xml_input':None
               }
    jsonObj = classObj.post_rest_api_handle(dInputBody, schemapath) 
    #jsonObj = classObj.get_rest_api_handle(dInputBody, schemapath) 
#     jsonObj = classObj._m.poweroff_machine()

    print '\n POST Output JSON object:\n',jsonObj

    classObj.__exit__()

