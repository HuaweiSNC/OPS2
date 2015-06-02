# -*- coding: utf-8 -*-
from pysnmp.carrier.asynsock.dispatch import AsynsockDispatcher
from pysnmp.carrier.asynsock.dgram import udp, udp6
from pyasn1.codec.ber import decoder
from pysnmp.proto import api

from pysnmp.proto.rfc1902 import ObjectName
from urlparse import urlparse
from websocket import create_connection

import httplib
import threading, time, random
import socket
import json
import config
import logging
import os
logger = logging.getLogger("trap.SNMP_TrapRcv") 

#===============================================================================
#  Configure
# Usage:
#  add  a rule in Rules
#  add  a dispatch in Dispatchers  
#===============================================================================

Rules=[
       {'host':'10.137.130.129','trap_oid':ObjectName('1.3.6.1.4.1.2011.5.25.191.3.1')},
       
       ]
Dispatchers=[
          {'target':'http://10.135.34.246:9000/channels/2/data'},
          ]
#Current ��SNMP�Ŀɿ��Ժ�HTTP POST�ɿ���δ���ǣ�������

#===============================================================================
#  Match Rules:which data to which ...
#===============================================================================
class Rules(object):
    def __init__(self):
        pass
    def equal(self,rule):
        pass
    def key(self):
        return None
    def value(self):
        return None

#订阅条件
class TrapRules(Rules):
    def __init__(self,host,trap_oid):
        self.type = 'TRAP'
        self.host = host
        self.trap_oid = trap_oid
        super(TrapRules,self).__init__()
    def equal(self,rule):
        if self.host == rule.host  and  self.trap_oid == rule.trap_oid:
            return True
        return False
    def key(self):
        return str(self.type)+str(self.host)+str(self.trap_oid)
    def value(self):
        return str(self.host)

#===============================================================================
# which data define
#===============================================================================
#community="%s"  
v1trapformat = '''
<snmpTrapPdu xmlns="http://huawei.com/common/trap">
    <snmpv1trap>
        <timestamp>%s</timestamp>
        <agentaddr>%s</agentaddr>
        <eid>%s</eid>
        <gid>%s</gid>
        <sid>%s</sid>
        <vbs>
        %s
        </vbs>
    </snmpv1trap>
</snmpTrapPdu>
'''

v2trapformat = '''
<snmpTrapPdu xmlns="http://huawei.com/common/trap">
    <snmpv2trap>
        <timestamp>%s</timestamp>
        <agentaddr>%s</agentaddr>
        <trapoid>%s</trapoid>
        <vbs>
        %s
        </vbs>
    </snmpv2trap>
</snmpTrapPdu>
'''

class Notify(object):
    def __init__(self):
        pass
    def key(self):
        pass
    def body(self):
        pass
class SnmpTrap(Notify):
    msgVer = None
    transportDomain=None
    transportAddress=None
    varBinds=None
    def __init__(self,msgVer,transportDomain,transportAddress,varBinds):
        self.msgVer = msgVer
        self.transportDomain = transportDomain
        self.host = transportAddress[0]  #ipaddress only
        self.port = transportAddress[1]
        self.varBinds = varBinds
        self.trap_oid = 1
        if msgVer == 1:
            self.trap_oid = varBinds[1][1][0][0][2]  #ObjectName    
            #print 'Notification %s received from %s' % (self.trap_oid, transportAddress)             
            logger.warning('Notification %s received from %s' % (self.trap_oid, transportAddress))      
        if msgVer == 0:            
            #print 'Notification received from %s' %(str(transportAddress))             
            logger.warning('Notification received from %s'%(str(transportAddress))) 
            self.trap_oid = 1
        super(SnmpTrap,self).__init__()
    def key(self):       
        return 'TRAP'+str(self.host)+str(self.trap_oid)    
    def body(self):        
        return {'body':{'host':self.host,'trap_oid':str(self.trap_oid),'msgVer':self.msgVer,'varBinds':str(self.varBinds)}}
        #return {'host':self.host,'trap_oid':str(self.trap_oid),'msgVer':self.msgVer,'varBinds':str(self.varBinds)}      
        #return {'data':{"host":"1.1.1.1",
        #                'trap_oid':'1.3.6.1'}
        #}
        
    
#===============================================================================
# 
#===============================================================================
class Dispatcher():
    """From Snmp to Http(channel)
    """
    filter=[]
    match_dict={} #{'key':[a,b,c]}
    def __init__(self, mychannels):
        self.channels = mychannels
             
    def dispatch(self,notify,traprecord):
        self.channels.dispatch(notify,traprecord)
        """        key = ''                   
        if notify.key() in self.match_dict:
            key = notify.key()
        elif 'TRAP' in self.match_dict:
            key = 'TRAP'   
        if key != '':  """
        
    #当前是Notification不可靠            
    def http_post(self,httpurl,body):        
        #_,netloc,path,_,_,_= urlparse(httpurl)
        
        from httpc_httplib import httpclient
        try:
            hc = httpclient()  
        except:
            print 'create httpclient fail'   
            return
        #print 'send to ',httpurl
        #print 'send body:\n',body        
        
        from xmlTojson import isdk_convert_xml2json

        try:
            body = isdk_convert_xml2json(body)
            body = json.dumps(body, sort_keys=True, indent=4, separators=(', ',': '))
            body=json.loads(body)
            status,_ = hc._post(httpurl,body) 
        except:
            print 'post to %s fail'%httpurl  
            return      
      
class AsynsockDispatcherEX(AsynsockDispatcher):
    def __init__(self):
        self.thread_stop = False
        AsynsockDispatcher.__init__(self)
    def runDispatcher(self, timeout=0.0):
        while ( self.jobsArePending() or self.transportsAreWorking()) and self.thread_stop == False:
            from asyncore import poll
            from time import time
            poll(timeout and timeout or self.timeout, self.getSocketMap())
            self.handleTimerTick(time())
        logger.debug( 'quit from runDispatcher')
    def stop(self):
        self.thread_stop = True


import threading  
import time  
class SNMP_NotifyRcv_Thread(threading.Thread): #The timer class is derived from the class threading.Thread
    _dispatchers = []  
    def __init__(self,ip,port):  
        threading.Thread.__init__(self)          
        #self.thread_stop = False  
        self.notifyDispatcher = AsynsockDispatcherEX()        
        self.notifyDispatcher.registerRecvCbFun(self.cbFun)        
        # UDP/IPv4
        try:
            self.notifyDispatcher.registerTransport(
                udp.domainName, udp.UdpSocketTransport().openServerMode((ip, int(port)))   )       
            self.notifyDispatcher.jobStarted(1)
        except Exception as e:
            logger.error('failed to create the socket : %s' % e)
            
    def run(self): #Overwrite run() method, put what you want the thread do here  
        try:
            # Dispatcher will never finish as job#1 never reaches zero
            self.notifyDispatcher.runDispatcher(1.0)
        except:
            self.notifyDispatcher.closeDispatcher()
            raise
        logger.debug('quit from run')
    def stop(self):  
        #self.thread_stop = True
        self.notifyDispatcher.stop()
        time.sleep(2)
        self.notifyDispatcher.closeDispatcher()
    def register_dispatcher(self,dispatcher):
        self._dispatchers.append(dispatcher)  
        pass
    
    #callback function
    def cbFun(self,transportDispatcher, transportDomain, transportAddress, wholeMsg):  
        record = '' 
        record = record + '<snmpTrapPdu xmlns="http://huawei.com/common/trap">\n' 
        while wholeMsg:
            msgVer = int(api.decodeMessageVersion(wholeMsg))
            if msgVer in api.protoModules:
                pMod = api.protoModules[msgVer]
            else:
                logger.warning('Unsupported SNMP version %s' % msgVer)
                return
            reqMsg, wholeMsg = decoder.decode(
                wholeMsg, asn1Spec=pMod.Message(),
                )                             
            #logger.warning('Notification message from %s:%s: ' % (transportDomain, transportAddress))
            reqPDU = pMod.apiMessage.getPDU(reqMsg)
            community = pMod.apiMessage.getCommunity(reqMsg)
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
            
            if reqPDU.isSameTypeWith(pMod.TrapPDU()):
                if msgVer == api.protoVersion1:                    
                    Enterprise = (str)(pMod.apiTrapPDU.getEnterprise(reqPDU).prettyPrint()) 
                    agentaddr = pMod.apiTrapPDU.getAgentAddr(reqPDU).prettyPrint()
                    GenericTrapid = pMod.apiTrapPDU.getGenericTrap(reqPDU).prettyPrint()
                    SpecificTrapid = pMod.apiTrapPDU.getSpecificTrap(reqPDU).prettyPrint()
                    varBinds = pMod.apiTrapPDU.getVarBindList(reqPDU)
                else:                     
                    varBinds = pMod.apiPDU.getVarBindList(reqPDU) 
                    trapoid =  (str)(varBinds[1][1][0][0][2])
               
                receivedTrap = SnmpTrap(msgVer,transportDomain,transportAddress,varBinds)  
                
                trapvbs = ''
                for oid, val in varBinds:
                    #logger.warning ('%s = %s' % (oid.prettyPrint(), val.prettyPrint())) 
                    trapvbs = trapvbs + '<vb>'  
                    trapvbs = trapvbs + '\n        <oid>' + oid.prettyPrint() + '</oid>' 
                    #print (val.getComponent(1)).prettyPrint()
                    value = (val.getComponent(1)).prettyPrint()
                    trapvbs = trapvbs + '\n        <value>' + value + '</value>\n'  
                    trapvbs = trapvbs + '        </vb>\n'  
                           
                #no print community message
                if msgVer == api.protoVersion1:
                    traprecord = v1trapformat%(timestamp,agentaddr,Enterprise,GenericTrapid,SpecificTrapid,trapvbs)
                else:
                    traprecord = v2trapformat%(timestamp,transportAddress[0],trapoid,trapvbs)
                #print traprecord     
                logger.debug(traprecord)                          
                for i in self._dispatchers:                    
                    i.dispatch(receivedTrap, traprecord)
    
def startReceiveTrap(serverip, trapport=162, channels=None):
    
    dispatcher = Dispatcher(channels)
 
    host=serverip
    disip = host
    if disip == '':
        disip = 'localhost'
    logger.info('%s port %s is listen trap'%(disip,trapport) )       
    nt=SNMP_NotifyRcv_Thread(host,trapport)  
    nt.register_dispatcher(dispatcher)
    nt.setDaemon(False)
    nt.start()
    logger.info('Start to receive trap')
    return nt
    
def stopReceiveTrap(nt):    
    nt.stop()
    logger.info( 'quit from TrapThread') 
    
if __name__ == '__main__':
    dispatcher = Dispatcher(None)
 
     