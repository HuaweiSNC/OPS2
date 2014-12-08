# -*- coding: utf-8 -*-
'''
Created on 2013-2-28

@author: m00147039
'''
# -*- coding: utf-8 -*-
'''
Created on 2013-2-27

@author: m00147039

http client : select urllib2 
 why:
   httplib is the basic lib 
   urllib is simular with urllib2
   urlib2 has the authonization and authentication
   
   
In this project ,http header should has below 
 Accept
 Authorization
 Content-type
 Host,(this is automate .we can change it )
 x-date
 
 
'''
import httplib

import time
import base64

import json

def usage():
    print """
    HTTPClient: 
    
        suport json data and xml data imput
        return data is base on accept
    
    
    It supports belowing headers:
       accept, Authorization,Content-type ,host and x-date
    default :
       accept :application/json
       content-type:application/json
       host: in url,also we can change
       x-date: submit time
       authorization: None
    
    Example:
     hc=HTTPClient('username','passwd')
     hc._put('127.0.0.1',8080,{'key1':'value1','key2':'value2'})
     
     jsondata={"key2":"values"}
     hc.put('127.0.0.1',8080,jsondata)
     
     xml='''<key2>value2</key2>
         
         '''
     hc.putx('127.0.0.1',8080,xml})
     
     
     hc.close()
    """
    
#===============================================================================
# Error code
#===============================================================================
DATA_NOT_VALID=600
status={
600: 'Data is not valid ',

}





def dict2xml(top,dictdata):
    pass
    #from xmltools import WriteToXMLString
    #whole=WriteToXMLString(dictdata, top)
    #return whole  
def xml2dict(xml_text):
    pass
    #from xmltools import ReadFromXMLString,XML_STRICT_HDR,XML_LOAD_EVAL_CONTENT
    #options=XML_STRICT_HDR | XML_LOAD_EVAL_CONTENT
    #d = ReadFromXMLString(xml_text,options=options)   
    #return d

class httpclient():
    def __init__(self,usrname=None,password=None):
        
        
        #=======================================================================
        # Default 
        #=======================================================================
        self._headers={}
        self._base64string=None
        self._host=None
        self._content='application/json'
        self._accept='application/json'
        self._xdate=True
        self._body=None
        
        if usrname!=None and password!=None:
            self._base64string = base64.encodestring('%s:%s' % (usrname, password)).replace('\n', '')
            
    def set_auth(self,username,password):
        self._base64string = base64.encodestring('%s:%s' % (username, password)).replace('\n', '')
    def set_host(self,ip,port=None):
        self._host=str(ip)+':'+str(port)
    def set_content(self,content):
        self._content=content
    def set_accept(self,accept):
        self._accept=accept    
    def set_xdate(self,boolean):
        self._xdate= boolean
    def __exit__(self):
        self._conn.close()
    def close(self):
        self.__exit__()
    
    #===========================================================================
    # data is dict
    #===========================================================================
    def _post(self,url,data=None):
        return self._call('POST',url,data)
    def _put(self,url,data=None):
        return self._call('PUT',url,data)
    def _get(self,url,data=None):
        return self._call('GET',url,data)
    def _delete(self,url,data=None):
        return self._call('DELETE',url,data)
    #===========================================================================
    # data is json
    #===========================================================================
    def post(self,url,jdata=None):
        try:
            data=json.loads(jdata)
        except:
            return DATA_NOT_VALID
        return self._call('POST',url,data)
    def put(self,url,jdata=None):
        try:
            data=json.loads(jdata)
        except:
            return DATA_NOT_VALID
        return self._call('PUT',url,data)
    def get(self,url,jdata=None):
        try:
            if jdata !=None:
                data=json.loads(jdata)
            else:
                data=None
        except:
            return DATA_NOT_VALID
        return self._call('GET',url,data)
    def delete(self,url,jdata=None):
        try:
            data=json.loads(jdata)
        except:
            return DATA_NOT_VALID
        return self._call('DELETE',url,data)
    #===========================================================================
    # data is xml
    #===========================================================================
    def postx(self,url,xdata=None):
        try:
            data=xml2dict(xdata)
        except:
            return DATA_NOT_VALID
        return self._call('POST',url,data)
    def putx(self,url,xdata=None):
        try:
            data=xml2dict(xdata)
        except:
            return DATA_NOT_VALID
        return self._call('PUT',url,data)
    def getx(self,url,xdata=None):
        try:
            data=xml2dict(xdata)
        except:
            return DATA_NOT_VALID
        return self._call('GET',url,data)
    def deletex(self,url,xdata=None):
        try:
            data=xml2dict(xdata)
        except:
            return DATA_NOT_VALID
        return self._call('DELETE',url,data)
    
    def add_header(self,k,v):
        self._headers[k]=v
    def _call(self,method,url,body=None):
        #=======================================================================
        # Header
        #=======================================================================
        from urlparse import urlparse
        o = urlparse(url)
        
        self._conn = httplib.HTTPConnection(o.hostname,port=int(o.port))
        
        self.add_header('Accept', self._accept)
        self.add_header('Content-type', self._content)
        
        if self._xdate == True:
            localtime = time.asctime( time.localtime(time.time()) )
            self.add_header('X-date', localtime)
        
        if self._base64string !=None:
            self.add_header("Authorization", "Basic %s" % self._base64string)
        if self._host!=None: 
            self.add_header('Host', self._host)
        
        #=======================================================================
        # Body
        #=======================================================================
        
        
        if body !=None and isinstance(body,dict):
            self._body=body
        
        #=======================================================================
        # Method
        #=======================================================================
        #=======================================================================
        # Open...
        #=======================================================================
        
        #print '*'*40
        #print self._body
        try:
            self._conn.request(method,o.path,body=json.dumps(self._body),headers=self._headers)
        
            #self._conn.request(method,url,body=self._body,headers=self._headers)
            #=======================================================================
            # Result
            # default is json
            #=======================================================================
            response= self._conn.getresponse()
            
            if self._accept =='applicaton/xml' :
                return dict2xml(None,json.loads(response.read()))
            # Add more acception handler
            #
            #
            return response.status,response.read()
        except:
            return response.status,response.read(),response.reason    
        
import warnings
def depr(message):
    warnings.warn(message, DeprecationWarning, stacklevel=3)



#===============================================================================
# 
#===============================================================================

def test_post():
    hc=httpclient()
    hc.set_host('10.137.130.219',8080)
    hc.set_auth('root', 'Root@123')
    

    jsondata={'user':{'userName':'maohongsen',
              'userGroupName':'manage-ug',
              'serviceFtp':'true',
              'password':'Mab12cd',
              'userLevel':1,
              'serviceTerminal':'true',
              'maxAccessNum':None
              }
              }
    print json.dumps(jsondata)
    print hc._post('http://10.135.32.108:8080/devices/1/netconf_api/datastores/running/aaa/lam/users',jsondata)
    
def test_delete():
    hc=httpclient()
    print hc._delete('http://10.135.32.108:8080/devices/1/netconf_api/datastores/running/aaa/lam/users/maohongsen')
def test_put():
    hc=httpclient()
    jsondata={
              'userLevel':3,
              }
    print hc._put('http://10.135.32.108:8080/devices/1/netconf_api/datastores/running/aaa/lam/users/sun',jsondata)
def test_get_interface():
    hc=httpclient()
    print hc.get('http://10.135.32.108:8080/devices/1/netconf_api/modules/ethernet/ethernetIfs/Ethernet1%2f0%2f0')
def test_action():
    hc=httpclient()
    jsondata={'ftpcTransferFile':{
              'commandType':'put',
              'userName':'root',
              'password':'root',
              'localFileName':'cfcard:/a.cfg',
              'remoteFileName':'/a.py' ,
              'serverIpv4Address':' 10.135.32.108'     ##Notice before 10 has one space to escape this situation '10.135.32.108'
              }
              }
    
    print hc._post('http://10.135.32.108:8080/devices/1/netconf_api/operations/ftpc/ftpcTransferFiles',jsondata)

def test_post2():
    hc=httpclient()
    jsondata={'user':{'userName':'maohongsen',
              'userGroupName':'manage-ug',
              'serviceFtp':'true',
              'password':'Mab12cd',
              'userLevel':1,
              'serviceTerminal':'true',
              'maxAccessNum':None
              }
              }
    print json.dumps(jsondata)
    print hc._post('http://10.135.32.108:8080/channels/2/data',jsondata)

if __name__=='__main__':
    #test_action()
    #test_get_interface()
    test_post2()
    #test_delete()
    #test_put()
    