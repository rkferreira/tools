#!/bin/bash

. /root/.custom/unity01

cd $UNITY01_BKP_DIR
if [ $? -eq 0 ]; then
	/usr/bin/date >> $UNITY01_LOG
	/usr/bin/uemcli -d $UNITY01_HOST -u $UNITY01_USER -p $UNITY01_SVC_PASS -noHeader /service/system collect -config -showPrivateData >> $UNITY01_LOG
	/usr/bin/uemcli -d $UNITY01_HOST -u $UNITY01_USER -p $UNITY01_SVC_PASS -noHeader -download config >> $UNITY01_LOG
fi
