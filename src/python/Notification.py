'''
Created on 2013-3-9

@author: Administrator
'''

from bottle import  request, abort, Bottle, response
from gevent import monkey; monkey.patch_all()
from time import sleep
from geventwebsocket import WebSocketError
from manager.trap.channel_oper import Channel,Channels
from manager.trap.snmp_traprcv import startReceiveTrap,stopReceiveTrap

from manager.trap.snmp_traprcv import TrapRules
import threading
import sys
import manager.trap.config
import logging 
logger = logging.getLogger("trap.web") 

g_channels=Channels()
g_mutex = threading.Lock()
g_index=0
#===============================================================================
# 
#===============================================================================
app = Bottle()

@app.route('/trap/websocket')
def handle_websocket():
    environ = request.environ
    wsock = environ.get('wsgi.websocket')
    myTrapRule = TrapRules('','')
    revice_websocket(wsock, request.url, myTrapRule)
    return

def revice_websocket(wsock, url, myTrapRule):
    if not wsock:
        abort(400, 'Expected WebSocket request.')

    myindexid = 0
    global g_index
    with g_mutex:
        g_index=g_index+1
        myindexid = g_index
        ch=Channel(myindexid, url, wsock, myTrapRule)
        g_channels.add(ch)
        
        logger.info( 'create channel %s for client %s' % (g_index, request.remote_addr)) 
    
    wsock.send("hello")
    while True:
        try:
            msg = wsock.receive()
            if msg is not None:
                logger.info('from client %s, receive trap msg equal %s ' % (myindexid, msg))
        except WebSocketError:
            ch._wsock = None
            logger.info('the client id = %s is closed' % myindexid)
            
    with g_mutex:
        g_channels.remove(ch)

@app.route('/trap/agent/<agent_ipaddress>')
def handle_websocket_byagentid(agent_ipaddress):
    environ = request.environ
    wsock = environ.get('wsgi.websocket')
    myTrapRule = TrapRules(agent_ipaddress,'')
    revice_websocket(wsock, request.url, myTrapRule)
    return

@app.route('/trap/oid/<trap_oid>')
def handle_websocket_bytrapoid(trap_oid):
    environ = request.environ
    wsock = environ.get('wsgi.websocket')
    myTrapRule = TrapRules('', trap_oid)
    revice_websocket(wsock, request.url, myTrapRule)
    return

@app.route('/trap/agent/<agent_ipaddress>/oid/<trap_oid>')
def handle_websocket_agent_oid(agent_ipaddress, trap_oid):
    environ = request.environ
    wsock = environ.get('wsgi.websocket')
    myTrapRule = TrapRules(agent_ipaddress, trap_oid)
    revice_websocket(wsock, request.url, myTrapRule)
    return

#send data to client
@app.route('/channels/<channel_id>/data',method='POST')
def handle_queue_post(channel_id):
    ch=g_channels.search(channel_id)
    if ch!= None:
        body = request.body
        data = body.read()
        print 'received data:',data
        ch._queue.put(data)
        if ch._wsock:
            data = ch._queue.get()
            logger.debug("get and send data = %s " % data)          
            try:
                ch._wsock.send(data)
            except WebSocketError:
                ch._wsock = None
                logger.error( "the client is closed")
                return            
    else:
        print 'channel %s is not exist'%channel_id
        response.status = 500
    


def notificationServer_start(hostip, serverport, trapport):
    from gevent.pywsgi import WSGIServer
    from geventwebsocket import WebSocketHandler, WebSocketError
    
    server = WSGIServer((hostip, int(serverport)), app,
                        handler_class=WebSocketHandler)
    disip = hostip
    if disip == '':
        disip = "localhost"
    
    print """Huawei Trap Server v1.01 server starting up ...
    Listening on %s://%s:%s/trap/websocket
    Hit Ctrl-C to quit."""%('http',disip,serverport)
    logger.info("access @ http://%s:%s/trap/websocket" % (disip, serverport))
    trapnt = trapServer_start(hostip, trapport)
    return server, trapnt

def trapServer_start(hostip, trapport):     
    trapnt = startReceiveTrap(hostip, trapport, g_channels)
    return trapnt    

def parse_arg():  
    lenofArgs = len(sys.argv)
    counti = 1
 
    trapPort='163'
    webport='9000'
    while counti < lenofArgs:
        argname = sys.argv[counti]
        if counti + 1 > lenofArgs :
            logger.info("Invalid command line option. Expected: '%s'" % argname)
            return 1
        argvalue = sys.argv[counti + 1]
        counti = counti + 2
        if argname == "-trapport":
            trapPort = argvalue
        if argname == "-webport":
            webport = argvalue
            
    return webport,trapPort

if __name__ == '__main__':
    webport, trapPort = parse_arg()
    server,trapnt = notificationServer_start('', webport, trapPort)
    try:
        server.serve_forever()
    except:
        logger.info( 'quit from Trap Server' )       
        stopReceiveTrap(trapnt)    

