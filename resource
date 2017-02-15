#!/bin/bash
#
#

BIN="/root/.pyenv/versions/3.5.2/bin/python3.5" 

CONF="/ROOT/sh/svn/panda/scripts/machineResource/resource.aiuv.cc/resource.aiuv.cc.py"

PID_FILE=/tmp/resource.pid

case $1 in 
	start)
		if [ -f $PID_FILE ];then
			echo "Maybe already running...! Pid file is: $PID_FILE"
			exit 2
		fi
		nohup $BIN $CONF > /tmp/resource.log &
		PID=$(ps axu | grep resource.aiuv.cc.py | grep -v grep | awk '{print $2}')
		echo $PID > $PID_FILE
		;;
	stop)
		if [ ! -f $PID_FILE ];then
			echo "Maybe not run ! Pid file not find ($PID_FILE)"
			exit 2
		fi
		kill $(cat $PID_FILE) && rm -rf $PID_FILE
		;;
	*)
		echo "Usage:$0 {start|stop}"
esac
