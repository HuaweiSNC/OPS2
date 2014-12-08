
@echo off

set currentdir=%~dp0
set PATH=%currentdir%\python27;%PATH%

::current dir 
set ops_port=8080
set ops_ip=localhost
set ops_web=Bottle_WebFrame.py

cd /d %currentdir%\OPS2
echo "ops2.0 starting, enjoy it..."
:: command like this: python Bottle_WebFrame.py [ -serverip <ipaddr> -port <portnum> ] [ -loglevel <level> ] [ -certfile <certfile> ] [ -auth <true|false> ] [ -whitelist <true|false>] [-channelnum <number>]
:: Supported level:DEBUG,INFO,WARNING,ERROR,CRITICAL

python "%currentdir%\OPS2\%ops_web%"

echo "ops2.0 ending, goodbye."

pause 




