setlocal enabledelayedexpansion
set currentdir=%~dp0

cd /d %currentdir%

set PYTHONHOME=E:\SDN\AgileTE\tools\Python27
set ops_src=%currentdir%python
set WINRAR="C:\Program Files\WinRAR\WinRAR.exe"
set PATH=%PYTHONHOME%;%PATH% 
set BUILD_TIME=Build %date:~0,4%%date:~5,2%%date:~8,2%0%time:~1,1%%time:~3,2%
set OPS_VERSION=V2.1 %BUILD_TIME%

echo import compileall > compile.py
echo compileall.compile_dir('%ops_src%')  >> compile.py
python compile.py

rmdir /S/Q %currentdir%\python_bin
mkdir %currentdir%\python_bin\ops2.1\OPS2

xcopy /Y /E %ops_src%\*  %currentdir%\python_bin\ops2.1\OPS2
cd /d %currentdir%\python_bin\ops2.1\OPS2
del /S/Q *.py

cd /d %currentdir%

copy /y python27_suse11.zip python_bin\
copy /y *.sh python_bin\ops2.1
@echo export OPS_VERSION=%OPS_VERSION% >¡¡python_bin\ops2.1\ops2_version.sh

cd /d %currentdir%\python_bin
%WINRAR% A python27_suse11.zip ops2.1

move /y python27_suse11.zip ops2.1_python27_suse11_%BUILD_TIME%.zip

cd /d %currentdir%


