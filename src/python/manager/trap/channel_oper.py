'''
Created on 2013-3-9

@author: Administrator
'''

import Queue
import config
import logging 
logger = logging.getLogger("trap.channel") 


from manager.trap.snmp_traprcv import TrapRules
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
            
    def remove(self,chan):
        self._list.remove(chan)
                
    def delete(self, sid):
        for i in self._list:
            if i._id == sid:
                self._list.remove(i)    
    def show(self):
        for i in self._list:
            i.show()
            
    def search(self, sid):
        for i in self._list:
            if i._id == sid:
                return i
        return None
    
    def dispatch(self,notify,traprecord):
        for onechannel in self._list:
            onechannel.accept(notify, traprecord)

class Channel(object):
    _id=None
    _url=None
    _data_url=None
    _queue=None
    
    def __init__(self, sid,url, wsock=None, mytraprule=None):
        self._id = sid
        self._url = url
        self._queue = Queue.Queue(100)
        self._wsock = wsock
        self.traprule=mytraprule
    
    def isaccept(self, notifynode):
        
        #detect if host ip 
        if ( self.traprule.host != None and self.traprule.host != '' and self.traprule.host !='*' ):
            if self.traprule.host != str(notifynode.host):
                return False
        
        #detect if oid 
        if (  self.traprule.trap_oid != None and self.traprule.trap_oid != '' and self.traprule.trap_oid != '*' ):
            if self.traprule.trap_oid != str(notifynode.trap_oid):
                return False
            
        return True
    
    def accept(self, notifynode, traprecord):
        if not self.isaccept(notifynode):
            return False
        
        if self._wsock == None:
            return False
        
        import json
        from xmlTojson import isdk_convert_xml2json
        body = isdk_convert_xml2json(traprecord)
        body = json.dumps(body, sort_keys=True, indent=4, separators=(', ',': '))
        #body=json.loads(body)
        try:
            #print '==%s=' % body
            self._wsock.send(body)
        except Exception, e:
            print repr(e)
            logger.error ('failed to accept the data : %s' % e)
            
    def show(self):
        print '_id:%s,_wsock:%s,_url:%s,_Data_URL:%s,Queue:%s'%(self._id,self._wsock,self._url,self._Data_URL,self._queue)
