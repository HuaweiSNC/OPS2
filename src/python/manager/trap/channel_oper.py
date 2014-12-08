'''
Created on 2013-3-9

@author: Administrator
'''

import Queue
#===============================================================================
# 
#===============================================================================
class Channels():
    _list=[]
    def __init__(self):
        pass
    def add(self,chan):
        if self.search(chan._id) == None:
            self._list.append(chan)
    def delete(self,id):
        for i in self._list:
            if i._id == id:
                self._list.remove(i)    
    def show(self):
        for i in self._list:
            i.show()
    def search(self,id):
        for i in self._list:
            if i._id == id:
                return i
        return None
class Channel(object):
    _id=None
    _url=None
    _data_url=None
    
    _wsock=None
    _queue=None
    
    def __init__(self,id,url,url_data):
        self._id = id
        self._url = url
        self.url_data = url_data
        self._queue = Queue.Queue(100)
        pass
    def show(self):
        print '_id:%s,_wsock:%s,_url:%s,_Data_URL:%s,Queue:%s'%(self._id,self._wsock,self._url,self._Data_URL,self._queue)
