#!/bin/bash

echo OPS2.1 flexPolicy - Huawei.com 

export currentdir=`pwd`

export PATH=$currentdir/tools/python27/bin:$PATH;  

# current dir 
export ops_port=8080
export ops_ip=localhost
export ops_web=Bottle_WebFrame.py
export LD_LIBRARY_PATH=$currentdir/tools/python27/lib:$LD_LIBRARY_PATH
export LIBRARY_PATH=$currentdir/tools/python27/lib:$LIBRARY_PATH
export PYTHONHOME=$currentdir/tools/python27

cd $currentdir
echo "ops2.0 flexPolicy starting, enjoy it..."

python "$currentdir/OPS2/FlexPolicySocket.py"

echo "ops2.0 flexPolicy ending, goodbye."





