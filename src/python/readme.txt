项目中主体的几个文件说明(功能增加过程中，不断添加update该文件)：

Bottle_WebFrame.py
    web框架，提供了http server能力。转换http requeset -> netconf request，下发到netconf manager侧。并且接收netconf manager返回xml报文后，根据http request中带的数据格式约束，返回相应的数据格式数据给http client。
    
manager/trap/Channel_Oper.py
    客户端和Server使用WebSocket通信时的一个通道管理，添加、删除通道使用
    
ciper_mgmt.py
    设备密码密文存储管理   
    
config.py
    定义了一些netconf协议实现的宏和全局数据（包括Bottle框架使用的一些全局配置信息）    
    
config_check.py
   判断命令行输入参数内容是否正确

dao/device_mgmt.py
    设备管理模块，定义并实现了设备管理类，包括增删查。当前封装了几个简单的管理接口，方便外面使用。

dao/driver_mgmt.py
    驱动管理模块，定义并实现了驱动管理类，包括增删查。
    
dao/sqlrow_proxy.py

dao/userroles_mgmt.py

dao/users_mgmt.py

dao/whitelist_mgmt.py

ncclient 
   ncclient-0.3.2-py2.7.egg第三方插件修改

HTTPC_httplib.py
    HTTP客户端程序，用于构造发送报文，当前在推送告警、日志时使用   
    
isdklib.py
    netconf协议内部实现。包括：
        Restful API -> rpc报文接口;
        netconf client下发rpc报文到netconf manager，并返回rpc-reply报文接口;
        rpc-reply报文转Restful API接口     
        
network_mgmt.py
networkdevice_mgmt.py
FlexPoclicySocket.py
doc_oper.py
connect_mgmt.py
plugin/auth_backend.py

generalDriver.py
    netconf协议模块,实现了:
        1.netconf client与manager建连接口；
        2.http get/put/post/delete等method对应的netconf操作集合。

rest_adapter.py 
    Rest实现接口类，加载设备时使用

notification.py:
    用于专门和Client使用WebSocket推送告警的server，可以单独启动，当前这部分在Bottle中也有，可以和其他的服务在同一个Server上
    
notification_client.py:   
    Notification客户端测试程序，采用的轮询机制
    
schema.py:

selflearn.py:

snmp_traprcv.py
   用来接收告警的程序，收到告警并发送到Notification Server
   
syslog_logrcv.py   
   用来接收日志的程序，收到告警并发送到Notification Server 
   
telnet_client.py
   使用telnet连接，通过命令行和设备通信
   
xml2xpath
    提供xmlToxpath转换接口   
    
xmlTojson
    提供了xmlTojson的转换接口。


