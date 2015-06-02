'''

@author: x00106601
'''
def ni(*args, **kwargs):
    raise NotImplementedError

class Process_Adapter(object): 
    
    def __init__(self, sshEngine):
        self.ssh = sshEngine
    
    #set sshEngine
    set_sshEngine = ni
    
    # process
    process = ni