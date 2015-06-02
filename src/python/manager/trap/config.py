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
slogFile = os.path.join(os.getcwd(), 'LOGS', 'TrapService.log')
#print slogFile
if True != os.path.isdir(os.path.join(os.getcwd(), 'LOGS')):
    os.mkdir(os.path.join(os.getcwd(), 'LOGS'))

# create logger with "ops"  
logger = logging.getLogger('trap')
logger.setLevel(logging.INFO)  

loggerall = logging.getLogger(None)
loggerall.setLevel(logging.DEBUG)  

# create file handler which logs even debug messages  
size = 20*1024*1024
fileMaxCount = 100
fh = logging.handlers.RotatingFileHandler(slogFile, maxBytes=size, backupCount=fileMaxCount)  
fh.setLevel(logging.INFO)   

# create console handler with a higher log level  
ch = logging.StreamHandler()  
ch.setLevel(logging.INFO)  

# create formatter and add it to the handlers  
formatter = logging.Formatter("%(asctime)s [%(name)s][%(levelname)s] %(message)s")  
fh.setFormatter(formatter)  
ch.setFormatter(formatter)  

# add the handlers to the logger  
logger.addHandler(fh)  
logger.addHandler(ch)   

DBPath=os.getcwdu()
dbFile='%s%sOPS2.db' % (DBPath, os.sep)

def setOpsLoggingLevel(loglevel):
    logger.setLevel(loglevel)
    ch.setLevel(loglevel)
    fh.setLevel(loglevel)   
    
    