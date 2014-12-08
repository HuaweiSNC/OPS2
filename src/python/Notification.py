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
    
g_channels=Channels()
#===============================================================================
# 
#===============================================================================
app = Bottle()
@app.route('/websocket')
def handle_websocket():   
    environ = request.environ
    wsock = environ.get('wsgi.websocket')
    if not wsock:
        abort(400, 'Expected WebSocket request.')
    
    wsock.send("Your message was: ")
    while False:
        try:
            message = wsock.receive()
            wsock.send("Your message was: %r" % message)
            sleep(3)
            wsock.send("Your message was: %r" % message)
        except WebSocketError:
            break

#add a new channel
@app.route('/channels/<channel_id>',method='POST')
def handle_channels_post(channel_id):
    
    ch=Channel(channel_id,request.url,request.url+'/data')
    #ch._id=channel_id
    #ch._url=request.url
    #ch._Data_URL=request.url+'/data'
    g_channels.add(ch)
    print 'create channel %s'%(channel_id)
    response.status = 202
    #return  'create channel 2' 

#delete a channel
@app.route('/channels/<channel_id>',method='DELETE')
def handle_channels_delete(channel_id):
    ch=g_channels.search(channel_id)
    if ch != None:
        g_channels.delete(channel_id)
        print 'delete channel %s'%(channel_id)
        response.status = 202
    else:
        response.status = 500
    
@app.route('/channels/<channel_id>/data',method='GET')
def handle_channel_get(channel_id):
    #just test 
    #handle_channels_post(channel_id)
    ch=g_channels.search(channel_id)
    print 'receive connect message from channel ',channel_id
    if ch!= None:
        environ = request.environ
        ch._wsock=environ.get('wsgi.websocket')
        try:
            message = ch._wsock.receive()
            print 'connect successful'   
        except WebSocketError:
            ch._wsock = None
            print "the client is closed"

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
            print "get and send data = ",data          
            try:
                ch._wsock.send(data)
            except WebSocketError:
                ch._wsock = None
                print "the client is closed"
                return            
    else:
        print 'channel %s is not exist'%channel_id
        response.status = 500
    
@app.route('/channels/<channel_id>/data/binds',method='POST')
def handle_queue_bindpost(channel_id):
    ch=g_channels.search(channel_id)
    print 'post data binds'
    if ch!= None:
        body = request.body
        data = body.read()
        ch._queue.put(data)
        
@app.route('/channels/<channel_id>/data/binds/<bind-id>',method='DELETE')
def handle_queue_binddelete(channel_id):
    ch=g_channels.search(channel_id)
    if ch!= None:
        body = request.body
        data = body.read()
        #ch._queue(data)        


def notificationServer_start(hostip, serverport, trapport):
    from gevent.pywsgi import WSGIServer
    from geventwebsocket import WebSocketHandler, WebSocketError
    
    server = WSGIServer((hostip, serverport), app,
                        handler_class=WebSocketHandler)
    disip = hostip
    if disip == '':
        disip = "localhost"
    print "access @ http://%s:%s/websocket.html" % (disip, serverport)
    
    trapnt = trapServer_start(hostip, trapport)
    return server, trapnt

def trapServer_start(hostip, trapport):             
    trapnt = startReceiveTrap(hostip, trapport)
    return trapnt    
    
if __name__ == '__main__':
    

    server,trapnt = notificationServer_start('', 9000, 163)
    
    try:
        server.serve_forever()
    except:
        print 'quit from bottle'        
        stopReceiveTrap(trapnt)    

