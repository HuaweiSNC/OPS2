'''

@author: x00106601
'''

def dbconn_trans(func):
    def connection(self,*args,**kwargs):
        #self.lock.acquire()
        conn = self.get_conn()
        kwargs['conn'] = conn
        rs = func(self,*args,**kwargs)
        self.conn_close(conn)
        #self.lock.release()
        return rs
    return connection

class SqlRowProxy(dict):

    def __init__(self, table, key, row, columns=None):
        
        _storedict = {}
        if (columns == None) :
            columns = table._columns
         
        rowid = 0;
        for (k, ktype) in columns:
            _storedict[k]=row[rowid]
            rowid=rowid+1

        li = ((k, v) for k, v in _storedict.items())
        dict.__init__(self, li)
        self._key = key

    def __setitem__(self, key, value):
        dict.__setitem__(self, key, value)
        
    def getjsonvalue(self, filter=['passwd']):
        retvalue = {}
        for d,x in self.items():
            if d in filter:
                retvalue[d] = ''
            else:
                retvalue[d] = x
        return retvalue
