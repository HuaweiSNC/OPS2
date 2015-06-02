#!/usr/bin/python
#coding=UTF-8
'''
Created on 2015年3月9日

@author: x00302603
'''
#!/usr/bin/python 
import paramiko
import config
import logging 

logger = logging.getLogger("ops.sshClient")  

##-------------------------------------------------------------------------------
##-- Class Name      : SSHClient
##-- Date Created    : 2015-3-24
##-- Author          : x00302603
##-- Description     : Class contains
##--                    a. Methods to open and close, reconect ssh session
##--                    b. Methods to execute bash on linux
##--                    c. Methods to upload file to linux
##--                    d. Methods to download file from linux
##-- Caution         :
##------------------------------------------------------------------------------
class SSHClient():
    def __init__(self,ip,port=22,username="root123",password="Root@123"):
        self.host = ip
        self.port = port
        self.username = username
        self.password = password  
        self.ssh = None
        
    def connect(self):
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh.connect(self.host, self.port, self.username, self.password, look_for_keys=False, allow_agent=False, key_filename=None)
        return self.ssh
        
    def reconnect(self):
        if (self.ssh != None):
            self.disconnect()
        self.connect()
        
    def disconnect(self):
        self.ssh.close()
      
    def exec_cmd(self, command):
        '''
                           执行linux的bash命令
        command  为命令行，一次要搪行多条命讼，可以用分号或&符号分隔，
        '''
        logger.info("host %s run bash: %s" % (self.host, command))
        stdin, stdout, stderr = self.ssh.exec_command(command)
        output = stdout.read()
        err = stderr.read()
        return output, err
      
    def upload(self, localpath, remotepath):
        '''
                           向linux服务器上传文件.
        localpath  为本地文件的绝对路径。如：D:\test.py
        remotepath 为服务器端存放上传文件的绝对路径,而不是一个目录。如：/tmp/my_file.txt
        '''
        client = paramiko.Transport((server_ip, server_port))
        client.connect(username = server_user, password = server_passwd)
        sftp = paramiko.SFTPClient.from_transport(client)
        
        sftp.put(localpath,remotepath)
        client.close()
      
    def downlaod(self, localpath, remotepath):
        '''
                           从linux服务器下载文件到本地
        localpath  为本地文件的绝对路径。如：D:\test.py
        remotepath 为服务器端存放上传文件的绝对路径,而不是一个目录。如：/tmp/my_file.txt
        '''
        client = paramiko.Transport((server_ip, server_port))
        client.connect(username = server_user, password = server_passwd)
        sftp = paramiko.SFTPClient.from_transport(client)
        
        sftp.get(remotepath, localpath)
        client.close()
        
        
    def getStatus(self):
        if (self.ssh != None):
            if (self.ssh.get_transport() == None):
                return False
            return self.ssh.get_transport().isAlive()
        return True
        
if __name__ == '__main__':
    print "server running..."
    server_ip = '10.110.139.189'
    server_user = 'root'
    server_passwd = 'passw0rd'
    server_port = 22
    
    sshclient = SSHClient(server_ip,server_port, server_user, server_passwd)
    sshclient.connect()
    
    sshclient.exec_cmd("dir")
    sshclient.exec_cmd("cd /home ; dir")
    sshclient.exec_cmd("ovs-vsctl show")
    sshclient.exec_cmd("dir")
    
    sshclient.downlaod("F:\\demo\\ops_install\\readme.txt", "/opt/ops/readme.txt")
    sshclient.upload("F:\\demo\\ops_install\\readme.txt", "/opt/ops/readme1.txt")
    sshclient.disconnect()
    
    