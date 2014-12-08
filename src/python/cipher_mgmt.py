from Crypto.Cipher import AES
import binascii
import os
from hashlib import sha256
from hmac import HMAC
import base64

key='0123456789abcdef0123456789abcdef'

def EncodePassword(passwd):        
    encryptor=AES.new(key)
    plain=passwd*16
    ciphertext = encryptor.encrypt(plain)  
    #print 'Encodeplain----',plain
    #print 'cipher---',ciphertext
    return ciphertext.encode('hex') 

def DecodePassword(ciphertext):
    ciphertext=ciphertext.decode('hex')
    decryptor=AES.new(key)
    plain=decryptor.decrypt(ciphertext)
    #print 'cipher---',ciphertext
    #print 'plain----',plain
    cipherlen=len(plain)   
    palinlen = cipherlen/16    
    passwd=plain[0:palinlen]
    #print passwd
    return passwd

def encrypt_password(password, salt=None):
    """Hash password on the fly."""
    if salt is None:
        salt = os.urandom(8) # 64 bits.

    assert 8 == len(salt)
    assert isinstance(salt, str)

    if isinstance(password, unicode):
        password = password.encode('UTF-8')

    assert isinstance(password, str)
    result = password
    
    for i in xrange(10):
        result = HMAC(result, salt, sha256).digest()
    return base64.b64encode(salt + result)


def validate_password(hashed, input_password):
    saltsha = base64.b64decode(hashed)
    return hashed == encrypt_password(input_password, salt=saltsha[:8])

if __name__ == '__main__':
    cipher = EncodePassword("netconf123");
    print 'ciphertext = ',cipher   
    passwd=DecodePassword(cipher)
    print 'password = ',passwd
    
    hashed = encrypt_password('secret password')
    print '----------', hashed
    
    assert validate_password(hashed, 'secret password')
    
    #hashed == encrypt_password(input_password, salt=hashed[:8])
    
    #def validate_password(hashed, input_password):
    #return hashed == encrypt_password(input_password, salt=hashed[:8])

    #assert validate_password(hashed, 'secret password')