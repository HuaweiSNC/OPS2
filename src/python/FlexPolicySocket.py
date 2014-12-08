#!/usr/bin/python
#coding=UTF-8
import socket
from threading import Thread 

 
_policyFile = '<?xml version="1.0" encoding="UTF-8"?><cross-domain-policy xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://www.adobe.com/xml/schemas/PolicyFileSocket.xsd"><allow-access-from domain="*" to-ports="*" secure="false" /><allow-http-request-headers-from domain="*" headers="AnotherHeader,X-MyPrefix-*"/><site-control permitted-cross-domain-policies="master-only" /></cross-domain-policy>'
def printd( aString ):
    # if debug:
    print aString
  
class FlexPolicySocket():
    def process(self):
        _connector = None
        _running = True
        _host = ''
        _port = '843'
        _maxClient = 999
        #debug = True

        _connector = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
        _connector.bind ( ( str(_host), int(_port) ) )
        _connector.listen ( int(_maxClient) )
        _running = True
        while _running:
            printd('Running on port ' + _port + ' for flex policy ... ')
            clientSock, details = _connector.accept()
            if _running:
                printd( 'New connection with: ' + str(details) )
                clientSock.setblocking( True )
                recvData = clientSock.recv(2000)
                if("policy-file-request" in recvData):
                    clientSock.send(_policyFile)
                printd( 'host: ' + str(details[0]) )
                printd( 'port: ' + str(details[1]) )
                printd( 'recvData:' + recvData )
                clientSock.close()
                
    def threadstart(self): 
        t = Thread(target = self.process,  args = ())
        t.daemon = True
        t.start()

if __name__ == '__main__':
    try:
        policySocket = FlexPolicySocket()
        policySocket.process() 
    except:
        print 'quit from FlexPolicySocket'
    