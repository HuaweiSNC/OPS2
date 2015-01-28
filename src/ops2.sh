#!/bin/bash

echo OPS2.1 - Huawei.com 

export currentdir=/opt/ops/ops2.1

export PATH=$currentdir/tools/python27/bin:$PATH;  

# current dir 
export ops_port=8080
export ops_ip=localhost
export ops_web=Bottle_WebFrame.py
export LD_LIBRARY_PATH=$currentdir/tools/python27/lib:$LD_LIBRARY_PATH
export LIBRARY_PATH=$currentdir/tools/python27/lib:$LIBRARY_PATH
export PYTHONHOME=$currentdir/tools/python27

cd $currentdir
source ./ops2_version.sh
@echo "Huawei Open Programmable System $OPS_VERSION."
@echo "ops2.0 starting, enjoy it..."

# command like this: python Bottle_WebFrame.py  [ -serverip <ipaddr> -port <portnum> ] [ -loglevel <level> ] [ -certfile <certfile> ] [ -auth <true|false> ] [ -whitelist <true|false>] [-channelnum <number>] [-checkesn <true|false>]
# Supported level:DEBUG,INFO,WARNING,ERROR,CRITICAL

nohup python "$currentdir/OPS2/FlexPolicySocket.py" &
python "$currentdir/OPS2/$ops_web"

echo "ops2.0 ending, goodbye."





