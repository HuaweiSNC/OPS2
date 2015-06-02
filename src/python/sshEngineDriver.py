#!/usr/bin/env python  
# -*- coding: utf-8 -*-  
# Autor: xielequan

import config
import logging 
from rest_adapter import Rest_Adapter
logger = logging.getLogger("ops.sshEngine")
from process_adapter import Process_Adapter
import os
import paramiko
import json
import inspect 
from dao.urlmapping_mgmt import urlmapping_mgmt

try:
    from lxml import etree
except ImportError:
    import xml.etree.ElementTree as etree
    
from sshClient import SSHClient

##-------------------------------------------------------------------------------
##-- Class Name      : Process_Rest_Api
##-- Date Created    : 2015-3-24
##-- Author          : x00302603
##-- Description     : Class contains
##--                    a. Methods to open and close ssh session
##--                    b. Methods to handle REST api's (POST, PUT, DELETE GET)
##--                    c. Methods to handle example string
##--                    d. Methods to get the Status of ssh session
##--                    e. Methods to get the file of sqlite  db
##-- Caution         :
##------------------------------------------------------------------------------
class Process_Rest_Api(Rest_Adapter): 

    createid = 0
    instanceMap = {  }
    
    def __init__(self,ip,port=22,username="root123",password="Root@123", dbfilename=None):
        self.ip = ip
        self.port = port
        self.username = username
        self.password = password
        self.createid = self.createid+1
        self.cid = self.createid
        self.status = True
        self.errorinfo = ""
        if (dbfilename == None):
            self.dbfile = self.getUrlmappingClass()
        else :
            self.dbfile = dbfilename
        
        self.sshEngine = SSHClient(ip, port, username, password) 
        
        try:   
            self.sshEngine.connect()
            self.status = self.sshEngine.getStatus()
            logger.debug('client session creation is successful ')
        except Exception as e: 
            self.status = False
            self.errorinfo = e
            logger.error('client session creation is failed. error: %s ', self.errorinfo)  
        logger.info('create sshEngine %s, ip:%s, port:%s, username:%s '% (self.cid ,self.ip, self.port, self.username))
        
    def getUrlmappingClass(self):
        stack = inspect.stack()
        stacklocal = stack[4][0]
        
        return stacklocal.f_globals['dbfile']

    def getInstance(self, filename):
        mod = None
        if (self.instanceMap.has_key(filename)):
            mod = self.instanceMap.get(filename)
        else:
            mod = __import__(filename)
            self.instanceMap[filename] = mod
            logger.info (' renew process class %s' % (filename))

        if (mod == None) :
            return None
        
        components = filename.split('.')
        for comp in components[1:]:
            mod = getattr(mod, comp)
           
        classObj = mod.Rest_Process(self.sshEngine)
        assert isinstance(classObj, Process_Adapter)
        return classObj
        
    def getFileName(self, schemapath):
        import re
        processUrlfileName = None
        urlmappingClass = urlmapping_mgmt(None,self.dbfile)
        templateMap = urlmappingClass.find_urlmappingbygroup("sshengine");
        if (templateMap == None) :
            return None
        for elem in templateMap:  
            urlpath = elem.get("uriregular")   
            fileName = elem.get("modulename")   
            #fileName = self.templateMap[elem]
            result = re.match(urlpath, schemapath)
            if (result != None):
                processUrlfileName = fileName 
                break
        return processUrlfileName

    def __exit__(self):
        self.close()
        logger.debug('close cid:%s, ip:%s, port:%s, username:%s '% (self.cid ,self.ip, self.port, self.username))   
    
    def getStatus(self):
        logger.debug('getStatus() cid:%s '% (self.cid)) 
        self.status = self.sshEngine.getStatus()  
        return self.status
    
    def close(self):
        self.sshEngine.disconnect
    
    def reconnect(self): 
        self.sshEngine.reconnect()
        return True
     
    def getBodyType(self, dInputBody):
        
        isIpBodyJsonType = False
        isIpBodyXMLType = False 
        isIpBodyTextType = False 
        for k,v in dInputBody.items():
            if k == config.ISDK_JSON_IP_BODY:
                if v != None:
                    isIpBodyJsonType = True
            elif k == config.ISDK_XML_IP_BODY:
                if v != None:
                    isIpBodyXMLType = True
            elif k == config.ISDK_TEXT_IP_BODY:
                if v != None:
                    isIpBodyTextType = True
        return isIpBodyJsonType,isIpBodyXMLType, isIpBodyTextType
        
    def getBody(self, dInputBody):
        
        isIpBodyJsonType, isIpBodyXMLType, isIpBodyTextType =  self.getBodyType(dInputBody)
        executetext = ''
        bodytype = "text"
        if isIpBodyJsonType == True:
            bodytype="json"
            executetext = dInputBody[config.ISDK_JSON_IP_BODY]
        
        elif isIpBodyXMLType == True:
            bodytype="xml"
            executetext = dInputBody[config.ISDK_XML_IP_BODY]
            
        elif isIpBodyTextType == True:
            bodytype="text"
            executetext = dInputBody[config.ISDK_TEXT_IP_BODY]
        return bodytype,executetext
        
    def rest_api_handle(self, method, dInputBody, schemapath):
        
        logger.debug('post: cid:%d, XPATH:%s, body:%s'% (self.cid, schemapath, dInputBody))
        
        lrestApiPath = schemapath.split('/')
        lrestApiPath.pop(0)  
        strschemapath  = '/'.join(lrestApiPath) 
        buildApiPath = lrestApiPath.pop(0)
     
        if  buildApiPath == None:
            raise Exception('only accept URL path /apiname .')
        
        if ((buildApiPath == "example") or (buildApiPath == "help")):
            return self.get_example_str()

        successReport = etree.Element('success')
        errorReport = etree.Element('error')
  
        bodytype, executetext = self.getBody(dInputBody)
 
        instanceClass = None
        processFileName = self.getFileName(strschemapath)
        if (processFileName != None):
            instanceClass = self.getInstance(processFileName)
            
        # execute process from filename 
        err = ""
        output = ""
        if (instanceClass != None):
            output, err = instanceClass.process(method, strschemapath, bodytype, executetext)
        else :
            #executetext = executetext.replace('\r\n', ';')
            #executetext = executetext.replace('\n', ';')
            #output, err = self.sshEngine.exec_cmd(executetext)
            raise NotImplementedError

        logger.debug('cid: %d run end'% (self.cid))
        if ("" != err):
            errorReport.text = err
            return err
            #return etree.tostring(errorReport, pretty_print=True)
        
        successReport.text = output
        return output
        #return etree.tostring(successReport, pretty_print=True)
        
    def post_rest_api_handle(self, dInputBody, schemapath):
        return self.rest_api_handle("POST", dInputBody, schemapath)

    def put_rest_api_handle(self, dInputBody, schemapath):
        return self.rest_api_handle("PUT", dInputBody, schemapath)

    def delete_rest_api_handle(self, dInputBody, schemapath):
        return self.rest_api_handle("DELETE", dInputBody, schemapath)

    def get_rest_api_handle(self, dInputBody, schemapath):
        return self.rest_api_handle("GET", dInputBody, schemapath)
       
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
        childCfgElement.text = "/exec"
        childCfgElement = etree.SubElement(cfgElement, 'Method')
        childCfgElement.text = "POST|PUT"
 
        childCfgElement = etree.SubElement(cfgElement, 'Body')
        childCfgElement.text = 'ovs-vsctl show'
        childCfgElement = etree.SubElement(cfgElement, 'Description')
        childCfgElement.text = "execute ovs-vsctl show with username and password "
        
        # example of Connect tsu
        cfgElement = etree.SubElement(examples, 'example')
        childCfgElement = etree.SubElement(cfgElement, 'URL')
        childCfgElement.text = "/example"
        childCfgElement = etree.SubElement(cfgElement, 'Method')
        childCfgElement.text = "GET"
    
        childCfgElement = etree.SubElement(cfgElement, 'Body')
        childCfgElement.text = ''
        childCfgElement = etree.SubElement(cfgElement, 'Description')
        childCfgElement.text = "get a examples !!! "
        
        return etree.tostring(examples, pretty_print=True)
    
if __name__ == '__main__':
    server_ip = '10.110.139.189'
    server_user = 'root'
    server_passwd = 'passw0rd'
    server_port = 22
    DBPath=os.getcwdu()
    from plugin.bootle_sqlite import SQLitePlugin
    dbfile='%s%sOPS2.db' % (DBPath, os.sep)
    sqlite_plugin=SQLitePlugin(dbfile)
    classObj = Process_Rest_Api(server_ip, server_port, server_user, server_passwd, dbfile) 
      
    #schemapath = '6/TgTsuAdd?fixed_params=LAN-1002,10.137.222.217'
    schemapath = '6/inventory/interfaces/interface?portID=tapf89b9d66-8e'
 
    dInputBody ={ 
               'text_input':"dir"
               }
    jsonObj = classObj.get_rest_api_handle(dInputBody, schemapath) 
    #jsonObj = classObj.get_rest_api_handle(dInputBody, schemapath) 
#     jsonObj = classObj._m.poweroff_machine()

    print '\n POST Output JSON object:\n',jsonObj
    

    classObj.__exit__()

