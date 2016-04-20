#!/usr/bin/python

import requests
import sys, os
from datetime import datetime
import re as re
import subprocess


## Main conf
#
HOST    = 'http://127.0.0.1:8080'
URL     = '/test'
HAPROXY = 'echo "show stat" | socat /var/lib/haproxy/stats stdio'
FILE	= '/tmp/haproxy-resptime.txt'


def getHttp(host, url):
	r = None

	try:
		r = requests.get(host + url, timeout=(5,10))
		c = checkHTTPResponse(r.text)
		if c == 0:
			raise Exception('HTTPContentNotExpected')
	except:
		e = sys.exc_info()
		errorHandle(e)

	return r


def getHA(cmd):
	return subprocess.check_output(cmd, shell=True)


def checkHTTPResponse(data):
	# Put expected page string
	exp1 = re.compile('.*.EXPECTED_HTTP_PAGE_STRING.*.', re.IGNORECASE)

	list1 = data.split("\n")
	for i in list1:
		if exp1.match(i):
			return 1

	return 0


def checkDown(text):
	# Put also expected HAPROXY down string
	exp1 = re.compile('^backend.*.DOWN.*', re.IGNORECASE)
	r = "OK"
	j = 0

	list1 = text.split("\n")
	for i in list1:
		if exp1.match(i):
			a = i.split(",")
			if j == 0:
				r = a[1]
			else:
				r = r + "," + a[1]
			j += 1

	return r


def formatTime(t):
	rtime = datetime.strptime(str(t),"%H:%M:%S.%f")
	return rtime.strftime("%S.%f")


def writeRespFile(file, rcode, time, url, ha):
	try:
		f = open(file, 'w+', 200)
		f.write('REQ_HTTP-STATUS-CODE %s\n' % (rcode))
		f.write('REQ_ELAPSED-TIME %s\n' % (time))
		f.write('REQ-URL %s\n' % (url))
		f.write('HA_DOWN_SERVERS %s\n' % (ha))
		f.flush()
		return f.close()
	except:
		e = sys.exc_info()
		errorHandle(e)

	return False


def errorHandle(e, file=FILE, rcode="UNKNOWN", time="UNKNOWN", url=URL, ha="UNKNOWN"):
	if e[0] == requests.exceptions.ConnectTimeout:
		print "ERROR timeout\n\n"

	elif e[0] == requests.exceptions.ConnectionError:
		print "ERROR connection error\n\n"

	elif e[0] == Exception:
		if str(e[1]) == 'HTTPContentNotExpected':
			print "ERROR HTTP Content different from expected one\n\n"

	writeRespFile(file, rcode, time, url, ha)
	raise


def main():
	host = HOST
	url  = URL
	file = FILE
	ha   = HAPROXY
	r    = None

	r = getHttp(host, url)
	d = formatTime(r.elapsed)
	g = getHA(ha)
	c = checkDown(g)

	res = writeRespFile(file, r.status_code, d, url, c)

	return res
		

if __name__ == "__main__":
	main()
