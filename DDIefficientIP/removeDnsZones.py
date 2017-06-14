#!/usr/bin/python

import requests
import base64
import urllib
import json
import time


##############################################################
USER  = 'myeipuser'
PASSW = 'mypass'
URL   = 'https://myeip.mydomain.com/rest/'
##############################################################

MYFILE = "list.txt"

user64 = base64.b64encode(USER)
passw64 = base64.b64encode(PASSW)
h = {'X-IPM-Username': user64, 'X-IPM-Password': passw64}

f = open(MYFILE, 'r')
for line in f:
	print "-BEGIN"
	DOMAIN = line.strip()
	print "Going to process: "+DOMAIN

	f = { 'dnszone_name': '\''+DOMAIN+'\''}
	url = URL+'dns_zone_list/WHERE/'+urllib.urlencode(f)
	print 'Querying dns_zone_list for domain: '+url

	r = requests.get(url, headers=h, verify=False)
	try:
		j = r.json()[0]
	except:
		print "Error querying: "+DOMAIN
		print "-END\n\n"
		time.sleep(12)
		continue

	dnszoneid1 = j['dnszone_id']
	print 'dns_id:       '+j['dns_id']
	print 'dns_name:     '+j['dns_name']
	print 'dnszone_id:   '+j['dnszone_id']
	print 'dnszone_name: '+j['dnszone_name']
	dnszonename1 = j['dnszone_name']

	if dnszoneid1 and (dnszonename1 == DOMAIN):
		url = URL+'dns_zone_info/dnszone_id/'+dnszoneid1
		print 'Getting dns_zone_info for: '+url
		z = requests.get(url, headers=h, verify=False)

		print 'Full json: '+r.text
		s = z.json()[0]

		print 'dns_id:       '+s['dns_id']
		dnsid = s['dns_id']
		print 'dns_name:     '+s['dns_name']
		dnsname = s['dns_name']
		print 'dnszone_id:   '+s['dnszone_id']
		dnszoneid = s['dnszone_id']
		print 'dnszone_name: '+s['dnszone_name']
		dnszonename = s['dnszone_name']

		if dnsid and dnsname and dnszoneid and dnszonename:
			d = None
			print "Going to delete: "+dnszonename
			url = URL+'dns_zone_delete/dns_id/'+dnsid+'/dns_name/'+dnsname+'/dnszone_id/'+dnszoneid+'/dnszone_name/'+dnszonename
			print url
			try:
				if DOMAIN == dnszonename:
					#d = requests.delete(url, headers=h, verify=False)
					print d.status_code
					print d.text
				else:
					print "Error deleting (comparison): "+DOMAIN
			except:
				print "Error deleting: "+DOMAIN
				print "-END\n\n"
				time.sleep(12)
				continue
	print "-END\n\n"
	time.sleep(12)
