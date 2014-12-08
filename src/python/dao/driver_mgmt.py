# -*- coding: utf-8 -*-
'''
Created on 2013-3-8

@author: m00147039

'''
import sqlite3

#===============================================================================
# DB Data struct 
#===============================================================================
ID = 0
PROCDUCTTYPE = 1
VERSION = 2
MODULENAME = 3
table_struct ={
               0: "id",
               1:'producttype',
               2:'version',
               3:'modulename'
               }

#===============================================================================
# �豸������
#===============================================================================
class driver_mgmt():
    _conn = None
    _useselfdb = True
    def __init__(self,db=None,DBName=None):
        try:
            if db != None:
                self._conn=db
                self._useselfdb = False
            else:
                self._conn = sqlite3.connect(DBName)
                self._useselfdb = True
            
            self._conn.execute("create table if not exists drivers_table( id integer primary key autoincrement, \
                                                                          productType varchar(128), \
                                                                          version varchar(128), \
                                                                          modulename varchar(128));")
            self._cur = self._conn.cursor()
        except:
            pass
    def __exit__(self):
        try:
            if (self._useselfdb == True and self._conn != None):
                self._conn.close()
            else:
                self._conn = None
        except:
            pass
    
    def find_driver(self,productType,version):
        try:
            tcontent =(productType,version)
            self._cur.execute("select * from drivers_table where productType=? and version=?;", tcontent)
            return self._cur.fetchone()
        except:
            return None
    def find_driverbyid(self,id):
        try:
            tcontent =(id,)
            self._cur.execute("select * from drivers_table where id = ?;", tcontent)
            line = self._cur.fetchone()
            if (line is not None):
                return line[PROCDUCTTYPE],line[VERSION],line[MODULENAME]
            return None,None,None
        except:
            return None,None,None
    def add_driver(self,productType,version,modulename):
        try:
            
            tcontent =(productType,version,modulename)
            sql_state="insert into drivers_table(productType,version,modulename) values (?,?,?);"  
            if self.find_driver(productType,version)!=None:
                tcontent =(productType,version,modulename,productType,version)
                sql_state='update drivers_table set productType=?,version=?,modulename=? where productType=? and version=? ;'

            self._conn.execute(sql_state, tcontent)
            self._conn.commit()
            return True
        except:
            return False
        
    def show_drivers(self):
        try:
            res=self._cur.execute("select * from drivers_table;")
            for line in res:
                print line
            return None
        except:
            return None   
        
    def getAllDriverInfo(self):
        try:
            c=self._cur.execute("select distinct * from drivers_table;")
            res=c.fetchall()
            namelist=[]
            count=0
            for line in res:
                count=count+1
                namelist.append({'id': line[0], 'productType':line[1],'version':line[2],'driverFile':line[3]})
            return namelist
        except:
            return namelist
           
    def delete_driver_id(self, sid):
        try:
            tcontent =(sid,)
            sql_state='delete from drivers_table where id=?;'
            self._conn.execute(sql_state, tcontent)
            self._conn.commit()
            return True
        except:
            return False
         
    def delete_driver(self, productType,version):
        try:
            line=self.find_driver(productType,version)
            if line== None:
                return False
            tcontent =(line[0],)
            sql_state='delete from drivers_table where id=?;' 
            self._conn.execute(sql_state, tcontent)
            self._conn.commit()
            return True
        except:
            return False
        
def getdriverinfo(db,productType,version):
    try:
        dm=driver_mgmt(db)
        line=dm.find_driver(productType, version)
        if line == None:
            return None
        else:
            return line[MODULENAME]
    except:
        return None
    
if __name__ == '__main__':
    #===========================================================================
    # Unit test samples
    #===========================================================================
    dm = driver_mgmt(None,'D:/OPS2.db')
    dm.add_driver('NE5000E', '1.0', 'xxx_Driver.py')
    dm.delete_driver('NE5000E', '1.0')
    dm.show_drivers()
    print dm.find_driver('NE5000E', '1.0')
    