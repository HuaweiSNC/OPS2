# -*- coding: utf-8 -*-
'''
Created on 2015-3-17

@author: x00302603

'''
import sqlite3

#===============================================================================
# DB Data struct 
#===============================================================================
ID = 0
GROUP = 1
URIREGULAR = 2
MODULENAME = 3
table_struct ={
               0: "id",
               1:'groupname',
               2:'uriregular',
               3:'modulename'
               }

#===============================================================================
# url mapping
#===============================================================================
class urlmapping_mgmt():
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
            
            self._conn.execute("create table if not exists urlmapping_table( id integer primary key autoincrement, \
                                                                          groupname varchar(128), \
                                                                          uriregular varchar(255), \
                                                                          modulename varchar(255));")
            self._cur = self._conn.cursor()
        except Exception, e:
            print repr(e)
            
    def __exit__(self):
        try:
            if (self._useselfdb == True and self._conn != None):
                self._conn.close()
            else:
                self._conn = None
        except:
            pass
        
    def find_urlmappingbyid(self,sid):
        try:
            tcontent =(sid,)
            c=self._cur.execute("select * from urlmapping_table where id = ?;", tcontent)
            res=c.fetchall()
            namelist=[]
            count=0
            for line in res:
                count=count+1
                namelist.append({'id': line[0], 'groupname':line[1],'uriregular':line[2],'modulename':line[3]})
            return namelist
       
        except:
            return None,None,None

    def find_urlmappingbygroup(self,groupname):
        try:
            tcontent =(groupname,)
            c=self._cur.execute("select * from urlmapping_table where groupname = ?;", tcontent)
            res=c.fetchall()
            namelist=[]
            count=0
            for line in res:
                count=count+1
                namelist.append({'id': line[0], 'groupname':line[1],'uriregular':line[2],'modulename':line[3]})
            return namelist
       
        except Exception as e:
            print repr(e)
            return None
        
    def find_urlmappingbygroupurl(self,groupname, uriregular):
        try:
            tcontent =(groupname,uriregular)
            self._cur.execute("select * from urlmapping_table where groupname = ? and uriregular=?;", tcontent)
            return self._cur.fetchone() 
            
        except Exception as e:
            print repr(e)
            return None
        
    def add_urlmapping(self,groupname,uriregular,modulename):
        try:
            
            tcontent =(groupname,uriregular,modulename)
            sql_state="insert into urlmapping_table(groupname, uriregular, modulename) values (?,?,?);"  
            if self.find_urlmappingbygroupurl(groupname,uriregular)!=None:
                tcontent =(modulename, groupname,uriregular)
                sql_state="update urlmapping_table set  modulename=? where groupname = ? and uriregular = ?;" 

            self._conn.execute(sql_state, tcontent)
            self._conn.commit()
     
            return True
        except Exception as e:
            print repr(e)
            return False
        
    def getAllUrlmappingInfo(self):
        try:
            c=self._cur.execute("select distinct * from urlmapping_table;")
            res=c.fetchall()
            namelist=[]
            count=0
            for line in res:
                count=count+1
                namelist.append({'id': line[0], 'groupname':line[1],'uriregular':line[2],'modulename':line[3]})
            return namelist
        except Exception as e:
            print repr(e)
            return []
           
    def delete_urlmapping_id(self, sid):
        try:
            tcontent =(sid,)
            sql_state='delete from urlmapping_table where id=?;'
            self._conn.execute(sql_state, tcontent)
            self._conn.commit()
            return True
        except:
            return False
         
    def delete_urlmapping(self, groupname):
        try:
            tcontent =(groupname,)
            sql_state='delete from urlmapping_table where groupname=?;' 
            self._conn.execute(sql_state, tcontent)
            self._conn.commit()
            return True
        except:
            return False
        
def geturlmappinginfo(db,productType,version):
    try:
        dm=urlmapping_mgmt(db)
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
    dm = urlmapping_mgmt(None,'D:/OPS2.db')
    dm.add_urlmapping('sshengine', '/execute/time', 'ovs.cmcc')
    print dm.find_urlmappingbygroup('sshengine')
    dm.add_urlmapping('user_111', '/execute/time', 'ovs.cmcc')
    dm.delete_urlmapping_id('1')
    dm.delete_urlmapping('sshengine')
   
    print dm.getAllUrlmappingInfo()
    
    