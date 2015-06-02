# -*- coding: utf-8 -*- 
#!/usr/bin/python


##----------------------------------------------------------------------------------------------------------------------
##-- Copyright (C) Huawei Technologies Co., Ltd. 2008-2011. All rights reserved.
##----------------------------------------------------------------------------------------------------------------------
##----------------------------------------------------------------------------------------------------------------------
##--Project Code    : ops2.1
##--File name       : portmirror.py
##--Author          :
##--Description     : File consist of user defined macro's
##----------------------------------------------------------------------------------------------------------------------
##--History:
##--Date                 Author                 Modification
##--03-20-2015            g00304937                 created file.
##----------------------------------------------------------------------------------------------------------------------

import config
import logging 
import re
from xml.etree import ElementTree
from xml.etree.ElementTree import Element  
 

# create logger 
logger = logging.getLogger("ops.portmirror") 

from process_adapter import Process_Adapter

class Rest_Process(Process_Adapter):
    
    def __init__(self, sshEngine):
        self.ssh = sshEngine
        self.result = ""
        self.err = ""
        self.cmd_template = " -- --id=@mirrorPortId%s get port %s -- --id=@observePortId%s get port %s -- --id=@m%s create Mirror name=%s"
        self.errorxml = \
'''<rpc-error xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0">
            <error-type>application</error-type>
            <error-tag>unknown-element</error-tag>
            <error-message>%s</error-message>
   </rpc-error>'''
        self.ruuid = r'[0-9a-z]{8}-[0-9a-z]{4}-[0-9a-z]{4}-[0-9a-z]{4}-[0-9a-z]{12}'        
    def process(self, method, apipath, bodytype, body):
            logger.debug("[process] starting \n")
            if("GET" == method):
                self.result, self.err = ("", "")
            elif("POST" == method):
                self.result, self.err = self.post_process(method, apipath, bodytype, body)
                logger.debug("[process] create port mirror result:\n %s \n",self.result)
                if self.err == "":
                    self.result = "<OK/>"
            elif("DELETE" == method):
                self.result, self.err = self.delete_process(method, apipath, bodytype, body)
                if self.err == "":
                    self.result = "<OK/>"
            elif("PUT" == method):
                self.result, self.err = ("", "")
            logger.debug("[process] ending \n")
            return self.result, self.err
    
    def post_process(self,method, apipath, bodytype, body):
        logger.debug("[post_process] input parameter method:%s, apipath:%s, bodytype:%s, body:%s \n",
                    method, apipath, bodytype, body)
        result,err = ("","")
        if str(body) == "":
            logger.error("no input body content ")
            err = self.errorxml%("no input body content ")
        comdline,err = self.parse_post_xml(method, apipath, bodytype, body)
        if(err == ""):
            result,err = self.ssh.exec_cmd(comdline)
        else:
            logger.error(err)
            err = self.errorxml%(err)
        logger.debug("[post_process] ending  \n")
        return result,err
    def delete_process(self,method, apipath, bodytype, body):
        logger.debug("[delete_process] starting  \n")
        result,err = ("","")
        comdline = "ovs-vsctl clear Bridge br-int mirrors"
        result,err = self.ssh.exec_cmd(comdline)
        logger.debug("[delete_process] ending  \n")
        return result,err
    
    def parse_post_xml(self,method, apipath, bodytype, body):
        logger.debug("[parse_post_xml] starting  \n")
        err = ""
        exe_cmd = "ovs-vsctl -- set Bridge br-int mirrors="
        mirrorPortId,observePortId,inenable,outenable,mirrorName = ("","","","","mymirror")
        if len(apipath.split("netmonitorPortMirror")) == 2 and apipath.split("netmonitorPortMirror")[1] == "/portMirrors/portMirror" :
            body = "<portMirrors> <portMirror>" + body + "</portMirror> </portMirrors>"
        elif len(apipath.split("netmonitorPortMirror")) == 2 and apipath.split("netmonitorPortMirror")[1] == "/portMirrors" :
            body = "<portMirrors>" + body + "</portMirrors>"
        else:
            err = "input url illegal!"
            return exe_cmd,err
        try:
            root = ElementTree.fromstring(body)
        except:
            err = "input xml body illegal!"
            return exe_cmd,err
        
        mirror_num = 1
        mirror_template_name = ""
        mirror_template = ""
        for param in root.findall("portMirror"): 
            if param.find("mirrorPortId")== None or param.find("observePortId")== None or param.find("in_MirrorEnable")== None or param.find("out_MirrorEnable")== None : 
                err = "input xml body illegal!"
                return exe_cmd,err
            if param.find("mirrorPortId")!= None:
                mirrorPortId = param.find("mirrorPortId").text
            if param.find("observePortId")!= None:
                observePortId = param.find("observePortId").text
            if param.find("in_MirrorEnable")!= None:
                inenable = param.find("in_MirrorEnable").text
            if param.find("out_MirrorEnable")!= None:
                outenable = param.find("out_MirrorEnable").text
            if param.find("mirrorID")!= None:
                mirrorName = param.find("mirrorID").text
            mirrorifname = ""
            observeifname = ""
            if (re.match(self.ruuid, mirrorPortId) and re.match(self.ruuid,observePortId)):
                if inenable != "false" and inenable != "FALSE" and inenable != "true" and inenable != "TRUE":
                    err = "in_MirrorEnable illegal"
                    break
                if outenable != "false" and outenable != "FALSE" and outenable != "true" and outenable != "TRUE":
                    err = "out_MirrorEnable illegal"
                    break
                if(("false" == inenable or "FALSE" == inenable) and ("false" == outenable or "FALSE" == outenable)):
                    err = "don't have port mirror flow direction"
                    break
                mirror_template_name = "@m%s"%mirror_num
                exe_cmd += (mirror_template_name +",")
                mirrorifname = "tap" + mirrorPortId[0:11]
                observeifname = "tap" + observePortId[0:11]
                mirror_template += self.cmd_template%(mirror_num,mirrorifname,mirror_num,observeifname,mirror_num,mirrorName)
                if "true" == inenable or "TRUE" == inenable: 
                    mirror_template += " select-src-port=@mirrorPortId%s"%mirror_num
                if "true" == outenable or "TRUE" == outenable:
                    mirror_template += " select-dst-port=@mirrorPortId%s"%mirror_num
                mirror_template += " output-port=@observePortId%s"%mirror_num
                    
            else:
                err = "portID format or length error"
                break
            mirror_num += mirror_num   
        exe_cmd += mirror_template
        logger.debug("[parse_post_xml] ending  \n")
        return exe_cmd,err
    
    
if __name__ == "__main__":
    pass
