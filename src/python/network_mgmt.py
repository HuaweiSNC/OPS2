from networkdevice_mgmt import NetworkDeviceM
import time,copy
from threading import Thread 
import json
import config 
import logging 
from thread_pool import ThreadPool,SigleThread
import Queue
import sys

logger = logging.getLogger("ops.network")  
class NetworkM():     
    _opsesn=False
    _channelnum=2
    def __init__(self):   
        self.devicedict={}
        self.timeOutQueue = Queue.Queue()
  
    def __exit__(self):
        pass
             
    def initConnectDevice(self,devicelist):
        for elem in devicelist:
            self.loadDevice(elem)
            #print elem           
        #print self.devicedict       
    
    def getDevice(self, id):
        return self.devicedict.get(id) 
    
    #load devices
    def loadDevice(self, elem):
        self.addDevice(elem)  
        
    #add device
    def addDevice(self, elem):
        sid = str(elem['id'])
        ip = elem['ip']
        username= elem['username']
        password= elem['passwd']
        productType= elem['productType']
        version= elem['version']
        driver=  elem['driver']
        devicename=  elem['devicename']
        port = elem.get('port')
        subdevices = elem.get('subdevices')
        if(subdevices == None or isinstance(subdevices,list) == False) : 
            subdevices = []
        if (ip == '' or username =='' or productType=='' or devicename==''):
            #TODO log
            return False
        
        networkDevice = NetworkDeviceM(sid,ip,port, username,password,driver)
        networkDevice.productType = productType
        networkDevice.version = version
        networkDevice.name = devicename
        networkDevice.set_multi_ipaddress(subdevices)
        networkDevice.initConnect(self._channelnum)
        
        self.devicedict[sid] = networkDevice   

    def modifyDevice(self, elem):
        did = elem['id']
        did = str(did)
        ip = elem['ip']
        username = elem['username']
        passwd = elem['passwd']
        devicename=  elem['devicename']
        subdevices = elem.get('subdevices')
        port = elem.get('port')
        driver=  elem.get('driver')
        if (port is None):
            port = 22
        networkDevice = self.devicedict.get(did) 
        if networkDevice != None:
            # to reload driverFile
            if networkDevice.driverFile != driver :
                self.delDevice(did)
                self.addDevice(elem)
            else :
                networkDevice.name = devicename
                networkDevice.set_main_device(ip, port, username, passwd)
                if (subdevices is not None):
                    networkDevice.set_multi_ipaddress(subdevices)

    def delDevice(self, sid):
        id = str(sid)
        networkDevice = self.devicedict.get(id) 
        if networkDevice != None:
            del self.devicedict[id]
            networkDevice.__exit__()
   
    def startThreadPool(self):
        while True:
            try:
                self.tp.keepAliveDaemon()
            except Exception as e:
                logger.exception(e)
            time.sleep(1)
    
    def detectConnectTimeOut(self):
        
        killThread = SigleThread('TimeOutManager', None, None)
        while True:
            try:
                timeoutThread = self.timeOutQueue.get()
                # kill timeout thread
                ident = timeoutThread.ident
                logger.error('Thread timeout, kill thread ident = %s' % ident)
                if (timeoutThread != None and timeoutThread.isAlive()):
                    killThread.asyncRaise(ident, SystemExit)
            except Queue.Empty:  
                pass
            except :
                n1 = sys.exc_info()
                logger.exception(n1[1]) 
                break
            finally:
                pass
        
    def detectConnect(self):
        while True:
            time.sleep(10) 
            timeOutThreadList = []
            try:
                for elem in self.devicedict:      
                            
                    networkDevice = self.devicedict[elem]
                    self.tp.addJob(networkDevice.detectConnect, networkDevice.deviceid)
                    
                    # detect esn running
                    if (self._opsesn == True):
                        self.tp.addJob(networkDevice.detectEsn, 'esn_%s' % networkDevice.deviceid)
                    
                    networkDevice.detectConnectTimeOut(timeOutThreadList)
                    
                #deal with Thread TimeOut
                for timeoutThread in timeOutThreadList:
                     self.timeOutQueue.put(timeoutThread)
 
            except Exception as e:
                logger.exception(e)
    
    def getDeviceInfoById(self, devid):
        networkDevice = self.getDevice(devid)
        if networkDevice == None:
            return
        deviceStatus = 'normal'
        if networkDevice.status == False :
                deviceStatus = 'sick'
                
        subdeviceMsg = copy.deepcopy(networkDevice.subdevices)
        for onesubdevice in subdeviceMsg:
            onesubdevice['passwd'] = ''
        
        deviceinfo = {'id':int(networkDevice.deviceid),
                    'status' : deviceStatus,
                    'devicename':networkDevice.name,
                    'connectstatus' : networkDevice.connectstatus,
                    'esn' : networkDevice.get_esn(),
                    'ip':networkDevice.ip,
                    'port':networkDevice.port,
                    'username':networkDevice.username,
                    'passwd':'',
                    'productType':networkDevice.productType,
                    'version':networkDevice.version,
                    'error' : networkDevice.getErrMsg(),
                    'subdevices' : subdeviceMsg}
        
 
        return { 'device' : deviceinfo}
          
    def getAllDeviceInfo(self):
        namelist=[]
        keys = self.devicedict.keys() 
        keys.sort() 
        for elem in keys:  
            namelist.append(self.getDeviceInfoById(elem))
        return {'devices':namelist}
        
    def threadstart(self): 
        self.tp = ThreadPool(10)
        self.tpool = Thread(target = self.startThreadPool,  args = ())
        self.tpool.daemon = True
        self.tpool.start()
        
        self.tdetect = Thread(target = self.detectConnect,  args = ())
        self.tdetect.daemon = True
        self.tdetect.start()
        
        self.ttimeout = Thread(target = self.detectConnectTimeOut,  args = ())
        self.ttimeout.daemon = True
        self.ttimeout.start()
          
    def addSubDevice(self, sid, elem):
        networkDevice = self.getDevice(sid)
        if(networkDevice != None):
            networkDevice.addSubDevice(elem)
            
    def deleteSubDevice(self, id, sid):
        networkDevice = self.getDevice(id)
        if(networkDevice != None):
            networkDevice.deleteSubDevice(sid)
            
    def modifySubDevice(self, id, sid, elem):
        networkDevice = self.getDevice(id)
        if(networkDevice != None):
            networkDevice.modifySubDevice(sid, elem)
 
        