#!/usr/bin/python

import argparse
import base64
import dns.resolver
import ipaddress
import json
import requests
import urllib

##############################################################
USER  = 'xxxx'
PASSW = 'xxxx'
DNSSERVER = 'smart.localhost'
URL   = 'https://hlg-eip.foo.bar/rest/'
##############################################################

user64	    = base64.b64encode(USER)
passw64	    = base64.b64encode(PASSW)
authHeaders = {'X-IPM-Username': user64, 'X-IPM-Password': passw64}



def add_rr(name, hostname, domain, rtype):
	validate_res, zoneid, dnszonesiteid = validate_zone(domain)
	if validate_res and dnszonesiteid:
		qurl = URL+'dns_rr_add/dns_name/'+DNSSERVER
		query = '/dnszone_name/'+domain+'/rr_name/'+hostname+"."+domain+'/rr_value1/'+name+'/dnszone_site_id/'+dnszonesiteid+'/rr_type/'+rtype
		#OOOKKKKKquery = '/dnszone_name/'+domain+'/rr_name/'+hostname+"."+domain+'/rr_type/A'+'/rr_value1/'+ip+'/dnszone_site_id/'+dnszonesiteid
		#query = '/dnszone_id/'+zoneid+'/dnszone_name/'+domain+'/rr_name/'+hostname+"."+domain+'/rr_value1/'+ip+'/dnszone_site_id/'+dnszonesiteid+'/rr_type/A'
		qurl = qurl+query
		print qurl
		res = requests.put(qurl, headers=authHeaders, verify=False)
		print res.status_code
		return True

	else:
		print "(add_rr): Couldnt validate the specified domain."
		return False


def validate_zone(domain):
	qurl = URL+'dns_zone_list/WHERE/'
	query = None

	if domain:
		query = 'dnszone_name=\''+domain+'\''

	qurl = qurl+urllib.quote(query, '=')
	res = requests.get(qurl, headers=authHeaders, verify=False)
	if res.status_code == 200:
		print "(validate_zone): This is a valid zone."
		val = res.json()[0]
		zonename = val['dnszone_name']
		zoneid	 = val['dnszone_id']
		dnszonesiteid = val['dnszone_site_id']
		print "(validate_zone): dnszone_name %s" % zonename
		print "(validate_zone): zoneid %s" % zoneid
		print "(validate_zone): dnszonesiteid %s" % dnszonesiteid
		return True, zoneid, dnszonesiteid
	else:
		print "Sorry, couldnt find specified zone."
		return False, False, False


def remove_rr():
	print "teste2"

def check_rr(name, hostname, domain, rtype):
	qurl = URL+'dns_rr_list/WHERE/'
	query = None
	print name

	if hostname and domain:
		query = 'rr_full_name=\''+hostname+'.'+domain+'\''
	if name:
		if query:
			 query = query+' and value1=\''+name+'\''
		else:
			query = 'value1=\''+name+'\''
	if domain:
		query = query+' and dnszone_name=\''+domain+'\''

	print query
	qurl = qurl+urllib.quote(query, '=')
	print qurl
        res = requests.get(qurl, headers=authHeaders, verify=False)

	if res.status_code == 200:
		val = res.json()[0]
		print "(check_rr): Found. HTTP return "+str(res.status_code)+".\n "+val['rr_id']+","+val['rr_full_name']+","+val['rr_type']+","+val['value1']+","+val['dnszone_name']
		return True
	else:
		print "(check_rr): Not found. HTTP return %s" % res.status_code
		return False


def validate_ip(ip):
	ip = unicode(ip)
	try:
		ipaddr = ipaddress.ip_address(ip)
		return True, ipaddr.exploded
	except:
		return False, None


def validate_hostname(hst):
	tmp = hst.split(".", 1)
	s = len(tmp)
	hostname = tmp[0]
	domain   = None
	
	if s > 1:
		domain   = tmp[1]

	return hostname,domain


def validate_domain(domain, hstdomain):
	if domain == hstdomain:
		return domain

	print "(validate_domain): You have told me different DOMAIN values, so I need to check now. Pay attention Dude!"

	try:
		d1 = dns.resolver.query(domain, 'NS')
		print '(validate_domain): %s it seems good' % domain
	except:
		print '(validate_domain): Dude, domain %s isnt valid\n' % domain
		d1 = False
		pass

	try:
		d2 = dns.resolver.query(hstdomain, 'NS')
		print '(validate_domain): %s it seems good' % hstdomain
	except:
		print '(validate_domain): Dude, domain %s isnt valid\n' % hstdomain
		d2 = False
		pass

	if d1 and d2:
		print '(validate_domain): I see both valids, I will pick the DOMAIN parameter, as you have explicited provided that, I trust you Dude.\n'
		return domain

	if d1:
		return domain
	if d2:
		return hstdomain



def parser_opts(args):

	#Find the operation
	if args.add == True:
		operation = "add"
	elif args.remove == True:
		operation = "remove"
	elif args.check == True:
		operation = "check"
	else:
		operation = None

	#Is there an IP?
	if args.name:
		tmpip = args.name
		ip, ipval = validate_ip(tmpip)
		if ip:
			name = ipval
		else:
			name = args.name
	else:
		name = None

	#RR type. default is A
	if args.rtype:
		rtype = args.rtype
		#if ip and rtype == "A":
		#	rtype = "A"
	else:
		rtype = None

	#Is there a Hostname?
	if args.hostname:
		tmphst = args.hostname
		hostname,hstdomain = validate_hostname(tmphst)
	else:
		hostname  = None
		hstdomain = None
	
	#Is there a Domain?
	if args.domain:
		tmpdomain = args.domain
		domain = validate_domain(tmpdomain, hstdomain)
	elif hstdomain:
		tmpdomain = hstdomain
		domain = validate_domain(tmpdomain, hstdomain)
	else:
		domain = None

	return operation, name, hostname, domain, rtype


def main():

	parser = argparse.ArgumentParser(description="Script for interaction with EfficientIP API",epilog='''Example:  ./eip.py -a -n 10.0.0.1 -hst test.foo.bar''')
	group_op = parser.add_mutually_exclusive_group()
	group_op.add_argument("-a", "--add", action="store_true", help="Add a new DNS rr")
	group_op.add_argument("-r", "--remove", action="store_true", help="Remove a DNS entry")
	group_op.add_argument("-c", "--check", action="store_true", help="Query for a DNS entry")
	parser.add_argument("-n", "--name", type=str, help="This is the value for the HOSTNAME provided on -hst/--hostname. IP address or hostname. This is RR value.")
	parser.add_argument("-t", "--rtype", type=str, default="A", help="RR type, ie: A or CNAME. Default: A")
	parser.add_argument("-hst", "--hostname", type=str, help="HOSTNAME that is going to be created. FQDN or not.")
	parser.add_argument("-d", "--domain", type=str, help="Domain name for the HOSTNAME. Optional if provided FQDN on HOSTNAME value.")
	args = parser.parse_args()

	operation,name,hostname,domain,rtype = parser_opts(args)

	print "(main): operation %s" % operation
	print "(main): name %s" % name
	print "(main): hostname %s" % hostname
	print "(main): domain %s" % domain
	print "(main): type %s" % rtype

	if operation == "check":
		check_res = check_rr(name,hostname,domain,rtype)
		if check_res == True:
			print "(main): It exists!\n"
		else:
			print "(main): There is no such entry\n"

	if operation == "add":
		check_res = check_rr(name,hostname,domain,rtype)
		if check_res == False:
			print "(main): Couldnt find it, so going to add"
			add_res = add_rr(name,hostname,domain,rtype)
			
		else:
			print "(main): It exists, already. Stopping."
		



if __name__ == '__main__':
	main()
