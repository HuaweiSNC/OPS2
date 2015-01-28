#!/bin/bash

echo OPS2.1 trap - Huawei.com 

export currentdir=`pwd`

export PATH=$currentdir/tools/python27/bin:$PATH;  

# current dir 
export ops_ip=localhost
export ops_web=Notification.py
export LD_LIBRARY_PATH=$currentdir/tools/python27/lib:$LD_LIBRARY_PATH
export LIBRARY_PATH=$currentdir/tools/python27/lib:$LIBRARY_PATH
export PYTHONHOME=$currentdir/tools/python27

cd $currentdir
echo "ops2.0 trap starting, enjoy it..."
 
python "$currentdir/OPS2/$ops_web"

echo "ops2.0 trap ending, goodbye."





