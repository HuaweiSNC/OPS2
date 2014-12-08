import sys
import config

 
def check_arg():  
    lenofArgs = len(sys.argv)
    match = 0
    for i in config.DUSER_ARGS_NUM:    
        if lenofArgs == config.DUSER_ARGS_NUM[i]:            
            match = 1
      
    if match != 1:
        print("Error: Command has invalid number of arguments")
        print("Expected command is 'python Bottle_WebFrame.py [ -serverip <ipaddr> -port <portnum> ] [ -loglevel <level> ] [ -certfile <certfile> ] [ -auth <true|false> ] [ -whitelist <true|false>] [-channelnum <number>] [-checkesn <true|false>]'")
        sys.exit(1) 
    
    counti = 1
    while counti < lenofArgs:
        argname = sys.argv[counti]
        if counti + 1 > lenofArgs :
            print("Invalid command line option. Expected: '%s'", argname)
            return 1
        
        argvalue = sys.argv[counti + 1]
        counti = counti + 2
        
        # parse log level
        if argname == config.LOGLEVEL_OPTION:
            if argvalue not in config.DLOGLEVEL:
                print 'Error: the level is not supported. Supported level:DEBUG,INFO,WARNING,ERROR,CRITICAL'
                return 1
            else:
                level = config.DLOGLEVEL[argvalue]
                config.DUSER_INPUT['input_loglevle'] = level 
                
        # parse ip option
        if argname == config.IP_OPTION: 
            config.DUSER_INPUT['input_serverip'] = argvalue
    
        # parse port option
        if argname == config.PORT_OPTION:
            config.DUSER_INPUT['input_port'] = argvalue
          
        # parse cert file 
        if argname == config.CERTFILE_OPTION:
            config.DUSER_INPUT['cert_file'] = argvalue
            
        if argname == config.CHANNEL_OPTION:
            config.DUSER_INPUT['channel_num'] = argvalue
            
        # enable auth 
        if argname == config.AUTHBASIC_OPTION:
            if argvalue.lower() == 'true' : 
                config.DUSER_INPUT['auth_basic'] = True
            else:
                config.DUSER_INPUT['auth_basic'] = False 
               
        # enable auth 
        if argname == config.WHITELIST_OPTION:
            if argvalue.lower() == 'true' : 
                config.DUSER_INPUT['white_list'] = True
            else:
                config.DUSER_INPUT['white_list'] = False 
                
        # enable checkesn
        if argname == config.CHECKESN_OPTION:
            if argvalue.lower() == 'true' : 
                config.DUSER_INPUT['check_esn'] = True
            else:
                config.DUSER_INPUT['check_esn'] = False         
    return 0
