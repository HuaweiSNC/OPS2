'''
Created on 2013-3-8

@author: m00147039
'''

import sqlite3
import base64
from cipher_mgmt import EncodePassword
from sqlrow_proxy import SqlRowProxy
import threading
import sys

class DevicesMgt(object):
    _conn = None
    _useselfdb = True
    _deviceIdList = {}
    _mutex = threading.Lock()
    
    def __iter__(self):
        return self
    
    def __init__(self,db=None,DBName=None):
        self._columns = (
            ('id', str),
            ('devicename', str),
            ('ip', str),
            ('port', str),
            ('username', str),
            ('passwd', str),
            ('productType', str),
            ('version', str) 
        )
          
        self._columns_subdevices = (
            ('id', str),
            ('sid', str),
            ('ip', str),
            ('port', str),
            ('username', str),
            ('passwd', str)  
        )
                
        if db != None:
            self._conn=db
            self._useselfdb = False
        else:
            self._conn = sqlite3.connect(DBName)
            self._useselfdb = True
        self._conn.execute("create table if not exists devices_table( id integer primary key, \
                                                                      devicename varchar(128), \
                                                                      ip varchar(128), \
                                                                      port integer, \
                                                                      username varchar(128), \
                                                                      passwd varchar(128), \
                                                                      productType varchar(128), \
                                                                      version varchar(128), \
                                                                      esn varchar(128) );")
        
        self._conn.execute("create table if not exists subdevices_table( id integer primary key, \
                                                                      sid varchar(128), \
                                                                      ip varchar(128), \
                                                                      port integer, \
                                                                      username varchar(128), \
                                                                      passwd varchar(128), \
                                                                      esn varchar(128)  );")
        self._cur = self._conn.cursor()
    
    def get_noexist_deviceid(self, devicename):
        
        deviceid = 0
        self._mutex.acquire() 
        maxint = sys.maxint
        while (deviceid < maxint):
            deviceid = deviceid + 1
            if (self._deviceIdList.get(str(deviceid)) is None):
                self._deviceIdList[str(deviceid)] = devicename
                break
        self._mutex.release()
        return deviceid
             
    def record_all_deviceid(self):
        self._deviceIdList.clear()
        res = self._cur.execute("select id,devicename  from devices_table ;")
        for line in res:
            lineId = int(line[0])
            devicename = line[1]
            self._deviceIdList[str(lineId)] = devicename
            
    def __exit__(self):
        if (self._useselfdb == True and self._conn != None):
            self._conn.close()
        else:
            self._conn = None
    
    def device_handle(self,devicename,ip,user_id):
        self.add_devices(devicename, ip,user_id)
        line=self.find_device(devicename)
        return line[0]  #Not use id but devicename
    
    def get_devicename(self,device_id):
        tcontent = (device_id,)
        self._cur.execute("select devicename from devices_table where id=?;", tcontent)
        row=self._cur.fetchone()
        if (row != None and isinstance(row, tuple)):
            return row[0]
        return None        
                
    def find_device(self,devicename):
        tcontent = (devicename, )
        self._cur.execute("select * from devices_table where devicename=?;", tcontent)
        rowold=self._cur.fetchone()
        if (rowold != None):
            return SqlRowProxy(self, 'id', rowold, self._columns)
        return None
    
    def find_devicebynamenotid(self,device_name,device_id):
        tcontent = (device_name,device_id,)
        self._cur.execute("select * from devices_table where devicename=? and id != ?;", tcontent)
        linebynamenotid=self._cur.fetchone()
        if (linebynamenotid != None):
            return SqlRowProxy(self, 'id', linebynamenotid, self._columns)
        return None
    
    def find_devicebyid(self,device_id):
        tcontent = (device_id,)
        self._cur.execute("select * from devices_table where id=?;", tcontent)
        rowbyid=self._cur.fetchone()
        if (rowbyid is not None):
            return {'id':rowbyid[0], 'devicename':rowbyid[1]}
        return None

    def find_subdevicebyid(self,id):
        self._cur.execute("select id,ip,port,username,passwd from subdevices_table where id = ?;", (id,))
        linesubid=self._cur.fetchone()
        if (linesubid != None and isinstance(linesubid, tuple)):
            return linesubid[0],linesubid[1], linesubid[2],linesubid[3],linesubid[4]
        return None,None,None,None,None
    
    def find_subdevicebyip(self,ip):
        sql_state="select id,ip,port,username,passwd from subdevices_table where ip=?;"
        self._cur.execute(sql_state, (ip,))
        line=self._cur.fetchone()
        if (line != None and isinstance(line, tuple)):
            return line[0],line[1], line[2],line[3],line[4]
        return None,None,None,None,None
     
    def add_devices(self,devicename,ip, port, username,passwd,productType,version, iid=None):
        if self.find_device(devicename)!=None:
            return False
        
        #encode the password before add to DB
        encryptpasswd=EncodePassword(passwd)  
        tcontent = (devicename,ip,port,username,encryptpasswd,productType,version)
        sql_state="insert into devices_table(devicename,ip,port,username,passwd,productType,version) values (?,?,?,?,?,?,?);"
        
        if (iid is None) :
            iid = self.get_noexist_deviceid(devicename)
   
        if (iid != None) :
            #the device id xxx is exist
            rowvaluebyid=self.find_devicebyid(iid)
            if (rowvaluebyid != None):
                return False 
            tcontent = (iid,devicename,ip,port,username,encryptpasswd,productType,version)
            sql_state="insert into devices_table(id,devicename,ip,port,username,passwd,productType,version) values (?,?,?,?,?,?,?,?);"
  
        retsql=self._conn.execute(sql_state, tcontent)
        self._conn.commit()
        lastrowid = iid
        if (iid is None and retsql != None):
            lastrowid = retsql.lastrowid
            
        self._mutex.acquire() 
        self._deviceIdList[str(lastrowid)] = devicename
        self._mutex.release()
        return lastrowid

    def show_devices(self):
        res=self._cur.execute("select * from devices_table;")
        namelist=[]
        for line in res:
            #print line
            rowValue = SqlRowProxy(self, 'id', line, self._columns)
            namelist.append({'device':rowValue.getjsonvalue()})
        return namelist
    
    def get_deviceinfos(self):
        res=self._cur.execute("select * from devices_table order by id;")
        namelist=[]
        
        for line in res:
            namelist.append({'id': line[0], 'devicename':line[1],'ip':line[2],'port':line[3],'username':line[4],'passwd':line[5],'productType':line[6],'version':line[7]})
        
        for deviceinfo in namelist:
            deviceId= deviceinfo['id']
            deviceinfo['subdevices'] = self.get_subdevices(deviceId)
        return namelist

    def delete_device(self,devicename):
        line=self.find_device(devicename)
        if line== None:
            return False
        
        deviceid = int(line[0])
        return self.delete_devicebyid(deviceid)

    def delete_devicebyid(self, id):
        tcontent = (id,)
        sql_state='delete from devices_table where id=?;'
        retsql = self._conn.execute(sql_state, tcontent)
        self._conn.commit()
        #self._deviceIdList.pop(str(id))
        deviceid = str(id)
        if (self._deviceIdList.get(deviceid) != None):
            self._deviceIdList.pop(deviceid)
        return (retsql.rowcount != 0)
    
    def update_device(self, deviceid, devicename,ip,port,username,passwd,productType,version):
        
        #if find device by devicename then update by devicename
        if (deviceid != None):
            rowvaluebyid=self.find_devicebyid(deviceid)
            if (rowvaluebyid == None):
                return False 
            else:
                if (rowvaluebyid.get('devicename') != devicename):
                    rowvaluebynotid = self.find_devicebynamenotid(devicename, deviceid)
                    if (rowvaluebynotid != None):
                        return False
        else:
            rowvaluebyname=self.find_device(devicename)
            if (rowvaluebyname == None):
                return False
        
        #print "find the device",line
        encryptpasswd=EncodePassword(passwd)
        tcontent = (devicename,ip,username,encryptpasswd,productType,version,devicename)
        sql_state='update devices_table set devicename=?,ip=?,username=?,passwd=?,productType=?,version=? where devicename=?;'
        if (deviceid == None and port != None):
            tcontent = (devicename,ip,port,username,encryptpasswd,productType,version,devicename)
            sql_state='update devices_table set devicename=?,ip=?, port=?, username=?,passwd=?,productType=?,version=? where devicename=?;'
         
        #print passwd
        if (deviceid != None):
            tcontent = (devicename,ip,username,encryptpasswd,productType,version,deviceid)
            sql_state='update devices_table set devicename=?,ip=?,username=?,passwd=?,productType=?,version=? where id=?;'
 
        if (deviceid != None and port != None):
            tcontent = (devicename,ip,port,username,encryptpasswd,productType,version,deviceid)
            sql_state='update devices_table set devicename=?,ip=?,port=?,username=?,passwd=?,productType=?,version=? where id=?;'
       
       
        self._conn.execute(sql_state, tcontent)
        self._conn.commit()
        return True
    
    def delete_alldevices(self):
        self._cur.execute("delete from devices_table;")
        self._conn.commit()
        self._deviceIdList.clear()
        return True
    
    #====================sudevice begin=======================
    
    def add_subdevices(self, sid, ip, port, username,passwd):
        if self.find_devicebyid(sid) == None:
            return False
        
        #encode the password before add to DB
        encryptpasswd=EncodePassword(passwd)   
        tcontent = (sid,ip,port,username,encryptpasswd)
        sql_state="insert into subdevices_table(sid,ip,port,username,passwd) values (?,?,?,?,?);"
        retsql=self._conn.execute(sql_state, tcontent)
        self._conn.commit()
        lastrowid = 0
        if (retsql != None):
            lastrowid = retsql.lastrowid
        return lastrowid
    
    def get_subdevices(self, device_id):
        subdevicestmp = []
        tcontent = (device_id,)
        sql_state="select id,sid, ip, port, username, passwd from subdevices_table where sid=?;"
        res=self._cur.execute(sql_state, tcontent)
        for row in res:
            onedevicestmp = SqlRowProxy(self, 'username', row, self._columns_subdevices)
            subdevicestmp.append(onedevicestmp)
        return subdevicestmp   
       
    def delete_subdevicebyid(self,id):
        sql_state='delete from subdevices_table where id=?;' 
        tcontent=(id, )
        retsql = self._conn.execute(sql_state, tcontent)
        self._conn.commit()
        return (retsql.rowcount != 0)
    
    def delete_subdevicebydeviceid(self,sid):
        sql_state='delete from subdevices_table where sid=?;' 
        tcontent=(sid, )
        retsql = self._conn.execute(sql_state, tcontent)
        self._conn.commit()
        return (retsql.rowcount != 0)
    
    def update_subdevice(self, id, ip, port, username, passwd):        
        line=self.find_subdevicebyid(id)
        if line == None:
            return False
 
        #print "find the device",line
        encryptpasswd=EncodePassword(passwd)
        tcontent=(ip,port,username,encryptpasswd,id)
        #print passwd
        sql_state='update subdevices_table set ip=?,port=?,username=?,passwd=?  where id=?;'
        self._conn.execute(sql_state, tcontent)
        self._conn.commit()

        return True
    ##--------------subdevice end--------------------------------------
    
##------------------subdevice begin-----------------------
def addonesubdevice(db, sid, ddict):
    device_db =  DevicesMgt(db)
    ret = device_db.add_subdevices(sid, ddict['ip'], ddict['port'], ddict['username'], ddict['passwd'] )
    if ret == False:
        return
    line =device_db.find_subdevicebyip(ddict['ip'])
    return line[0]

 
##-----------------subdevice end---------------------------

##-------------------------------------------------------------------------------
##-- Class Name      : add/delete/get/show operator of devices
##-- Date Created    : 
##-- Author          :
##-- Description     :
##-- Caution         :
##------------------------------------------------------------------------------
 
##-------------------------------------------------------------------------------
##-- main process in this module
##-- if you ran this module, the following code would be executed independently.
##-------------------------------------------------------------------------------
 

if __name__ == '__main__':
    # create a db handle
    dm=DevicesMgt(None,'D:/OPS2.db')
    print '^'*30
    dm.show_devices()
    
    # add devices to DB
    dm.delete_alldevices()
    dm.add_devices('10.137.210.122', '10.137.210.122', 'netconf', 'netconf123', 'NE5000E', '1.0')
    dm.add_devices('10.137.210.66', '10.137.210.66', 'netconf', 'netconf123', 'NE5000E', '1.0')
    print '^'*30
    dm.show_devices()
    print dm.find_devicebyid('2')
    
    #print dm.find_devicebyid(1)
    print '^'*30
    print dm.show_devices()
    a = '84566'
    print a.isdigit()   
    print 2147483647   
    import sys
    print int(a) > sys.maxint 
    print int(a)
    