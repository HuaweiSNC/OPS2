# -*- coding: utf-8 -*- 
import telnetlib

class Process_Rest_Api(object):                
    def __init__(self,ip,port=23,username="root123",password="Root@123"):
        self.host = ip
        self.username = username
        self.password = password
        self.finishUserView = '>'      # 命令提示符，标识上一条命令已执行完毕
        self.finishSysView = ']'      # 命令提示符，标识上一条命令已执行完毕
        #connect    
        #print self.host,self.username,self.password
        try:
            self.tn = telnetlib.Telnet(self.host)   
        except Exception as e:
            print 'error:',e
            self.status = False
            self.errorinfo = e
            return
        
        print 'wait username'
        # 输入登录用户名
        self.tn.read_until('Username:')
        self.tn.write(self.username + '\r\n')  
        
        print 'wait password'
        # 输入登录密码
        self.tn.read_until('Password:') 
        self.tn.write(self.password + '\r\n')
        
        self.tn.read_until(self.finishUserView)
        print 'connect %s successful'%self.host
        self.status = True
        self.tn.write('system-view\r\n')
        self.tn.read_until(self.finishSysView)
        print 'Enter system-view'
        #return self.tn        
    def __exit__(self):
        self.tn.close()
        pass
    
    def get_rest_api_handle(self, dInputBody, schemapath):        
        #组装命令
        print 'input url:',schemapath
        cmd_elems = schemapath.split('/')
        del cmd_elems[0]
        cmdstring = "display"
        for elem in cmd_elems:
            if elem.find('?') != -1:
                tempelem = elem.replace('%2F','/')                
                temp = tempelem.split('?')              
                elem = temp[0]+' '+temp[1]           
            cmdstring = cmdstring + ' ' + elem      
        print 'Command:',cmdstring   
        self.tn.write(cmdstring + '\r\n')         
        retval = self.tn.read_until('[')
        disresult = retval.strip('[')
        #print disresult           
        return disresult

if __name__ == '__main__':
    '''
    telnetcon = TelnetConDevice("10.137.210.122","root123","!QAZ2wsx#")
    telnetcon.connect()
    ret = execute_command(telnetcon, 'system', 'display snmp-agent sys-info')
    print ret
    '''
    classObj=Process_Rest_Api("10.137.210.122","netconf","!QAZ2wsx#")
    dataObj = classObj.get_rest_api_handle("", "snmp-agent/sys-info")
    classObj.__exit__()
    del classObj
    print dataObj
    

  