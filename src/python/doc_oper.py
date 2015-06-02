import os
import config
import logging 
logger = logging.getLogger("ops.docs")  

def GetDocContent(filepath,size=0):
    if os.path.isfile(filepath) == 0:
        logger.warning( "the file %s does not exist" % filepath)
        return
            
    file = open(filepath, "rb");
    if file == None:
        logger.info( "open file %s failed" % filepath )      
    content=file.read()    
 
    #print "get file content OK"
    file.close()
    #print content    
    return  content

def GetHelpDoc(path):
    if path == 'doc':
        content = '<files>'
        for filename in os.listdir(r'docs'):        
            content = content + '\n' + '    <file>' + filename + '</file>' 
        content = content + '\n' + '</files>'        
        return content
 
    filepath="docs/"+ path
    #print "open file: %s"%filepath    
    content = GetDocContent(filepath)
    return content

def GetLogDoc():
    filepath="LOGS/REST-RPC_Debug.log"  
    #print "open file: %s"%filepath    
    content = GetDocContent(filepath,100000)  
    return  content 
    