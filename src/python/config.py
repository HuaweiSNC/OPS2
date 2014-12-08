##----------------------------------------------------------------------------------------------------------------------
##-- Copyright (C) Huawei Technologies Co., Ltd. 2008-2011. All rights reserved.
##----------------------------------------------------------------------------------------------------------------------
##----------------------------------------------------------------------------------------------------------------------
##--Project Code    : VRPV8
##--File name       : config.py
##--Author          :
##--Description     : File consist of user defined macro's
##----------------------------------------------------------------------------------------------------------------------
##--History:
##--Date                 Author                 Modification
##--04-03-2013             Ganesh                 created file.
##----------------------------------------------------------------------------------------------------------------------

import logging
import os
import logging.handlers  


##open file for logging
slogFile = os.path.join(os.getcwd(), 'LOGS', 'REST-RPC_Debug.log')
slogAlllogFile = os.path.join(os.getcwd(), 'LOGS', 'Alllog.log')
#print slogFile
if True != os.path.isdir(os.path.join(os.getcwd(), 'LOGS')):
    os.mkdir(os.path.join(os.getcwd(), 'LOGS'))

# create logger with "ops"  
logger = logging.getLogger('ops')
logger.setLevel(logging.INFO)  

loggerall = logging.getLogger(None)
loggerall.setLevel(logging.DEBUG)  

# create file handler which logs even debug messages  
size = 20*1024*1024
fileMaxCount = 100
fh = logging.handlers.RotatingFileHandler(slogFile, maxBytes=size, backupCount=fileMaxCount)  
fh.setLevel(logging.INFO)  

logall = logging.handlers.RotatingFileHandler(slogAlllogFile, maxBytes=size, backupCount=fileMaxCount)  
logall.setLevel(logging.INFO)  

# create console handler with a higher log level  
ch = logging.StreamHandler()  
ch.setLevel(logging.INFO)  

# create formatter and add it to the handlers  
formatter = logging.Formatter("%(asctime)s [%(name)s][%(levelname)s] %(message)s")  
fh.setFormatter(formatter)  
ch.setFormatter(formatter) 
logall.setFormatter(formatter) 

# add the handlers to the logger  
logger.addHandler(fh)  
logger.addHandler(ch)  
loggerall.addHandler(logall) 

DBPath=os.getcwdu()
dbFile=DBPath+'\OPS2.db'

def setOpsLoggingLevel(loglevel):
    logger.setLevel(loglevel)
    ch.setLevel(loglevel)
    fh.setLevel(loglevel)  
    logall.setLevel(loglevel)

## return values
ISDK_OK = 0
ISDK_ERROR = 1

## true false
ISDK_TRUE = 1
ISDK_FALSE = 0

#### Argument check
##LIST_TOOL_ARG = 3
##LIST_TOOL_ARG_WITH_OPTION = 4

#input body type
ISDK_JSON_IP_BODY = 'json_array'
ISDK_XML_IP_BODY = 'xml_input'


## schema version
SCHEMAVERSION = 'V8R5'

## OPS version
OPSVERSION = 'OPS2.0 V100R001C00B004'

'''DLOGLEVEL = {
             'DEBUG':logging.DEBUG,
             'INFO':logging.INFO,
             'WARNING':logging.WARNING,
             'WARN':logging.WARNING,
             'ERROR':logging.ERROR,
             'CRITICAL':logging.CRITICAL,
             'FATAL':logging.CRITICAL
             }'''
DLOGLEVEL = {
             'DEBUG':logging.DEBUG,
             'INFO':logging.INFO,
             'WARNING':logging.WARNING,
             'WARN':logging.WARNING,
             'ERROR':logging.ERROR,
             'CRITICAL':logging.CRITICAL,
             'FATAL':logging.CRITICAL
             }

## Argument check
DUSER_ARGS_NUM = {
'BOTTLE_ARG' : 1,
'BOTTLE_ARG_WITH_OPTION_SERVER' : 5,
#'BOTTLE_ARG_WITH_OPTION_TRAP' : 4,
#'BOTTLE_ARG_WITH_OPTION_SERVERANDTRAP' : 8,
'BOTTLE_ARG_WITH_OPTION_LOGLEVEL' : 3,
'BOTTLE_ARG_WITH_OPTION_SERVERANDLOGLEVEL' : 7,
'BOTTLE_ARG_WITH_OPTION_SERVERCERTFILE' : 9,
'BOTTLE_ARG_WITH_OPTION_AUTHBASE' : 11,
'BOTTLE_ARG_WITH_OPTION_WHITELIST' : 13,
'BOTTLE_ARG_WITH_OPTION_CHANNELNUM' : 15,
'BOTTLE_ARG_WITH_OPTION_CHECKESN' : 17,
#'BOTTLE_ARG_WITH_OPTION_TRAPANDLOGLEVEL' : 6,
#'BOTTLE_ARG_WITH_OPTION_SERVERANDLOGLEVELANGTRAP' : 10
}
 
IP_OPTION = '-serverip'
PORT_OPTION = '-port'
ENABLETRAP_OPTION = '-enabletrap'
TRAPPORT_OPTION = '-port'
LOGLEVEL_OPTION = '-loglevel'
CERTFILE_OPTION = '-certfile'
AUTHBASIC_OPTION = '-auth'
WHITELIST_OPTION = '-whitelist'
CHANNEL_OPTION ='-channelnum'
CHECKESN_OPTION = '-checkesn'

## User input parameters
DUSER_INPUT = {
    'serverip_option' : '',
    'input_serverip' : '',
    'port_option' : '',
    'input_port' : '',
    'auth_basic' : False,
    'white_list' : False,
    'channel_num' : '',
    'enabletrap_option':'',
    'trapport_option':'',
    'input_trapport':'163',
    '-loglevel': '',
    'input_loglevle':logging.INFO,
    'cert_file':'',
    'check_esn': False
}

## netocnf.py file open Flag
IS_NETCONF_PY_OPEN_FIRST_TIME = False

#### User input parameters
##DUSER_INPUT = {
##    'tool_option' : '',
##    'input_path' : '',
##    'output_path' : '',
##    'xml_file_path' : ''
##}

## REST api operation
POST = 'POST'
PUT = 'PUT'
DELETE = 'DELETE'
GET = 'GET'

#azam
ACTION = 'ACTION' 
GETCONFIG = 'GETCONFIG' 
COPYCONFIG = 'COPYCONFIG' 
DELETECONFIG = 'DELETECONFIG'
KILLSESSION = 'KILLSESSION'

## HTTP response status code
HTTP_OK = 200
HTTP_NO_CONTENT = 204
HTTP_CREATED = 201
HTTP_NOT_IMPLEMENTED = 501



## xml node type
DM_DATA_MODEL_FILE_ELEMENT = '{http://www.huawei.com/netconf/vrp}data-model-file'

DM_TABLE_INSTANCE_ELEMENT = '{http://www.huawei.com/netconf/vrp}table-instance-element'
DM_TABLE_CONTAINER_ELEMENT = '{http://www.huawei.com/netconf/vrp}table-container-element'

DM_CFG_DATA_ELEMENTS_ELEMENT = '{http://www.huawei.com/netconf/vrp}cfg-data-elements'
DM_CFG_DATA_ELEMENT_ELEMENT = '{http://www.huawei.com/netconf/vrp}cfg-data-element'

DM_SERVICE_ELEMENT = '{http://www.huawei.com/netconf/vrp}service-element'
DM_SUB_SERVICE_ELEMENT = '{http://www.huawei.com/netconf/vrp}sub-service-element'

DM_QUERY_INSTANCE_ELEMENT = '{http://www.huawei.com/netconf/vrp}query-instance-element'


## namespace
BASE_CAP_NAMESPACE = 'urn:ietf:params:xml:ns:netconf:base:1.0'
NETCONF_NAMESPACE = 'http://www.huawei.com/netconf/vrp'

# schema version
CONTENT_VERSION = '1.0'
FORMAT_VERSION = '1.0'

## error code
ISDK_BASE_ERROR_CODE = 80
ISDK_FILE_TYPE_NOT_OPER = ISDK_BASE_ERROR_CODE + 1

## Edit-config operation
EDIT_CONFIG_CREATE_OPERATION = 'create'
EDIT_CONFIG_MERGE_OPERATION = 'merge'
EDIT_CONFIG_DELETE_OPERATION = 'delete'

#### Basic datatype
##DBASIC_DATATYPE = {
##    '1' : 'CHAR',
##    '2' : 'UCHAR',
##    '3' : 'SHORT',
##    '4' : 'USHORT',
##    '5' : 'INT32',   
##    '6' : 'UINT32',
##    '7' : 'INT64',
##    '8' : 'UINT64',
##    '9' : 'COUNTER32',
##    '10' : 'COUNTER64',
##    '11' : 'GAUGE32',
##    '12' : 'GAUGE64',
##    '13' : 'BOOL',
##    '14' : 'HEX',
##    '15' : 'DATE',
##    '16' : 'TIME',
##    '17' : 'DATETIME',
##    '18' : 'DATETIME',
##    '19' : 'TIMETICK',
##    '20' : 'MAC',
##    '21' : 'IPV4',
##    '22' : 'IPV6',  
##    '23' : 'IPV4_PRE',  
##    '24' : 'IPV6_PRE',  
##    '25' : 'STRING',  
##    '26' : 'BLOCK',  
##    '27' : 'OID',  
##    '28' : 'DATA',  
##    '29' : 'ENUM',  
##    '30' : 'ACCESSTYPE',  
##    '31' : 'LRID',  
##    '32' : 'VRID',  
##    '33' : 'PASSWORD',  
##    '38' : 'IPV4IPV6'
##}
##
##
### rest api class template
##REST_API_CLASS_TEMPLATE = '\n \
##class $txpath : \n \
##{\n \
##    \n \
##    def POST_$txpath(json_obj_$tpath, schemapath): \n \
##        srpcstring = $isdklib.isdk_convert_restapi2rpc(json_obj_$tpath, schemapath, \'POST\') \n \
##        srpcreplystring = $isdklib.isdk_sendrecv_nccclient(srpcstring) \n \
##        iret = $isdklib.isdk_convert_rpc2restapi(srpcreplystring) \n \
##        return json_obj_$tpath \n \
##    \n \
##    def PUT_$txpath(json_obj_$tpath): \n \
##        return json_obj_$tpath \n \
##    \n \
##    def GET_$txpath(url_$tpath): \n \
##        return json_obj_$tpath \n \
##    \n \
##    def DELETE_$txpath(url_$tpath); \n \
##        return json_str_$tpath \n \
##    \n \
##    \n \
##    url_$tpath = $tjsonurl \n \
##    json_str_$tpath = $tjsonstr \n \
##    json_obj_$tpath = $tjsonobj \n \
##    \n\
##}\n \
##\n' 
