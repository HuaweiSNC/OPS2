'''
 

@author: x00106601
'''
from dao.users_mgmt import users_mgmt
from dao.userroles_mgmt import userroles_mgmt
from dao.whitelist_mgmt import whitelist_mgmt
from dao.sqlrow_proxy import dbconn_trans

import threading
from cipher_mgmt import encrypt_password, validate_password

class AuthBackend():

    AUTH_USER=50
    AUTH_ADMIN=100
    AUTH_SPECIAL=200
    
    _usersStore = {}
    _rolesStore = {}
    lock = threading.RLock()
    mutex = threading.RLock()
    LOADDB_FAILED = 'failed to load sqlite db '

    def __init__(self, filename, initialize=False):

        import sqlite3
        self._filename = filename
        conn = self.get_conn()
        try:
            if initialize:
                users = users_mgmt(conn)
                roles = userroles_mgmt(conn)
                whitelist = whitelist_mgmt(conn)
                if (users.find_user('admin') is None):
                    users.add_user('admin', self._encode_password('admin') , self.AUTH_ADMIN, 'init admin')
                #if (users.find_user('guest') is None):    
                #    users.add_user('guest', self._encode_password('guest'), self.AUTH_USER, 'init user')
                if (whitelist.find_ipaddr('127.0.0.1') is None):
                    whitelist.add_ipaddr('127.0.0.1', 'loopback ipaddress')
                if (whitelist.find_ipaddr('localhost') is None):
                    whitelist.add_ipaddr('localhost', 'localhost ipaddress')
                if (roles.find_role('special') is None):
                    roles.add_role('special', self.AUTH_SPECIAL, 'Super user privilege')
                if (roles.find_role('admin') is None):
                    roles.add_role('admin', self.AUTH_ADMIN, 'Management user privilege')
                if (roles.find_role('user') is None):
                    roles.add_role('user', self.AUTH_USER, 'Common user privilege')
                
        except sqlite3.IntegrityError, e:
            conn.rollback()
        finally:
            conn.close()
            

    
    def get_conn(self):
        try:
            import sqlite3
            conn = sqlite3.connect(self._filename)
            return conn
        except AttributeError, e:
            print 'error : %s' , e
            
    def conn_close(self,conn=None):
        if (conn != None):
            conn.close()
        
#=======================user start=======================

    @dbconn_trans
    def reset_password(self, user, newpasswd, conn=None):
        if conn == None : 
            return None, self.LOADDB_FAILED
        users = users_mgmt(conn)
        bret = users.modify_passwd(user, self._encode_password(newpasswd))
        self.mutex.acquire()
        if bret :
            storeuser = self._usersStore.get(user)
            if (storeuser != None) : 
                storeuser['realpasswd'] = newpasswd
        self.mutex.release()
        return bret
    
    @dbconn_trans
    def add_user(self, username, passwd, role, desc, conn=None):
        if conn == None : 
            return None, self.LOADDB_FAILED
        users = users_mgmt(conn)
        return users.add_user(username, self._encode_password(passwd), role, desc)
 
    @dbconn_trans
    def modify_user(self, username, passwd, role, desc, conn=None):
        if conn == None : 
            return None, self.LOADDB_FAILED
        users = users_mgmt(conn)
        bret = users.modify_user(username, self._encode_password(passwd) , role, desc)
        self.mutex.acquire()
        if bret :
            storeuser = self._usersStore.get(username)
            if (storeuser != None) : 
                storeuser['realpasswd'] = passwd
        self.mutex.release()
        return bret
    
    @dbconn_trans
    def delete_user(self, user, conn=None):
        if conn == None : 
            return None, self.LOADDB_FAILED
        users = users_mgmt(conn)
        bret = users.delete_user(user)
        self.mutex.acquire()
        if bret :
            try:
                storeuser = self._usersStore.get(user)
                if (storeuser != None) : 
                    self._usersStore.pop(user)
            except Exception, e:
                print repr(e)
        self.mutex.release()
        return bret

    @dbconn_trans
    def show_user(self, conn=None):
        if conn == None : 
            return None, self.LOADDB_FAILED
        users = users_mgmt(conn)
        return users.show_user()
    
    @dbconn_trans
    def find_user(self, user, conn=None):
        if conn == None : 
            return None, self.LOADDB_FAILED
        users = users_mgmt(conn)
        return users.find_user(user)
    
#=======================user end=======================

#=======================role start=====================
    @dbconn_trans
    def show_role(self, conn=None):
        if conn == None : 
            return None, self.LOADDB_FAILED
        roles = userroles_mgmt(conn)
        return roles.show_role()
    
#=======================role end=====================

#=======================whitelist start=====================
    @dbconn_trans
    def checkipaddress(self, remoteip, conn=None):
        if conn == None : 
            return None, self.LOADDB_FAILED
        whitelist = whitelist_mgmt(conn)
        ipaddress = whitelist.find_ipaddr(remoteip)
        return (ipaddress != None)

    @dbconn_trans
    def show_whitelist(self, conn=None):
        if conn == None : 
            return None, self.LOADDB_FAILED
        whitelist = whitelist_mgmt(conn)
        return whitelist.show_ipaddr()
    
    @dbconn_trans
    def add_whitelist(self, ipaddress, desc, conn=None):
        if conn == None : 
            return None, self.LOADDB_FAILED
        whitelist = whitelist_mgmt(conn)
        return whitelist.add_ipaddr(ipaddress, desc)
    
    @dbconn_trans
    def modify_whitelist(self, ipaddress, desc, conn=None):
        if conn == None : 
            return None, self.LOADDB_FAILED
        whitelist = whitelist_mgmt(conn)
        return whitelist.modify_ipaddr(ipaddress, desc)
    
    @dbconn_trans
    def delete_whitelist(self, ipaddress, conn=None):
        if conn == None : 
            return None, self.LOADDB_FAILED
        whitelist = whitelist_mgmt(conn)
        return whitelist.delete_ipaddr(ipaddress)
    
#=======================whitelist end=====================

        
#=======================user end=======================
    def login(self, user, passwd, needrole):
        #block ip address and password check
        
        isAuth = None
        storeuser = None
        
        # find user from userstore
        if self.mutex.acquire(1): 
            storeuser = self._usersStore.get(user)
            if (storeuser != None) : 
                realencryptor = storeuser.get('realpasswd')
                role = storeuser.get('role')
                if (realencryptor != None):
                    isAuth = ((passwd==realencryptor) and (int(role) >= int(needrole)))
            self.mutex.release()
            
        #detect from database
        if (storeuser == None):
            storeuser = self.find_user(user) 
            if (storeuser != None) : 
                
                encryptor = storeuser.get('passwd') 
                role = storeuser.get('role')
                isAuth = self._verify_password(user, passwd, encryptor)
                isAuth = (isAuth and ( int(role) >=  int(needrole)))
                if isAuth ==True:
                    storeuser['realpasswd'] = passwd
                    if self.mutex.acquire(1): 
                        self._usersStore[user] = storeuser
                        self.mutex.release()
   
        if (isAuth == None) : 
            isAuth = False
            
        return isAuth
     
    def _encode_password(self, pwd):
        return encrypt_password(pwd)
    
    def _verify_password(self, username, pwd, salted_hash):
        
        return validate_password(salted_hash, pwd)
    