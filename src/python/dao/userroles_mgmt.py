'''

@author: x00106601
'''
import sqlite3
from datetime import datetime
from sqlrow_proxy import SqlRowProxy

class userroles_mgmt(object):
    
    _conn = None
    _useselfdb = True
    
    
    def __init__(self,db=None,DBName=None):
        self._columns = (
            ('role', str),
            ('level', str) ,
            ('desc', str) 
        )
                
        try:
            if db != None:
                self._conn=db
                self._useselfdb = False
            else:
                self._conn = sqlite3.connect(DBName)
                self._useselfdb = True
            
            self._conn.execute("create table if not exists role_table(   role TEXT PRIMARY KEY ASC, \
                                                                          level INTEGER , \
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
        
   
    def find_role(self, role):
        try:
            tcontent = (role,)
            self._cur.execute("select role, level, desc  from role_table where role=? ;", tcontent)
            row = self._cur.fetchone()
            if (row != None and isinstance(row, tuple)):
                row_value = SqlRowProxy(self, 'role', row)
                return row_value
            
        except Exception as e:
            print 'error: %s' %e
            return None
        return None
        
    def modify_role(self, role, level, desc):
        try:
        
            sql_state='update role_table set level=?, desc=? where role=? ;'
            tcontent = (level, desc, role)
            self._conn.execute(sql_state, tcontent)
            self._conn.commit()
            return True
        except:
            return False
        
    def add_role(self, role, level, desc):
        try:
            if self.find_role(role)!=None:
                return self.modify_role(role, level, desc)
            tcontent = (role, level, desc)
            sql_state="insert into role_table(role,level, desc) values (?,?,?);"
            self._conn.execute(sql_state, tcontent)
            self._conn.commit()
            return True
        except Exception as e:
            print 'error:%s' %e
            return False
        
    def show_role(self):
        try:
            rows=self._cur.execute("select * from role_table;")
            rowsvalue = []
            if (rows != None):
                for row in rows:
                    row_value = SqlRowProxy(self, 'role', row)
                    rowsvalue.append(row_value)
            return rowsvalue
        except Exception as e:
            print 'error:%s' %e
            return None   
 
           
    def delete_role(self, role):
        try:
            tcontent = (role,)
            sql_state='delete from role_table where role=?;'
            self._conn.execute(sql_state, tcontent)
            self._conn.commit()
            return True
        except Exception as e:
            print 'error:%s' %e
            return False
        
        
if __name__ == '__main__':
    dm = userroles_mgmt(None,'D:/OPS2.db')
    dm.add_role('special', 200, 'good admin')
    dm.add_role('admin', 100, 'good admin')
    dm.add_role('user', 50, 'good admin')
    print dm.show_role()  
    
    print dm.find_role('special')
   
    dm.delete_role('special')
    print dm.show_role()  