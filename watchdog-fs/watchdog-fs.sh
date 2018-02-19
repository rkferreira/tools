#!/bin/sh
TARGETPATH="/tmp/"
FILENAME="*.txt"
MAILADDR="foo@foo.com"
/usr/bin/python -m pyinotify -e IN_CLOSE_WRITE ${TARGETPATH} -f -c '/usr/bin/ls -lat ${TARGETPATH}${FILENAME} | /usr/bin/mail -s "${TARGETPAH} - ${FILENAME} file modifications" ${MAILADDR}'
