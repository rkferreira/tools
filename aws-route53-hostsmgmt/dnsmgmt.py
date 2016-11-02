#!/usr/bin/python
 
import boto3
import botocore
import fcntl
import json
import re
import socket
import struct
import sys
import time
from datetime import datetime
from optparse import OptionParser


ZONE_ID 	= 'MYROUTE53-ZONEID'

DEF_DOMAIN 	= ".myroute53domain"
REGION		= "us-east-1"
TTL		= 600
RTYPE		= "A"
COMMENT		= "dnsmgmt auto registration"
LOG_PREFIX	= "[dnsmgmt] "

client		= boto3.client('route53')
t1    		= datetime.now().strftime("%c")


def get_ip_address(ifname):
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	return socket.inet_ntoa(fcntl.ioctl( s.fileno(), 0x8915, struct.pack('256s', ifname[:15]) )[20:24])


def getridof_fqdn(host):
	if re.search('\.', host):
		h = host.split('.')
		host = h[0]

	return host
		

def get_hostname(h=None):
	if h:
		#re_fqdn = re.compile('[a-zA-Z\d-]{,63}(\.[a-zA-Z\d-]{,63})*', re.IGNORECASE)
		if re.search('\.', h):
			ip = socket.gethostbyname(h)
			host = h
		else:
			h = h + DEF_DOMAIN
			ip = socket.gethostbyname(h)
			host = h
	else:
		host = socket.gethostname()
		try:
			ip   = socket.gethostbyname(host)
		except:
			ip = get_ip_address('eth0')
			pass

	print "%s Hostname : %s" % (LOG_PREFIX, host)
	print "%s IP : %s" % (LOG_PREFIX, ip)
	return(host,ip)


#####
#{u'ResourceRecordSets': [ {u'Name': 'host.mydomain.com.', u'Type': 'A', u'Region': 'us-east-1', u'ResourceRecords': [ {u'Value': '10.0.0.1'}], u'TTL': 600, u'SetIdentifier': 'dnsmgmt auto registration'} ], 

def list_rr(entry=None, t=None, ALL=0):
	if ALL == 0:
		response = client.list_resource_record_sets(
			HostedZoneId=ZONE_ID,
			StartRecordName=entry,
			StartRecordType=t
		)
	else:
		response = client.list_resource_record_sets(
                        HostedZoneId=ZONE_ID
                )

	rr_entries = ''

	for k,v in response.iteritems():
		if k == 'ResourceRecordSets':
			for a in response[k]:
				rr_entries = rr_entries + a['Name'] + ' '
				rr_entries = rr_entries + a['Type'] + ' '
				for b in a['ResourceRecords']:
					rr_entries = rr_entries + b['Value'] + '\n'

	return rr_entries


def create_record(entry, ip, t=RTYPE, reg=REGION, ttl=TTL, comment=COMMENT):
	print "%s Starting creation process %s %s" % (LOG_PREFIX, entry, ip)
	name = entry + DEF_DOMAIN
	try:
		response = client.change_resource_record_sets(
			HostedZoneId=ZONE_ID,
			ChangeBatch={
				'Changes': [
				{
					'Action': 'UPSERT',
					'ResourceRecordSet': {
					'Name': name,
					'Region': reg,
					'Type': t,
					'TTL': ttl,
					'SetIdentifier': comment,
					'ResourceRecords': [
						{
							'Value': ip
						}
					],
					}
				}
				]
			}
		)

	except:
		print "%s Error creating entry %s" % (LOG_PREFIX,name)
		print(response)

	print "%s Status: %s | Id: %s" % (LOG_PREFIX, response['ChangeInfo']['Status'], response['ChangeInfo']['Id'])
	s = response['ChangeInfo']['Status'] 
	i = response['ChangeInfo']['Id']

	while s == 'PENDING':
		s = get_change_status(i)
		time.sleep(10)

	print "%s Entry %s has been created. Request status is: %s" % (LOG_PREFIX, name, s)
	return response


def get_change_status(reqid):
	response = client.get_change(
		Id=reqid
	)
	#response = client.get_change_details(Id=reqid)
	return response['ChangeInfo']['Status']


def delete_record(entry, ip, reg=REGION, t=RTYPE, ttl=TTL, comment=COMMENT):
	print "%s Starting deletion process %s %s" % (LOG_PREFIX, entry, ip)
	name = entry + DEF_DOMAIN
	try:
		response = client.change_resource_record_sets(
			HostedZoneId=ZONE_ID,
			ChangeBatch={
				'Changes': [
				{
					'Action': 'DELETE',
					'ResourceRecordSet': {
					'Name': name,
					'Region': reg,
					'Type': t,
					'TTL': ttl,
					'SetIdentifier': comment,
					'ResourceRecords': [
						{
							'Value': ip
						}
					],
					}
				}
				]
			}
		)

	except:
		print "%s Error deleting record %s" % (LOG_PREFIX,name)
		print(response)

	print "%s Status: %s | Id: %s" % (LOG_PREFIX, response['ChangeInfo']['Status'], response['ChangeInfo']['Id'])
	s = response['ChangeInfo']['Status']
	i = response['ChangeInfo']['Id']

        while s == 'PENDING':
                s = get_change_status(i)
                time.sleep(10)

	print "%s Entry %s has been removed" % (LOG_PREFIX, name)
	return response


def helpTxt(option, opt, value, parser):
	print "\n-a/--add   	--> ADD action\n"
	print "-r/--remove  	--> REMOVE action\n"
	print "-n/--name 	--> HOSTNAME to add\n"
	print "-i/--ip   	--> IPADDR to add"
	sys.exit(0)


def main():
	parser = OptionParser()
	parser.add_option("-a", "--add", action="store_const", const=1, dest="dnsadd", help="add new DNS entry")
	parser.add_option("-r", "--remove", action="store_const", const=1, dest="dnsremove", help="remove a DNS entry")
	parser.add_option("-n", "--name", dest="dnshost", help="hostname NOT fqdn")
	parser.add_option("-i", "--ip", dest="dnsip", help="ipaddress")
	parser.add_option("-?", action="callback", callback=helpTxt, help="detailed help")
	(options, args) = parser.parse_args()

	h,i = get_hostname()
	h = getridof_fqdn(h)

	if (options.dnshost):
		h = options.dnshost
	if (options.dnsip):
		i = options.dnsip
	if ( (not(options.dnsadd) and not(options.dnsremove)) or (options.dnsadd) ):
		#Assume you are adding the local machine
		r = create_record(entry=h, ip=i)
	if (not(options.dnsadd) and options.dnsremove):
		#Assumme you are deleting the local machine
		d = delete_record(entry=h, ip=i)
	l = list_rr(h+DEF_DOMAIN,RTYPE); print "%s %s" % (LOG_PREFIX, l)


if __name__ == '__main__':
	main()
