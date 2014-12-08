import threading
from connect_mgmt import ConnectM 
import time
import logging 
logger = logging.getLogger("ops.network.device") 

class NetworkDeviceM():     
    
    def __init__(self,deviceid,ip,username,password,driver):        
        self.connlist = []
        self.deviceid = deviceid
        self.ip = ip
        self.username =username
        self.password = password
        self.driverFile =driver
        self.mutex = threading.Lock()
        self.status =True
        self.connectstatus = ''
        self.esn=''
        self.productType = ''
        self.version = ''
        self.name = ''
        self.subdevices =[]
        self.isbreak = False
        self.port = 22
        self.esn = ''
        self.connesn = None
        self.errmsg = ''
        
    def __exit__(self):
        self.isbreak = True
        for elem in self.connlist:
            if elem != None:
                elem.__exit__()
                del elem
                
    def getErrMsg(self):
        return self.errmsg
        
    def initConnect(self, num=2):
        # judge driver file is exists
        exists = True
        try:
            mod = __import__(self.driverFile)
        except Exception as e:
            #print repr(e)
            logger.error('device %s[%s] can not load the driver \'%s\', detail: producttype=%s and version=%s; %s'  %(self.name, self.deviceid,self.driverFile,self.productType, self.version, e))
            exists = False
        while (exists and num>0):
            connect = ConnectM(self.ip, self.port, self.username, self.password, self.driverFile, num)
            connect.set_multi_ipaddress(self.subdevices)
            self.connlist.append(connect)
            num = num - 1
                
    def getFreeConnect(self, isWrite = True):    
          
        elemret = None
        errormsg = ''
        
        # if status is break, return the error message
        if (self.isbreak == True):
            raise Exception(self.errmsg)
        
        waitcount = 10 * 60
        
        # wait 5 minute to get lock
        while not self.mutex.acquire(0):
            waitcount = waitcount -1    
            time.sleep(0.5)
            if (waitcount <= 0):
                errormsg = 'Timeout 10 minute, the device %s lock cannot be acquired' % self.name
                raise Exception(errormsg)
            
        try:  
            count = 50
            
            #detect if break device
            isAllBreak = True
            while(len(self.connlist) > 0 and count >0 and self.isbreak == False):
                for elem in self.connlist:
                    if elem.status == True:
                        isAllBreak = False
                    else :
                        errormsg = elem.errorinfo
                    if elem.isBusy == False and elem.status == True:
                        elem.setBusy()
                        elemret = elem
                        break
                    
                if elemret != None:
                    break
                # if all device is break quit
                if isAllBreak == True : 
                    break;
                
                time.sleep(0.5)
                count = count -1
        finally:
              self.mutex.release()      
 
        if elemret == None and errormsg != '':
            raise Exception(errormsg)
            
        return elemret
    
    def detectConnectTimeOut(self, timeOutThreadList=[]):
        for elem in self.connlist :
            if elem.isBusy == True and self.isbreak != True :
               if (elem.detectConnectTimeOut() and elem.mythread != None):
                   timeOutThreadList.append(elem.mythread)
        
    
    def detectConnect(self):
        
        #logger.info('Detectconnect deviceid %s, ipaddress %s '% (self.deviceid,self.ip))
        # get release connlist
        breakConnlist = []
        statusList = []
        statusTmp = False
        
        # if status is break, return the error message
        if (self.isbreak == True):
            self.connectstatus ='[]'
            self.status = 'sick'
            return 
        
        for elem in self.connlist :
                if elem.isBusy == False and self.isbreak != True and elem.isSleep != True:
                    #print elem.ipaddress,elem.driverFile
                    if elem.detectConnect() != True:
                        breakConnlist.append(elem)
                        statusList.append("sick")
                    else:
                        statusList.append("normal")
                        statusTmp = True   
                else :
                        statusTmp = True   
                        statusList.append("normal")
      
      
        self.status = statusTmp
        self.connectstatus = str(statusList)
        
        # reconnect breaklist
        for elem in breakConnlist:
            if elem.isBusy == False and self.isbreak != True and elem.isSleep != True:
                #print elem.ipaddress,elem.driverFile
                if elem.detectConnect() != True:
                    logger.error('Connection interruption, attempting to reconnect: %s, channel %s'% (elem.ipaddress,elem.sid))
                    elem.reconnect()
    
    def getEsnBySpeical(self, ip, port, username, password, driverFile):
        
       # recreate connection of device
       esnString = None
       if (self.connesn == None):
            exists = True
            try:
                mod = __import__(self.driverFile)
            except Exception as e:
                logger.error('device %s[%s] can not load the driver \'%s\', detail: producttype=%s and version=%s; %s'  %(self.name, self.deviceid,self.driverFile,self.productType, self.version, e))
                exists = False
            if (exists == True):
                self.connesn = ConnectM(ip, port, username, password, driverFile, 1)
                
       if (self.connesn != None):
           self.connesn.closeDevice()
           self.connesn.set_main_device(ip, port, username=username, password=password)
           logger.info('device %s[%s] getting esn , detail: ipaddress=%s, port=%s, username=%s'  %(self.name, self.deviceid, ip, port, username))
           try:
              esnString = self.connesn.get_esn()
           except Exception as e:
              logger.error('device %s[%s] getting esn , detail: ipaddress=%s, port=%s, username=%s, %s'  %(self.name, self.deviceid, ip, port, username, e))
           finally:
              self.connesn.closeDevice()
       return esnString
 
    def detectEsn(self):
        
        # not need to detect esn
        if (len(self.subdevices) == 0):
            return True
        
        esnTmpList = []
        
        # detect all device have same esn string
        if (self.esn == None or self.esn == ''):
            self.esn = self.getEsnBySpeical(self.ip, self.port, self.username, self.password, self.driverFile)
     
        #detect if subdevice esn is ok 
        detectisbreak = False
        for onsubdevice in self.subdevices:
            passwd = onsubdevice['passwd']
            ipaddress = onsubdevice['ip']
            port = onsubdevice['port']
            username = onsubdevice['username']
            esn = onsubdevice.get('esn')
            if (esn == None or esn == ''):
                esn = self.getEsnBySpeical(ipaddress, port, username, passwd, self.driverFile)
                onsubdevice['esn'] = esn
            if (esn != None and esn != ''):
                if(self.esn != None and self.esn != '' and self.esn != esn) :
                    
                    detectisbreak = True 
                    break
                elif(self.esn == None and self.esn == ''):
                    esnTmpList.append(esn)
  
        # detect if only subdevice can connect
        if (len(esnTmpList) > 0):
            esnstr = None
            for oneDeviceEsnStr in esnTmpList:
                if (esnstr == None):
                    esnstr = oneDeviceEsnStr
                else:
                    if (oneDeviceEsnStr != esnstr):
                        detectisbreak = True
            
        #set if esn is ok, continue set errmsg 
        self.isbreak = detectisbreak    
        if (detectisbreak == False):
            self.errmsg = ''
        else :
            self.errmsg = 'please confirm whether it is the same device' 
                    
    def getStatus(self):
        return self.status
            
    def getDevice(self):
        return self.connectstatus
    
    def addSubDevice(self, elem):
        self.subdevices.append(elem)
        for elemConn in self.connlist:
            elemConn.set_multi_ipaddress(self.subdevices)

    def deleteSubDevice(self, sid):
        for onsubdevice in self.subdevices:
            if (str(sid) == str(onsubdevice['id'])):
                self.subdevices.remove(onsubdevice)
                break

        for elemConn in self.connlist:
            elemConn.set_multi_ipaddress(self.subdevices)

    def modifySubDevice(self, sid, elem):
        for onsubdevice in self.subdevices:
            if (str(sid) == str(onsubdevice['id'])):
                onsubdevice['passwd'] = elem['passwd']
                onsubdevice['ip'] = elem['ip']
                onsubdevice['port'] = elem['port']
                onsubdevice['username'] = elem['username']
                break
        for elemConn in self.connlist:
            elemConn.set_multi_ipaddress(self.subdevices)
            
    def set_multi_ipaddress(self, devices=[]):
        self.subdevices = devices
    
    
    def get_esn(self):
        return self.esn
      #  try:
        #for elemConn in self.connlist:
            #esnList.append(elemConn.get_esn())
        
        #except Exception as e:
      #      print "error=%s"%e

    def set_main_device(self, ipaddress, port, username , password):
        self.ip = ipaddress
        self.username =username
        self.password = password
        self.port = port
        for elemConn in self.connlist:
            elemConn.set_main_device(ipaddress, port, username, password)

        

            