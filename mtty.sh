#!/usr/bin/env bash

DEV_PATH=$1
if [ -z "$DEV_PATH" ]; then
	DEV_PATH="/dev/ttyUSB0"
fi
DEV_NAME=$(basename $DEV_PATH)

LOG_PATH=$2
if [ -z "$LOG_PATH" ]; then
	LOG_PATH="/tmp/$DEV_NAME.log"
fi

WAIT=60

function log() {
	echo "$1" >> $LOG_PATH
}

while true; do
	DATE=$(date +%Y-%m-%d:%H:%M:%S)
	log "---{[ $DATE: Starting mtty of $DEV_PATH ]}---"
	stty -F /dev/ttyUSB0 -icrnl -onlcr -imaxbel -opost -isig -icanon -echo line 0 kill ^H min 100 time 2 brkint 115200

	ERR=$?
	if [ $ERR -ne 0 ]; then
		log "Failed stty dev_path($DEV_PATH), ERR($ERR)"
	fi

	cat $DEV_PATH 2>&1 >> $LOG_PATH
	ERR=$?
	if [ $ERR -ne 0 ]; then
		log "Failed cat dev_path($DEV_PATH), ERR($ERR)"
	fi

	sleep $WAIT
done
