'''
Created on 2013-11-30

'''

import sqlite3
import base64
import os

from cipher_mgmt import EncodePassword

class WebAppDBMgt():
    def __init__(self,db=None,DBName=None):
        
        initialize = True
        if db != None:
            self._conn=db
        else:
            if not os.path.exists(DBName):
                initialize = False
            self._conn = sqlite3.connect(DBName)
            
        self._conn.execute("create table if not exists webappdb_table(username  varchar(128), \
                                                                      infoname varchar(128) primary key, \
                                                                      datatype varchar(128), \
                                                                     data varchar(65535));")
        
        if not initialize:
            self.add_userdata("admin", "password", "password", "admin")
        self._cur = self._conn.cursor()
    
    def __exit__(self):
        self._conn.close()

    def get_userdata(self,username,infoname):
        sql_state = "select username,infoname,datatype,data from webappdb_table where (username='%s' and infoname='%s');"%(str(username),str(infoname))  
        res = self._conn.execute(sql_state)   
        for line in res:
            if line[0] == username:
                #print line[3];
                return line          
        return None   
    
    def add_userdata(self,username,infoname,datatype,data):  
        res = self.get_userdata(username, infoname)
        if res != None:
            print 'add %s %s already exist.'%(username, infoname)
            return True  
        #print 'add info:', str(username),str(infoname),str(datatype),str(data)    
        sql_state="insert into webappdb_table(username,infoname,datatype,data) values ('%s','%s','%s','%s');"%(str(username),str(infoname),str(datatype),str(data))
        self._conn.execute(sql_state)
        self._conn.commit()
        return True   

    def delete_userdata(self,username,infoname):
        sql_state="delete from webappdb_table where (username='%s' and infoname='%s');"%(str(username),str(infoname))
        self._conn.execute(sql_state)
        self._conn.commit()
        return True
    
    def update_userdata(self,username,infoname,datatype,data):
        
        ret = self.get_userdata(username,infoname)
        if (ret == None):
            self.add_userdata(username,infoname,datatype,data)
        else:
            sql_state="update webappdb_table set datatype='%s',data='%s' where (username='%s' and infoname='%s');"%(str(datatype),str(data),str(username),str(infoname))
            self._conn.execute(sql_state)
            self._conn.commit()
        return True  
    
    def show_userdata(self):
        res=self._cur.execute("select * from webappdb_table;")
        namelist=[]
        for line in res:
            #print line
            namelist.append({'data':{'username':line[0],
                    'infoname':line[1],
                    'datatype':line[2],
                    'data':line[3]}})
        for elem in namelist:
            print elem
        return namelist

if __name__ == '__main__':
    # create a db handle
#    dm=WebAppDBMgt(None,'E:/dcdb.db')
#    print 'init data:'
#    dm.show_userdata()
#    print 'add:'
#    dm.add_userdata('admin', 'userdata', 'password', 'netconf123')
#    
#    dm.add_userdata('admin', 'userpage', 'data', 'netconf1ffffffffffffff23')
#    print 'after add:'
#    dm.show_userdata()    
#    dm.get_userdata('admin', 'userpage')
#    dm.get_userdata('admin', 'abcde')
#    
#    print 'upate:'
#    dm.update_userdata('admin', 'userdata', 'password', 'huawei')    
#    dm.update_userdata('admin', 'userpage', 'data', 'netconf1ffffffffffffff23')
#    print 'after update:'
#    dm.show_userdata()   
#    print 'delete:'
#    dm.delete_userdata('admin', 'userdata')
#    dm.delete_userdata('admin', 'userpage')
#    print 'after delete'
#    dm.show_userdata()  
     dm=WebAppDBMgt(None,'D:\install\src\webapps\dc\dc.db')
     dm.show_userdata()

   
    