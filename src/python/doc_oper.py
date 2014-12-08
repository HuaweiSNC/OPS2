import os

def GetDocContent(filepath,size=0):
    if os.path.isfile(filepath) == 0:
        print "the file %s does not exist"%filepath
        return
            
    file = open(filepath, "rb");
    if file == None:
        print "open file %s failed"%filepath       
    content=file.read()    
 
    #print "get file content OK"
    file.close()
    #print content    
    return  content

def GetHelpDoc(path):
    if path == 'doc':
        content = '<files>'
        for filename in os.listdir(r'OPEN_DAYLIGHT'):        
            content = content + '\n' + '    <file>' + filename + '</file>' 
        content = content + '\n' + '</files>'        
        return content
    
    fileinfo = path.split('/')  
    if len(fileinfo) != 2 or fileinfo[0]!='doc':
        print 'wrong url'
        return
    
    filepath="OPEN_DAYLIGHT/"+fileinfo[1]  
    #print "open file: %s"%filepath    
    content = GetDocContent(filepath)
    return content

def GetLogDoc():
    filepath="LOGS/REST-RPC_Debug.log"  
    #print "open file: %s"%filepath    
    content = GetDocContent(filepath,100000)  
    return  content 
    