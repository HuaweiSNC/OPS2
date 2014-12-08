# -*- coding: utf-8 -*-
from pysnmp.carrier.asynsock.dispatch import AsynsockDispatcher
from pysnmp.carrier.asynsock.dgram import udp, udp6
#from pyasn1.codec.ber import decoder
#from pysnmp.proto import api

#from pysnmp.proto.rfc1902 import ObjectName
from urlparse import urlparse
from websocket import create_connection

import httplib
import threading, time, random
import socket
import config
import logging
from logging.handlers import RotatingFileHandler

logger = logging.getLogger("syslog_logRcv")        
#logging.basicConfig(filename=config.syslogFile, level=logging.DEBUG)
#fs = '%(asctime)s %(levelname)s %(message)s'
#dfs = '%m-%d %H:%M'
fmt = logging.Formatter(fmt='%(asctime)s %(message)s')
#hdlr = logging.FileHandler(config.syslogFile)
size=1024*1024
hdlr = RotatingFileHandler(filename=config.syslogFile, maxBytes=size,backupCount=10)
hdlr.setFormatter(fmt)
logger.addHandler(hdlr)

#===============================================================================
#  Configure
# Usage:
#  add  a rule in Rules
#  add  a dispatch in Dispatchers  
#===============================================================================
Dispatchers=[
          {'target':'http://10.135.34.246:8090/channels/2/data'},
          ]

#Current ��SNMP�Ŀɿ��Ժ�HTTP POST�ɿ���δ���ǣ�������

logformat = '''<syslogs xmlns="http://huawei.com/common/syslog">
    <syslog>
        <PRI>
            <MsgSource>%d</MsgSource>
            <Severity>%d</Severity>
        </PRI>
        <HEADER>
            <timestamp>%s</timestamp>
            <agentaddress>%s</agentaddress>
        </HEADER>
        <MSG>
            %s
        </MSG>
    </syslog>
</syslogs>'''


class Syslog(object):
    def __init__(self, addr):
        self.addr = addr   
    def body(self,log):  
        source,level,timestamp,loginfo=parselogmessage(log)          
        body= logformat%(source,level,timestamp,self.addr,loginfo)      
        return body 


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
class syslog_NotifyRcv_Thread(threading.Thread): #The timer class is derived from the class threading.Thread
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
        time.sleep(1)
        self.notifyDispatcher.closeDispatcher()
    def register_dispatcher(self,dispatcher):
        self._dispatchers.append(dispatcher)
        pass
        
    def cbFun(self,transportDispatcher, transportDomain, transportAddress, wholeMsg):
        logmsg = wholeMsg[0:-2]
        #print 'Log message received from %s: %s' %(transportAddress, logmsg)
        logger.warning('Log message received from %s: %s' %(transportAddress,logmsg))
        
        addr = transportAddress[0]
        log=Syslog(addr) 
        self.dispatch(log.body(logmsg))
    
    def dispatch(self,log):                 
        for i in Dispatchers:
            self.http_post(i['target'],log)  
    
    def http_post(self,httpurl,body):    
        from httpc_httplib import httpclient
        try:
            hc = httpclient()  
        except:
            print 'create httpclient fail'   
            return
        #print 'send to ',httpurl
        #print 'send body:\n',body 
        '''
        from xmlTojson import isdk_convert_xml2json
        body = isdk_convert_xml2json(body)       
        body=json.loads(body)        
        '''         
        try:
            status,_ = hc._post(httpurl,body) 
        except:
            print 'post to %s fail'%httpurl  
            return 

def parselogmessage(logmsg):
    marker = ' %%'
    logmsg = logmsg.split(marker)
    temp1 = logmsg[0].split('>')
    temp2 = temp1[1]
    index1 = temp2.rfind(' ') 
    timestamp=temp2[0:index1]    
    temp3 = temp1[0].split('<')
    temp4 = temp3[1]    
    source = int(temp4)/8
    level = int(temp4)%8
    loginfo =  temp2+ marker+logmsg[1]
    return  source,level,timestamp,loginfo

def startReceiveLog(serverip, trapport=514): 
    host=serverip
    print '%s port %s is listen log'%(host,trapport)        
    nt=syslog_NotifyRcv_Thread(host,trapport)  
    #nt.register_dispatcher(dispatcher)
    nt.setDaemon(False)
    nt.start()
    print 'Start to receive log'
    return nt
    
def stopReceiveLog(nt):    
    nt.stop()
    print 'quit from LogThread' 

if __name__ == '__main__':
    host_name = socket.gethostname()
    host = socket.gethostbyname(host_name)
    print host_name, host    
    port = 514 
    nt=syslog_NotifyRcv_Thread(host,port)  
   # nt.register_dispatcher(dispatcher)
    nt.setDaemon(False)
    nt.start()
    print 'Start to receive log'
    time.sleep(5000)
    print 'Waiting time out'
    nt.stop()
    print 'close'
    
    