��Ŀ������ļ����ļ�˵��(�������ӹ����У��������update���ļ�)��

Bottle_WebFrame.py
    web��ܣ��ṩ��http server������ת��http requeset -> netconf request���·���netconf manager�ࡣ���ҽ���netconf manager����xml���ĺ󣬸���http request�д������ݸ�ʽԼ����������Ӧ�����ݸ�ʽ���ݸ�http client��
    
manager/trap/Channel_Oper.py
    �ͻ��˺�Serverʹ��WebSocketͨ��ʱ��һ��ͨ��������ӡ�ɾ��ͨ��ʹ��
    
ciper_mgmt.py
    �豸�������Ĵ洢����   
    
config.py
    ������һЩnetconfЭ��ʵ�ֵĺ��ȫ�����ݣ�����Bottle���ʹ�õ�һЩȫ��������Ϣ��    
    
config_check.py
   �ж�������������������Ƿ���ȷ

dao/device_mgmt.py
    �豸����ģ�飬���岢ʵ�����豸�����࣬������ɾ�顣��ǰ��װ�˼����򵥵Ĺ���ӿڣ���������ʹ�á�

dao/driver_mgmt.py
    ��������ģ�飬���岢ʵ�������������࣬������ɾ�顣
    
dao/sqlrow_proxy.py

dao/userroles_mgmt.py

dao/users_mgmt.py

dao/whitelist_mgmt.py

ncclient 
   ncclient-0.3.2-py2.7.egg����������޸�

HTTPC_httplib.py
    HTTP�ͻ��˳������ڹ��췢�ͱ��ģ���ǰ�����͸澯����־ʱʹ��   
    
isdklib.py
    netconfЭ���ڲ�ʵ�֡�������
        Restful API -> rpc���Ľӿ�;
        netconf client�·�rpc���ĵ�netconf manager��������rpc-reply���Ľӿ�;
        rpc-reply����תRestful API�ӿ�     
        
network_mgmt.py
networkdevice_mgmt.py
FlexPoclicySocket.py
doc_oper.py
connect_mgmt.py
plugin/auth_backend.py

generalDriver.py
    netconfЭ��ģ��,ʵ����:
        1.netconf client��manager�����ӿڣ�
        2.http get/put/post/delete��method��Ӧ��netconf�������ϡ�

rest_adapter.py 
    Restʵ�ֽӿ��࣬�����豸ʱʹ��

notification.py:
    ����ר�ź�Clientʹ��WebSocket���͸澯��server�����Ե�����������ǰ�ⲿ����Bottle��Ҳ�У����Ժ������ķ�����ͬһ��Server��
    
notification_client.py:   
    Notification�ͻ��˲��Գ��򣬲��õ���ѯ����
    
schema.py:

selflearn.py:

snmp_traprcv.py
   �������ո澯�ĳ����յ��澯�����͵�Notification Server
   
syslog_logrcv.py   
   ����������־�ĳ����յ��澯�����͵�Notification Server 
   
telnet_client.py
   ʹ��telnet���ӣ�ͨ�������к��豸ͨ��
   
xml2xpath
    �ṩxmlToxpathת���ӿ�   
    
xmlTojson
    �ṩ��xmlTojson��ת���ӿڡ�


