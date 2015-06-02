#!/usr/bin/python
# coding=UTF-8
import config
import logging 
import re
from json import *

try:
    from lxml import etree
except ImportError:
    import xml.etree.ElementTree as etree


# create logger 
logger = logging.getLogger("ops.flowLimit") 

from process_adapter import Process_Adapter

class Rest_Process(Process_Adapter):
    
    def __init__(self, sshEngine):
        self.ssh = sshEngine
        self.errorxml = \
'''<rpc-error xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0">
    <error-type>application</error-type>
    <error-tag>bash</error-tag>
    <error-message>%s</error-message>
</rpc-error>'''
        self.okXml = '<ok/>'
        
    
    def parseDeleteInfo(self, apipath, bodytype, body):
        portList = []
        err = ''
        delType = {'direction':''}
        strlist = apipath.split('&')
        for index in range(len(strlist)):
            equalMarkIndex = strlist[index].find('=')
            if (equalMarkIndex == -1):
                err = 'url is error '
                return portList,delType,err
            key = strlist[index][0:equalMarkIndex].strip()
            value = strlist[index][equalMarkIndex+1:len(strlist[index])].strip()
            
            if (index == 0):
                keyList = key.split('?')
                if len(keyList)>1:
                    key = keyList[1]
                else:
                    err = 'url is error '
                    return portList,delType,err
                
            if (key != "portID") and (key != "direction"):
                err = 'url is error '
                logger.error("key = %s",key)
                return portList,delType,err
            if index == 0:
                portList.append(value)
            else:
                if key == "portID":
                    portList.append(value)
                else:
                    delType[key] = value

        return portList,delType,err
    
    def clearPortConfig(self, portList,delType):
        ruuid = r'[0-9a-z]{8}-[0-9a-z]{4}-[0-9a-z]{4}-[0-9a-z]{4}-[0-9a-z]{12}'
        text,err= '',''
        if len(portList) == 0:
            err = "portID is empty"
            err = self.errorxml%(err)
            logger.debug(err)
            return text,err 
        direction = delType['direction']    
        if direction == '':
            for portID in portList:
                logger.debug(portID)
                if re.match(ruuid, portID.replace(" ","")) == None:
                    err = "portID is error"
                    err = self.errorxml%(err)
                    return '',err
                
                portID = JSONEncoder().encode(portID)
                command = 'evs-vsctl evs_set_qos '  + '\'' + portID  + '\'' + ' ' + str(0) + ' ' + str(0)
                logger.debug(command)

                text, err = self.ssh.exec_cmd(command)
                if (err != ""):
                    logger.error(err)
                    err = self.errorxml%(err)
                    return text,err
                
                command = 'evs-vsctl evs_set_qos '  + '\'' + portID  + '\'' + ' ' + str(0) + ' ' + str(1)
                logger.debug(command)

                text, err = self.ssh.exec_cmd(command)
                if (err != ""):
                    logger.error(err)
                    err = self.errorxml%(err)
                    return text,err
        else:
            portID = portList[0]
            if re.match(ruuid, portID.replace(" ","")) == None:
                err = "portID is error"
                err = self.errorxml%(err)
                return '',err
                
            portID = JSONEncoder().encode(portID)
            command = 'evs-vsctl evs_set_qos ' + '\'' + portID  + '\'' + ' ' + str(0) + ' ' + direction
            logger.debug(command)

            text, err = self.ssh.exec_cmd(command)
            if (err != ""):
                logger.error(err)
                err = self.errorxml%(err)
                return text,err  
        return self.okXml, err
    
    def parsePostInfo(self, apipath, bodytype, body):
        inputParameterList = []
        inputParameter = {'portID':'','a2z-cir':'','z2a-cir':''}
        err = ''
        body = "<cars>" + body + "</cars>"
      
        root = etree.fromstring(body)
        flowLimitNodeList = root.findall('car')
        for flowLimitNode in flowLimitNodeList:
            flowLimitChildList = flowLimitNode.getchildren()
            inputParameter = {'portID':'','a2z-cir':'','z2a-cir':''}
            for flowLimitChild in flowLimitChildList :
                tag = flowLimitChild.tag.strip()
                if ((tag != "portID") and (tag != "a2z-cir") and (tag != "z2a-cir") 
                    and (tag != "a2z-pir") and (tag != "z2a-pir") and (tag != "a2z-cbs")
                    and (tag != "z2a-cbs") and (tag != "a2z-pbs") and (tag != "z2a-pbs")):
                    err = 'xml format is error'
                    return inputParameterList,err
                else:
                    if inputParameter.has_key(tag):
                        if inputParameter[tag] != '':
                            err = 'xml format is error'
                            return inputParameterList,err
                        if flowLimitChild.text == '':
                            err = 'xml format is error'
                            return inputParameterList,err
                        value = flowLimitChild.text.strip()
                        inputParameter[tag] = value
            inputParameterList.append(inputParameter)
        return inputParameterList,err
        
    def configPort(self, inputParameterList):
        ruuid = r'[0-9a-z]{8}-[0-9a-z]{4}-[0-9a-z]{4}-[0-9a-z]{4}-[0-9a-z]{12}'
        text,err= '',''

        for index in range(len(inputParameterList)):
            inputParameter = inputParameterList[index]

            portID = inputParameter['portID']
            a2zcir = inputParameter['a2z-cir']
            z2acir = inputParameter['z2a-cir']
            
            #check all the parameter except interfaceId
            if portID == '':
                err = "portID is empty"
                err = self.errorxml%(err)
                return text,err
            
            if re.match(ruuid, portID.replace(" ","")) == None:
                err = "portID is error"
                err = self.errorxml%(err)
                return '',err
            
            if (a2zcir == '' and z2acir == ''):
                err = "both a2z-cir and z2a-cir are empty"
                err = self.errorxml%(err)
                return text,err
            
            portID = JSONEncoder().encode(portID)
            if(a2zcir != ''):
                command = 'evs-vsctl evs_set_qos ' + '\''+ portID + '\''+ ' ' + a2zcir + ' ' + str(0)
                logger.debug(command)

                text, err = self.ssh.exec_cmd(command)
               
                if (err != ""):
                    logger.error(err)
                    err = self.errorxml%(err)
                    return text,err
                
            if(z2acir != ''):
                command = 'evs-vsctl evs_set_qos ' + '\''+ portID + '\''+ ' ' + z2acir + ' ' + str(1)
                logger.debug(command)

                text, err = self.ssh.exec_cmd(command)
        
                if (err != ""):
                    logger.error(err)
                    err = self.errorxml%(err)
                    return text,err
                
        return self.okXml,err

        
    def process(self, method, apipath, bodytype, body):
        
        inputMsg = "method == %s"%method + " apipath == %s"%apipath + " bodytype == %s"%bodytype + " body == %s"%str(body)
        logger.debug(inputMsg)

        text,err= '',''
        portList = []
        delType = {}

   
        if "GET" == method:
            return text,err
        elif "POST" == method:
            #Get input parameter from xml 
            inputParameterList,err = self.parsePostInfo(apipath, bodytype, body)
            if err != '':
                err = self.errorxml%(err)
                return text,err
            text,err = self.configPort(inputParameterList)
            return text,err
        elif "PUT" == method:
            return text,err
        elif "DELETE" == method:
            #Get input parameter from url
            portList,delType,err = self.parseDeleteInfo(apipath, bodytype, body)
            if err != '':
                err = self.errorxml%(err)
                return text,err
            text,err = self.clearPortConfig(portList,delType)
            return text,err
        else:
            err = "request method is error"
            err = self.errorxml%(err)
            return text,err
        
if __name__ == "__main__":
    pass


    
        
