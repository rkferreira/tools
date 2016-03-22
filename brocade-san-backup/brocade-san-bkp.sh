#!/bin/bash

#
# It backups BROCADE SAN SWITCH configurations to an FTP
# It must run on a linux cron and you must have SSH access to switch and a destination FTP to store those backups
#

SAN1="switch01.foo.bar.com"
SAN2="switch02.foo.bar.com"
SANU="switchUser"
SPASS="switchPass"

FHOST="ftphost.foor.bar.com"
FUSER="ftpUser"
FPASS="ftpPass"
FDIR="ftpDir"

DATE=`date +%F`
CONFIGUPLOAD="configupload"
SLEEP="/bin/sleep"


for i in $SAN1 $SAN2; do

	/usr/bin/expect -c '
	    spawn ssh '$SANU'@'$i' "configupload -all -ftp '$FHOST','$FUSER','$FDIR'/config_'$i'_'${DATE}'.txt,'$FPASS'"
	    expect "password:"
	    send "'$SPASS'\r"
	    send "exit"
	    expect eof'
	$SLEEP 5

	/usr/bin/expect -c '
	    spawn ssh '$SANU'@'$i' "configupload -chassis -ftp '$FHOST','$FUSER','$FDIR'/chassis_'$i'_'${DATE}'.txt,'$FPASS'"
	    expect "password:"
	    send "'$SPASS'\r"
	    send "exit"
	    expect eof'
	$SLEEP 5

	/usr/bin/expect -c '
	    spawn ssh '$SANU'@'$i' "configupload -vf -ftp '$FHOST','$FUSER','$FDIR'/switch_vf_'$i'_'${DATE}'.txt,'$FPASS'"
	    expect "password:"
	    send "'$SPASS'\r"
	    send "exit"
	    expect eof'
	$SLEEP 5

done
