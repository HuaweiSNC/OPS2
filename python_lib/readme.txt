
download python2.7.3.exe , install it 
download setuptools-4.0.1.zip ez_setup.py into same dir 
./ez_setup.py 

set PYTHON_PATH=c:\python27
set PATH=%PYTHON_PATH%/script;%PYTHON_PATH%;%PATH%

download pycrypto-2.6.tar.gz, and unzip 
cd /d pycrypto-2.6
easy_install .


easy_install pyasn1-0.1.6-py2.7.egg

easy_install lxml-2.3-py2.7-win32.egg


download xmltodict-0.4.2.tar.gz, and unzip
cd /d xmltodict-0.4.2
easy_install .

easy_install generateDS-2.8a-py2.7.egg

gevent-0.13.8.win32-py2.7.exe

greenlet-0.4.0.win32-py2.7.exe


easy_install pysnmp-4.2.4-py2.7.egg

download websocket-client-0.9.0.tar.gz, and unzip 
cd /d websocket-client-0.9.0
easy_install .


download gevent-websocket-0.3.6.tar.gz
cd /d gevent-websocket-0.3.6
easy_install .