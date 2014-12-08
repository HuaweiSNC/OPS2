'''

@author: x00106601
'''
import sqlite3
from datetime import datetime
from sqlrow_proxy import SqlRowProxy

def ni(*args, **kwargs):
    raise NotImplementedError

class users_mgmt(object):
    
    _conn = None
    _useselfdb = True
    
    def __init__(self,db=None,DBName=None):
        self._columns = (
            ('username', str),
            ('passwd', str),
            ('role', str),
            ('desc', str),
            ('creation_date', str),
            ('last_login', str)
        )
                
        try:
            if db != None:
                self._conn=db
                self._useselfdb = False
            else:
                self._conn = sqlite3.connect(DBName)
                self._useselfdb = True
            
            self._conn.execute("create table if not exists users_table(   username TEXT PRIMARY KEY ASC, \
                                                                          passwd TEXT, \
                                                                          role TEXT, \
                                                                          desc TEXT, \
                                                                          creation_date TEXT, \
                                                                          last_login TEXT );")
            self._cur = self._conn.cursor()
        except Exception as e:
            print 'error: %s' %e
            
    def __exit__(self):
        try:
            if (self._useselfdb == True and self._conn != None):
                self._conn.close()
            else:
                self._conn = None
        except:
            pass
        
    def __iter__(self):
        return self
    
    def next(self):
        if self.index == 0:
            raise StopIteration
        self.index = self.index - 1
        return self.data[self.index]
    
    def find_user(self, username):
        try:
            tcontent = (username,)
            self._cur.execute("select username, passwd, role, desc,creation_date,last_login  from users_table where username=? ;", tcontent)
            row = self._cur.fetchone()
            if (row != None and isinstance(row, tuple)):
                row_value = SqlRowProxy(self, 'username', row)
                return row_value
            
        except Exception as e:
            print 'error: %s' %e
            return None, str(e)
    
    def modify_passwd(self, username, newpasswd):
        try:
            #return False
            sql_state='update users_table set passwd=? where username=? ;'
            tcontent = (newpasswd, username)
            self._conn.execute(sql_state, tcontent)
            self._conn.commit()
            return True
        except Exception as e:
            return False, str(e)
         
    def modify_user(self, username, passwd, role, desc):
        try:
            if self.find_user(username)!=None:
                #return False
                sql_state='update users_table set passwd=?, role=?, desc=? where username=? ;'
                tcontent = (passwd, role, desc, username)
                self._conn.execute(sql_state, tcontent)
                self._conn.commit()
            return True
        except Exception as e:
            return False, str(e)
        
    def add_user(self, username, passwd, role, desc):
        try:
            tstamp = str(datetime.utcnow())
            tcontent = (username, passwd, role, desc, tstamp)
            sql_state="insert into users_table(username,passwd,role,desc,creation_date) values (?,?,?,?,?);"
                
            if self.find_user(username)!=None:
                return False, str('exists user %s', username)
                #sql_state='update users_table set passwd=?, role=?, desc=? where username=? ;'
                #tcontent = (passwd, role, desc, username)
       
            self._conn.execute(sql_state, tcontent)
            self._conn.commit()
            return True
        except Exception as e:
            return False, str(e)
        
    def show_user(self):
        try:
            rows=self._cur.execute("select * from users_table;")
            rowsvalue = []
            if (rows != None):
                for row in rows:
                    row_value = SqlRowProxy(self, 'username', row)
                    rowsvalue.append(row_value.getjsonvalue())
            return rowsvalue
        except Exception as e:
            return None, str(e)  
 
           
    def delete_user(self, username):
        try:
            tcontent = (username,)
            sql_state='delete from users_table where username=?;'
            self._conn.execute(sql_state, tcontent)
            self._conn.commit()
            return True
        except Exception as e:
            return False, str(e)
        
if __name__ == '__main__':
    #===========================================================================
    # Unit test samples  , username, passwd, role, desc):
    #===========================================================================
    dm = users_mgmt(None,'D:/OPS2.db')
    dm.add_user('test', 'testtt', 'admin', 'the test name')
    dm.add_user('test2', 'testtt', 'admin', 'the test name')
    print dm.show_user()  
    
    dm.modify_user('test', 'xeee', 'ettt', 'the test name')
    print dm.show_user()  
 
    findtest = dm.find_user('test')
    print findtest
    
    dm.delete_user('test')
    print dm.show_user()