'''
Created on 2013-3-9

@author: Administrator
'''
import httplib
import json
from urlparse import urlparse
class Notification_Client():
    
    def __init__(self,url):
        _,self._netloc,_,_,_,_ = urlparse(url)
        self.conn = httplib.HTTPConnection(self._netloc)  
        self._channel_id = None
        self._Channel_Data=None 
        pass
    def __exit__(self):
        self.conn.close()
    def create_channel(self,channel_id):
        # build http://127.0.0.1:8080/channels/<channel_id>
        self.conn.request('post', '/channels/%s'%str(channel_id))  
        #print self.conn.getresponse().read()
        res = self.conn.getresponse()
        res.read()
        if res.status == 200:
            self._channel_id=channel_id
        
        
    def LLR(self):
        from websocket import create_connection
        from urlparse import urlunparse
        url = urlunparse(('ws',self._netloc,'/channels/%s/data'%str(self._channel_id),None,None,None))
        print url
        try:
            ws = create_connection(url)
        except:
            print "creat connect fail"
            return
        print "Reeiving..."
        try:
            self._Channel_Data =  ws.recv()
        except:
            print "receive no data"
            return
        print "Received '%s'" % self._Channel_Data
        #jsoninfo = json.dumps(self._Channel_Data)     
        #print jsoninfo   
        #vblists = jsoninfo['bind']
        #print vblists
        data = self._Channel_Data
        '''
        if data.find('log') != -1 and data.find('Command=') != -1:
            logdata1, logdata2 = data.split('Command=')
            commanddata = logdata2.split('\\\"')
            command = commanddata[1]   
        '''
        if data.find('log') != -1 and data.find('linkdown(t)') != -1 and data.find('ifName=Ethernet1/0/0'):
            pass
            #print 'run shutdown'
            #ifm = IfmInterface("10.135.34.246", 8080, 14)
            #ifm.down('Ethernet2/0/0')
        #if data.find('log') != -1 and data.find('linkup(t)') != -1 and data.find('ifName=Ethernet1/0/0'):
            #print 'run shutup'
            #ifm = IfmInterface("10.135.34.246", 8080, 14)
            #ifm.up('Ethernet2/0/0')
        #ws.close()
        
    def close_channel(self,channel_id):
        self.conn.request('delete', '/channels/%s'%str(channel_id))  
        #print self.conn.getresponse().read()
        res = self.conn.getresponse()
        if res.status == 200:
            self._channel_id=None

    def post_notification_source(self,bind_id,trigger_source,trigger_id):
        ddict = {'bind':
                    {'bind_id':bind_id,
                     'trigger_source':trigger_source,
                     'trigger_id':trigger_id}}
        self.conn.request('post', '/channels/%s/data/binds'%str(self._channel_id),json.dumps(ddict) )  
        res = self.conn.getresponse()
        res.read()
        #print res.status
    
    def delete_notification_source(self,bind_id):
        self.conn.request('delete', '/channels/%s/data/binds/%s'%(str(self._channel_id),bind_id))  
        res = self.conn.getresponse()
        print res.read()
        print res.status
            




"""    
def LLR(ip,port,uri):
    from websocket import create_connection
    from urlparse import urlunparse
    url = urlunparse(('ws',':'.join((ip,str(port))),uri,None,None,None))
    print url
    ws = create_connection(url)
    print "Reeiving..."
    result =  ws.recv()
    print "Received '%s'" % result
    ws.close()
    

def long_polling_request():
    from websocket import create_connection
    ws = create_connection("ws://localhost:8080/notification/channels/2/data")
    #print "Sending 'Hello, World'..."
    #ws.send("Hello, World")
    #print "Sent"
    print "Reeiving..."
    result =  ws.recv()
    print "Received '%s'" % result
    ws.close()
    

"""

if __name__ == '__main__':
    #LLR('127.0.0.1',8080,'/channels/1/data')
    #while True:
    #    long_polling_request()
    import time
    nc=Notification_Client('http://10.135.34.246:8090/')
    nc.create_channel(2)
    nc.post_notification_source(1,'10.137.131.82',"1.3.6.1.4.1.2011.5.25.191.3.1")
    
    count = 0
    while (1):    
        nc.LLR()
        #print nc._Channel_Data
        count += 1
        if count > 300:
            break
        
    nc.delete_notification_source(1)    
    
    nc.close_channel(2)