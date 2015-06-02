# -*- coding: utf-8 -*-
import os
from xmlrpclib_1_0_1 import xmlrpclib 
import base64
import thread
import config
import logging 
logger = logging.getLogger("ops.testEngine.controller")  

# http://localhost:8080/devices/6/TgTsuSetEthernetLinkData --- post
# [{

#    'port' : 1,
#    'fixed_params' : ['60.1.1.2','60.1.1.1','24'],
#    'option_params' : {
#                       'ArpReply':'FALSE', 
#                       'ArpKeepalive':'FALSE'
#                      },
# }]
# from testcontroller import test_controller
# 
# test_device = test_controller.add_test_device('10.137.222.217', 'LAN1002')
# or
# test_device = test_controller.get_test_device('10.137.222.217')
# test_device.send('TgTsuSetEthernetLinkData', 1, ['60.1.1.2','60.1.1.1','24'], {'ArpReply':'FALSE', 'ArpKeepalive':'FALSE'})
# send: 'TgTsuSetEthernetLinkData 1 1 60.1.1.2 60.1.1.1 24 -ArpReply FALSE -ArpKeepalive FALSE' 
# result: 0TG_OK
# 


class TestEngineController:
    def __init__(self, ip, port=55555, username="root123", password="Root@123"):
        self.test_device_list = {}
        self._init_test_env(ip, port=port, username=username, password=password)
    
    def _init_test_env(self, ip, port=55555, username="root123", password="Root@123"):
        cur_dir = os.path.dirname(__file__).replace("\\",'/')
        
        self.uri = 'http://%s' % ip
        self.uri_port = str(port)
        logger.info("Initial testEngine server %s:%s " % (self.uri,self.uri_port))
        self.server_proxy = xmlrpclib.ServerProxy(self.uri+':'+self.uri_port, verbose=False)
  
    def _format_ip(self, ip):
        ip_elem_list = ip.split('.')
        i = 0
        for v in ip_elem_list:
            ip_elem_list[i] = str(int(v))
            i = i+1
        ip = ".".join(ip_elem_list)
        return ip
        

    def sendcmd(self, cmd):
        
        logger.info("-->%s" % cmd)
        cmd = base64.b64encode(cmd)
        ret = self.server_proxy.xml_rpc_eval(cmd)
        ret = base64.b64decode(ret)
        result = ret[0:1]
        ret = ret[1:]
        if "1" == result:
            logger.error("<--%s" % ret)
        else:
            logger.info("<--%s" % ret)
        return result, ret
    
    def send(self, cmd, tsuid, port, fixed_params, option_params):
        tmp = cmd
        if None == port:
            if None != tsuid:
                tmp = '%s %s' % (tmp, tsuid)
        else:
            tmp = '%s %s %s' % (tmp, tsuid, str(port))
            
        if (fixed_params != None):
            for v in fixed_params:
                tmp = tmp + ' ' + v

        if (option_params != None):
            for k in option_params:
                tmp = '%s -%s %s' % (tmp, k, option_params[k]) 
        
        bret, result= self.sendcmd(tmp)
        return bret, result