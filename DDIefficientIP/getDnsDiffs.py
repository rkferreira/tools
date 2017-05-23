#!/usr/bin/python

import dns.resolver
import requests
import base64
import urllib
import json
import time
import re
import sys
import smtplib
from email.mime.text import MIMEText
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

### getDnsDiffs
#
# It queries local DNS server versus Google 8.8.8.8 and compare answers.
# Just to check if there are inconsistencies on local database X internet.
#
# Schedule as crontab:    >/tmp/getDnsDiffs.txt && /usr/local/bin/getDnsDiffs.py >> /tmp/getDnsDiffs.txt
#

##############################################################
USER  = 'restuser'
PASSW = 'xxxxxxx'
URL   = 'https://my-efficientIP-server/rest/'
##############################################################

localResolver = dns.resolver.Resolver()
localResolver.nameservers = ['127.0.0.1']

extResolver = dns.resolver.Resolver()
extResolver.nameservers = ['8.8.8.8']

arpa = re.compile("^.*.10\.in-addr\.arpa$")

whitelist = ['168.192.in-addr.arpa','127.in-addr.arpa']



user64 = base64.b64encode(USER)
passw64 = base64.b64encode(PASSW)
h = {'X-IPM-Username': user64, 'X-IPM-Password': passw64}

url = URL+'dns_zone_list/'
print 'Querying dns_zone_list for domain: '+url
r = requests.get(url, headers=h, verify=False)
print '\nI\'m not trying query 8.8.8.8 for ^.*.10.in-addr.arpa$ those are internal.\n\n'


print "-BEGIN"
for a in r.json():
	localAnswers = []
	extAnswers = []
	diff = []

	domain = a['dnszone_name']
	try:
		localAnswers = localResolver.query(domain, "NS")
	except:
		localAnswers = []
		print domain
		print "--Error1..."+localResolver.nameservers[0]
		pass

	try:
		got = False
		if not arpa.match(domain):
			for i in whitelist:
				if i == domain:
					got = True
					print domain
					print "--Whitelisted..."+extResolver.nameservers[0]
					whitelist.remove(i)
					break
			if not got:
				extAnswers = extResolver.query(domain, "NS")
	except:
		extAnswers = []
		print domain
		print "--Error2..."+extResolver.nameservers[0]
		pass

	if extAnswers and localAnswers:
		diff   = set(extAnswers) - set(localAnswers)

	if diff:
		print domain
		print "--Difference..."+str(diff)

print "-END"

sys.stdout.flush()

fp = open('/tmp/getDnsDiffs.txt', 'rb')
msg = MIMEText(fp.read())
fp.close()

msg['Subject'] = 'getDnsDiffs - Check Local EIP x External GoogleDNS'
msg['From'] = 'root@myDnsServer'
msg['To'] = 'user@mydomain.com'
s = smtplib.SMTP('mysmtprelay.mydomain.com')
s.sendmail('root@myDnsServer', 'user@mydomain.com', msg.as_string())
s.quit()
