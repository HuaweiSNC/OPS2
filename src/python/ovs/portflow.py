# -*- coding: utf-8 -*- 
#!/usr/bin/python


##----------------------------------------------------------------------------------------------------------------------
##-- Copyright (C) Huawei Technologies Co., Ltd. 2008-2011. All rights reserved.
##----------------------------------------------------------------------------------------------------------------------
##----------------------------------------------------------------------------------------------------------------------
##--Project Code    : ops2.1
##--File name       : protflow.py
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

# create logger 
logger = logging.getLogger("ops.protflow") 

from process_adapter import Process_Adapter

class Rest_Process(Process_Adapter):
    
    def __init__(self, sshEngine):
        self.ssh = sshEngine
        self.responsexml = \
'''<inventory>
      <interfaces>
          <interface>
              <portID>%s</portID>
              <statistics>
                <in-pkts>%s</in-pkts>
                <in-octets>%s</in-octets>
                <in-discards>%s</in-discards>
                <in-errors>%s</in-errors>
                <out-pkts>%s</out-pkts>
                <out-octets>%s</out-octets>
                <out-discards>%s</out-discards>
                <out-errors>%s</out-errors>
              </statistics>
          </interface>
      </interfaces>
   </inventory>'''
        self.errorxml = \
        '''<rpc-error xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0">
                <error-type>application</error-type>
                <error-tag>unknown-element</error-tag>
                <error-message>%s</error-message>
            </rpc-error>'''
        self.result = ""
        self.err = ""
    def process(self, method, apipath, bodytype, body):
        logger.debug("[process] starting \n")
        if("GET" == method):
            self.result, self.err = self.get_process(method, apipath, bodytype, body)
        elif("POST" == method):
            self.result, self.err = ("", "")
        elif("DELETE" == method):
            self.result, self.err = ("", "")
        elif("PUT" == method):
            self.result, self.err = ("", "")
        logger.debug("[process] ending \n")
        return self.result, self.err
    
    def get_process(self,method, apipath, bodytype, body):
        logger.debug("[get_process] input parameter method:%s, apipath:%s, bodytype:%s, body:%s \n",
                    method, apipath, bodytype, body)
        flow_result , err = ("","")
        #判断url格式是否正确
        if(len(apipath.split("?portID=")) == 2 and apipath.split("?portID=")[1] != ""):
            param = apipath.split("?portID=")[1].replace(" ","")
            #判断url传入参数是否为36位uuid格式
            ruuid = r'[0-9a-z]{8}-[0-9a-z]{4}-[0-9a-z]{4}-[0-9a-z]{4}-[0-9a-z]{12}'
            if re.match(ruuid, param.replace(" ","")):
                ifname = "tap" + param[0:11]
                ofport, err = self.ssh.exec_cmd("ovs-vsctl get interface " + ifname + " ofport")
                #获取port端口成功
                if (err == ""):
                    flow_result, err = self.ssh.exec_cmd("ovs-ofctl dump-ports br-int " + ofport)
                    if (self.err != ""):
                        logger.error(err)
                        err = self.errorxml%(err)
                    #将evs响应信息转换为xml格式
                    flow_result = self.parse_response_xml(flow_result, param)
                else:
                    #记录获取port端口异常
                    logger.error(err)
                    err = self.errorxml%(err)
            else:
                #记录参数异常
                logger.error("portID format or length error \n")
                err = self.errorxml%("portID format or length error")
        else:
            #记录url异常
            logger.error("not input portID \n")
            err = self.errorxml%("not input portID")
        logger.debug("[get_process] output parameter flow info:%s\n error:%s \n",flow_result,err)
        return flow_result,err
    
    def parse_response_xml(self,text,portID):
        logger.debug("[para_response_xml] input parameter: %s \n",text)
        text = text.split(":")[2]
        rxstr = text[text.index("rx") + 2:text.index("tx")]
        txstr = text[text.index("tx") + 2:]
        rxstr = rxstr.replace(" ", "").replace("\n", "").split(",")
        txstr = txstr.replace(" ", "").replace("\n", "").split(",")
        para = {}
        for i in rxstr:
            i = i.split("=")
            para['rx_' + i[0]] = i[1]
        for j in txstr:
            j = j.split("=")
            para['tx_' + j[0]] = j[1]
        text = self.responsexml%(portID,para['rx_pkts'],para['rx_bytes'],para['rx_drop'],
                          para['rx_errs'],para['tx_pkts'],para['tx_bytes'],para['rx_drop'],para['tx_errs'])
        logger.debug("[para_response_xml] parse ending \n")
        return text
    
if __name__ == "__main__":
    pass


    
        
