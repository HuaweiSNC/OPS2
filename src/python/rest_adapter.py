'''

@author: x00106601
'''

def ni(*args, **kwargs):
    raise NotImplementedError

class Rest_Adapter(object): 
    
    def __init__(self,ip,port=22,username="root123",password="Root@123"):
        pass
    
    """Base Rest_Adapter class - to be subclassed by real Rest_Adapter."""
    getStatus = ni
    close = ni
    reconnect = ni
    post_rest_api_handle = ni
    put_rest_api_handle = ni
    delete_rest_api_handle = ni
    get_rest_api_handle = ni
    set_main_device = ni
    get_esn = ni
    set_multi_ipaddress = ni
    
        