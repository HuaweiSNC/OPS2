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
from logging.handlers import RotatingFileHandler

logger = logging.getLogger("SNMP_TrapRcv")   
#logging.basicConfig(filename=config.trapFile, level=logging.DEBUG)
fmt = logging.Formatter(fmt='%(asctime)s %(message)s')
#hdlr = logging.FileHandler(config.trapFile)
size=1024*1024
hdlr = RotatingFileHandler(filename=config.trapFile, maxBytes=size,backupCount=10)

hdlr.setFormatter(fmt)
logger.addHandler(hdlr)

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


class TrapRules(Rules):
    def __init__(self,host,trap_oid,target):
        self.type = 'TRAP'
        self.host = host
        self.trap_oid = trap_oid
        self.target = target
        super(TrapRules,self).__init__()
    def equal(self,rule):
        if self.host == rule.host  and  self.trap_oid == rule.trap_oid  and self.target == rule.target  :
            return True
        return False
    def key(self):
        return str(self.type)+str(self.host)+str(self.trap_oid)
    def value(self):
        return str(self.target)

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
    def __init__(self):
        pass
    
    def _search(self,rule):
        for i in self.filter:
            if i.equal(rule):
                return i
        return None
        
    def add_filer(self,rule):
        if self._search(rule) == None:            
            self.filter.append(rule)             
        self.to_dict()        
    def delete_filter(self,rule):
        r = self._search(rule)
        if r != None:
            self.filter.remove(r)
        self.to_dict()
    def to_dict(self):
        self.match_dict={}        
        for i in self.filter: 
            if self.match_dict.has_key(i.key()):               
                t = self.match_dict[i.key()]               
                t.append(i.value)              
                self.match_dict[i.key()] = t
            else:
                self.match_dict[i.key()]=[i.value()]                
    def dispatch(self,notify,traprecord):
        key = ''                   
        if notify.key() in self.match_dict:
            key = notify.key()
        elif 'TRAP' in self.match_dict:
            key = 'TRAP'   
        if key != '':  
            #print 'Receive subscribed trap'                   
            for i in self.match_dict[key]:
                self.http_post(i,traprecord)   
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
              
        #print 'http_request:%s,%s'%(httpurl,body)          
           
'''
def dispatch(snmptrap):
    print snmptrap.key()
    #if rule['host'] == snmptrap.transportAddress and rule['trap_oid'] == snmptrap.trap_oid :
    if snmptrap.key() in Rules:
        for dispatch in Dispatchers:
            http_post(dispatch['target'],snmptrap.body())      
    
'''

'''
transportDispatcher = AsynsockDispatcher()

transportDispatcher.registerRecvCbFun(cbFun)

# UDP/IPv4
transportDispatcher.registerTransport(
    udp.domainName, udp.UdpSocketTransport().openServerMode(('10.135.32.108', 162))
)

"""
# UDP/IPv6
transportDispatcher.registerTransport(
    udp6.domainName, udp6.Udp6SocketTransport().openServerMode(('::1', 162))
)
"""
transportDispatcher.jobStarted(1)

try:
    # Dispatcher will never finish as job#1 never reaches zero
    transportDispatcher.runDispatcher()
except:
    transportDispatcher.closeDispatcher()
    raise
'''

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
        print 'quit from runDispatcher'
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
                udp.domainName, udp.UdpSocketTransport().openServerMode((ip, port))        
            )       
            self.notifyDispatcher.jobStarted(1)
        except:
            print 'failed to create the socket'
    def run(self): #Overwrite run() method, put what you want the thread do here  
        try:
            # Dispatcher will never finish as job#1 never reaches zero
            self.notifyDispatcher.runDispatcher(1.0)
        except:
            self.notifyDispatcher.closeDispatcher()
            raise
        print 'quit from run'
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
               
                ReceivedTrap = SnmpTrap(msgVer,transportDomain,transportAddress,varBinds)  
                
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
                logger.warning(traprecord)                          
                for i in self._dispatchers:                    
                    i.dispatch(ReceivedTrap, traprecord)
    
def startReceiveTrap(serverip, trapport=162):
    dispatcher = Dispatcher()
    '''
    traprule1=TrapRules('10.137.210.122',ObjectName('1.3.6.1.6.3.1.1.5.3'),'http://10.135.34.246:8080/channels/2/data')
    dispatcher.add_filer(traprule1)
    traprule2=TrapRules('10.137.210.122',ObjectName('1.3.6.1.6.3.1.1.5.4'),'http://10.135.34.246:8080/channels/2/data')
    dispatcher.add_filer(traprule2)    
    ''' 
    #All trap  
    traprule3=TrapRules('','','http://localhost:9000/channels/2/data')
    dispatcher.add_filer(traprule3)
    '''
    host_name = socket.gethostname()
    host = socket.gethostbyname(host_name)
    #port = 163
    '''
    host=serverip
    disip = host
    if disip == '':
        disip = 'localhost'
    print '%s port %s is listen trap'%(disip,trapport)        
    nt=SNMP_NotifyRcv_Thread(host,trapport)  
    nt.register_dispatcher(dispatcher)
    nt.setDaemon(False)
    nt.start()
    print 'Start to receive trap'
    return nt
    
def stopReceiveTrap(nt):    
    nt.stop()
    print 'quit from TrapThread' 
    
if __name__ == '__main__':
    #ss=SnmpTrapService('10.135.32.108',162)
    #ss.startService()
    dispatcher = Dispatcher()
    
    traprule1=TrapRules('10.137.210.122',ObjectName('1.3.6.1.6.3.1.1.5.3'),'http://10.135.34.246:8090/channels/2/data')
    dispatcher.add_filer(traprule1)
    traprule2=TrapRules('10.137.210.122',ObjectName('1.3.6.1.6.3.1.1.5.4'),'http://10.135.34.246:8090/channels/2/data')
    dispatcher.add_filer(traprule2)
    ''' 
    #All trap  
    traprule3=TrapRules('','','http://10.135.34.246:8090/channels/2/data')
    dispatcher.add_filer(traprule3)
    '''
    host_name = socket.gethostname()
    host = socket.gethostbyname(host_name)
    port = 163
    print host,port, 'is listen trap'        
    nt=SNMP_NotifyRcv_Thread(host,port)  
    nt.register_dispatcher(dispatcher)    
    nt.setDaemon(False)
    nt.start()
    print 'Start to receive trap'
    '''
    time.sleep(5000)
    print 'Wait time out'
    nt.stop()
    print 'close'
    '''
     