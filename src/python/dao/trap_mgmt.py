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
AGENT = 1
VERSION = 2
OID = 3
TRAPDATA = 4

table_struct ={
               0: "id",
               1:'agent',
               2:'version',
               3:'oid',
               4:'trapdata'
               }

#===============================================================================
# �豸������
#===============================================================================
class traps_mgmt():
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
            
            self._conn.execute("create table if not exists traps_table( id integer primary key autoincrement, \
                                                                          agent    varchar(128), \
                                                                          version  varchar(128), \
                                                                          oid      varchar(128), \
                                                                          trapdata text);")
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
    
    def find_trapbyid(self,id):
        try:
            tcontent =(id,)
            self._cur.execute("select * from traps_table where id = ?;", tcontent)
            line = self._cur.fetchone()
            if (line is not None):
                return line[AGENT],line[VERSION],line[OID],line[TRAPDATA]
            return None,None,None
        except:
            return None,None,None
        
    def add_trap(self,agentip,version,oid, trapdata):
        try:
            
            tcontent =(agentip, version, oid, trapdata)
            sql_state="insert into traps_table(agent,version,oid,trapdata) values (?,?,?,?);"  

            self._conn.execute(sql_state, tcontent)
            self._conn.commit()
            return True
        except:
            return False
        
    def show_trap(self):
        try:
            res=self._cur.execute("select * from traps_table;")
            for line in res:
                print line
            return None
        except:
            return None   
        
    def getAllTrapsInfo(self):
        try:
            c=self._cur.execute("select distinct * from traps_table;")
            res=c.fetchall()
            namelist=[]
            count=0
            for line in res:
                count=count+1
                namelist.append({'id': line[0], 'agent':line[1],'version':line[2],'oid':line[3],'trapdata':line[4]})
            return namelist
        except:
            return namelist
           
    def delete_trap_id(self, sid):
        try:
            tcontent =(sid,)
            sql_state='delete from traps_table where id=?;'
            self._conn.execute(sql_state, tcontent)
            self._conn.commit()
            return True
        except:
            return False
         
    def delete_trap(self, agent):
        try:
             
            tcontent =(agent,)
            sql_state='delete from traps_table where agent=?;' 
            self._conn.execute(sql_state, tcontent)
            self._conn.commit()
            return True
        except:
            return False
         
if __name__ == '__main__':
    #===========================================================================
    # Unit test samples
    #===========================================================================
    dm = traps_mgmt(None,'D:/OPS2.db')
    dm.add_trap('10.28.91.247', 'v1', '1.1.5.81.4.9','<trap>data</trap>')
    #dm.delete_trap('10.28.91.247')
    dm.show_trap()
    print dm.find_trapbyid('1')
    
    print dm.getAllTrapsInfo()
    