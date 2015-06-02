'''

@author: x00106601
'''
import sqlite3
from datetime import datetime
from sqlrow_proxy import SqlRowProxy

class whitelist_mgmt(object):
    
    _conn = None
    _useselfdb = True
    
    def __init__(self,db=None,DBName=None):
        self._columns = (
            ('ipaddress', str),
            ('desc', str) 
        )
                
        try:
            if db != None:
                self._conn=db
                self._useselfdb = False
            else:
                self._conn = sqlite3.connect(DBName)
                self._useselfdb = True
            
            self._conn.execute("create table if not exists whitelist_table( ipaddress TEXT PRIMARY KEY ASC, \
                                                                            desc TEXT );")
            self._cur = self._conn.cursor()
        except Exception as e:
            print 'error:%s' %e
            pass
    def __exit__(self):
        try:
            if (self._useselfdb == True and self._conn != None):
                self._conn.close()
            else:
                self._conn = None
        except:
            pass
        
   
    def find_ipaddr(self, ipaddress):
        try:
            tcontent = (ipaddress,)
            self._cur.execute("select ipaddress, desc  from whitelist_table where ipaddress=? ;", tcontent)
            row = self._cur.fetchone()
            if (row != None and isinstance(row, tuple)):
                row_value = SqlRowProxy(self, 'ipaddress', row)
                return row_value
            
        except Exception as e:
            print 'error: %s' %e
            return None
        return None
        
    def modify_ipaddr(self, ipaddress, desc):
        try:
        
            sql_state='update whitelist_table set ipaddress=?, desc=? where ipaddress=? ;'
            tcontent = (ipaddress, desc, ipaddress)
            self._conn.execute(sql_state, tcontent)
            self._conn.commit()
            return True
        except:
            return False
        
    def add_ipaddr(self, ipaddress, desc):
        try:
            if self.find_ipaddr(ipaddress)!=None:
                return self.modify_role(ipaddress)
            tcontent = (ipaddress, desc)
            sql_state="insert into whitelist_table(ipaddress, desc) values (?,?);"
            self._conn.execute(sql_state, tcontent)
            self._conn.commit()
            return True
        except Exception as e:
            print 'error:%s' %e
            return False
        
    def show_ipaddr(self):
        try:
            rows=self._cur.execute("select * from whitelist_table;")
            rowsvalue = []
            if (rows != None):
                for row in rows:
                    row_value = SqlRowProxy(self, 'ipaddress', row)
                    rowsvalue.append(row_value)
            return rowsvalue
        except Exception as e:
            print 'error:%s' %e
            return None   
 
           
    def delete_ipaddr(self, ipaddress):
        try:
            tcontent = (ipaddress,)
            sql_state='delete from whitelist_table where ipaddress=?;'
            self._conn.execute(sql_state, tcontent)
            self._conn.commit()
            return True
        except Exception as e:
            print 'error:%s' %e
            return False
        
        
if __name__ == '__main__':
    dm = whitelist_mgmt(None,'D:/OPS2.db')
    dm.add_ipaddr('10.138.91.247', 'good admin')
    dm.add_ipaddr('localhost', 'good admin')
    print dm.show_ipaddr()  
    
    print dm.find_ipaddr('localhost')
   
    dm.delete_ipaddr('localhost')
    print dm.show_ipaddr()  