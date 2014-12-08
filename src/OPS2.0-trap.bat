
@echo off

set currentdir=%~dp0
set PATH=%currentdir%\python27;%PATH%

::current dir 
set ops_port=8080
set ops_ip=localhost
set trap_web=Notification.py

cd /d %currentdir%\OPS2
echo "ops2.0 trap starting, enjoy it..."
 
python "%currentdir%\OPS2\%trap_web%"

echo "ops2.0 trap ending, goodbye."

pause 




