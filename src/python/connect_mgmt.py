
import logging
import threading
from rest_adapter import Rest_Adapter
from threading import local, enumerate, Thread, currentThread
logger = logging.getLogger("ops.network.device.channel")  
        
class ConnectM():  
    maxConnectTimeOut = 120  # 120*10=1200/60=20 minute
    def __init__(self,ip, port, username, password, driverFile, sid): 
        self.sid = sid       
        self.ipaddress = ip
        self.port = 22
        self.password = password
        self.username =username
        self.driverFile = driverFile
        self.status = True
        self.isBusy = False    
        self.errorinfo =''
        self.usetimeCount = 0
        self.isSleep = False
        self.subdevices = []
        self.classObj = None
        self.mutex = threading.Lock()
        self.mythread = None
        self.threadTimeCount=0
        
    def __exit__(self):
        self.mythread = None
        self.threadTimeCount=0
        if self.classObj != None:
            self.closeDevice()
            
    def setBusy(self):
        self.isBusy = True
        with self.mutex:
            self.mythread = None
            self.threadTimeCount=0
        
    def free(self):
        self.isBusy = False
        with self.mutex:
            self.mythread = None
            self.threadTimeCount=0
         
    def getStatus(self):
        if self.classObj == None:
            self.loadDevice()
        return self.status
     
    def loadDevice(self):
        mod = __import__(self.driverFile)
        logger.info ('renew connect client %s, channel %s' % (self.ipaddress ,self.sid))
        self.classObj = mod.Process_Rest_Api(self.ipaddress,port = self.port, username=self.username, password=self.password)
        assert isinstance(self.classObj, Rest_Adapter)
        self.classObj.set_multi_ipaddress(self.subdevices)
        self.status = self.classObj.getStatus()
        if self.status == False:
            self.errorinfo = self.classObj.errorinfo
            return False            
        else:
            return True

    def closeDevice(self):
        if self.classObj != None:
            logger.info ('delete connect client %s, channel %s' % (self.ipaddress ,self.sid))
            self.usetimeCount = 0
            self.classObj.close()
            
    def getCurrentThreadId(self):
        self.mythread = currentThread()
    

    def get_rest_api_handle(self, dInputBody, schemapath):
        
        self.getCurrentThreadId()
        
        # get current thread id
        if self.classObj == None:
            if (self.loadDevice() == False):
                return
        self.reconnect()
        self.usetimeCount = 0
        self.isSleep = False
        return self.classObj.get_rest_api_handle(dInputBody, schemapath)   
      
    def delete_rest_api_handle(self, dInputBody, schemapath):
        
        self.getCurrentThreadId()
        
        if self.classObj == None:
            if (self.loadDevice() == False):
                return
        self.reconnect()
        self.usetimeCount = 0
        self.isSleep = False
        return self.classObj.delete_rest_api_handle(dInputBody, schemapath)
    
    def put_rest_api_handle(self, dInputBody, schemapath):
        
        self.getCurrentThreadId()
         
        if self.classObj == None:
            if (self.loadDevice() == False):
                return
        self.reconnect()
        self.usetimeCount = 0
        self.isSleep = False
        return self.classObj.put_rest_api_handle(dInputBody, schemapath)   

    def post_rest_api_handle(self, dInputBody, schemapath):
        
        self.getCurrentThreadId()
        
        if self.classObj == None:
            if (self.loadDevice() == False):
                return
        self.reconnect()
        self.usetimeCount = 0
        self.isSleep = False
        return self.classObj.post_rest_api_handle(dInputBody, schemapath)   
    
    def reconnect(self) :
        if self.classObj.getStatus() == False:
            try: 
                reconStatus = self.classObj.reconnect()
                if (reconStatus == None or reconStatus == False ):
                    if self.status == False:
                         self.errorinfo = self.classObj.errorinfo
                    logger.error('Reconnect failed: ipaddress %s, channel %s, msg: %s' % (self.ipaddress ,self.sid, self.errorinfo))
            except Exception as e: 
                self.errorinfo = e 
                self.status = self.classObj.getStatus()
                logger.exception(e)
                logger.error('Client session creation failed, ipaddress %s, channel %s, msg: %s ' % (self.ipaddress , self.sid, self.errorinfo))
                
    def detectConnectTimeOut(self):
        with self.mutex:
            if (self.mythread != None and self.mythread.isAlive()):
                self.threadTimeCount=self.threadTimeCount + 1
        if (self.threadTimeCount > self.maxConnectTimeOut):
            # start kill process
            self.threadTimeCount = 0
            return True
        return False
    
    def detectConnect(self):
        if self.classObj == None:
            self.status = True
            return True
        
        nexttimecount = self.usetimeCount + 1
        self.usetimeCount = nexttimecount
        #print  '[%s:%s]increase id %s' % (self.ipaddress ,self.sid,nexttimecount)
        #if no use 600 time , close it
        if (nexttimecount > 120):
            self.isSleep = True
            logger.info ( 'idle 20 minute, close client %s, channel %s' % (self.ipaddress ,self.sid))
            self.status = True
            self.closeDevice()
            return True
        self.status = self.classObj.getStatus()
        return self.status
        
    def set_multi_ipaddress(self, devices=[]):
        self.subdevices = devices
        if self.classObj != None:
            self.classObj.set_multi_ipaddress(devices)
    
    def get_esn(self):
        if self.classObj == None:
            if (self.loadDevice() == False):
                return
        self.reconnect()
        self.usetimeCount = 0
        self.isSleep = False 
        return self.classObj.get_esn()
    
    def set_main_device(self, ip, port=22, username="root123", password="root123"):
        self.ipaddress = ip
        self.port = port
        self.password = password
        self.username = username
        if self.classObj is not None:
            self.classObj.set_main_device(ip, port, username, password)
        
    