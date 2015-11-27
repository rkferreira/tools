#!/usr/bin/python

##################
# Find CISCO ACLs

# You probably should adjust guessFile function, if you want.
# That is based on my file format, maybe not same as yours.

# Rodrigo Kellermann Ferreira
#   rkferreira@gmail.com


import ipaddress as ip
import re as re
import sys, os, subprocess
from optparse import OptionParser

exp1 = re.compile('(permit|deny) (ip|tcp|udp) host [0-9]{1,3}\..*.host [0-9]{1,3}\..*', re.IGNORECASE)
exp2 = re.compile('(permit|deny) (ip|tcp|udp) [0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3} [0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}.*.host [0-9]{1,3}\..*', re.IGNORECASE)
exp3 = re.compile('(permit|deny) (ip|tcp|udp) host [0-9]{1,3}\..*.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3} [0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}.*', re.IGNORECASE)
exp4 = re.compile('(permit|deny) (ip|tcp|udp) [0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3} [0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}.*.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3} [0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}.*', re.IGNORECASE)
exp5 = re.compile('(permit|deny) (ip|tcp|udp) any.*.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3} [0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}.*', re.IGNORECASE)
exp6 = re.compile('(permit|deny) (ip|tcp|udp) [0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3} [0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}.*.any.*', re.IGNORECASE)
exp7 = re.compile('(permit|deny) (ip|tcp|udp) host [0-9]{1,3}\..*.any.*', re.IGNORECASE)
exp8 = re.compile('(permit|deny) (ip|tcp|udp) any.*.host [0-9]{1,3}\..*', re.IGNORECASE)
exp9 = re.compile('(permit|deny) (ip|tcp|udp) any.*.any.*', re.IGNORECASE)

URL_FILTERS = 'https://filters.mydomain.com/'
FILTERS_POPS = ['DATACENTER01','DATACENTER02','DATACENTER03']

def download(dirprefix=None, abspath=None):
	if (not(dirprefix) and not(abspath)):
		dest = '.'
	else:
		if dirprefix:
			dest = './'+dirprefix+'/'
		else:
			dest = '.'+abspath+'/'

	for i in FILTERS_POPS:
		tgt_url = URL_FILTERS+i+'/invalid/ipv4/'
		cmd = 'cd '+dest+' ; '+'wget -A \'*.txt\' -r -nH --cut-dirs=3 '+tgt_url+' --no-check-certificate'
		output = os.system(cmd)
		if output:
			print "something went wront downloading, try it manually. I'm exiting now, see you."
			sys.exit(1)
		tgt_url = URL_FILTERS+i+'/valid/ipv4/'
		cmd = 'cd '+dest+' ; '+'wget -A \'*.txt\' -r -nH --cut-dirs=3 '+tgt_url+' --no-check-certificate'
		output = os.system(cmd)
		if output:
			print "something went wront downloading, try it manually. I'm exiting now, see you."
			sys.exit(1)

	sys.exit(0)


def guessFile(vlan, dirprefix=None, abspath=None):
	#default format v2513-BK_name-BACK_DC01_vl2513_out.txt
	#DC01-BK-2513-OUT
	parts = vlan.split('-')
	strVlan = '.*'+str(parts[2])+'-'+str(parts[1])+'.*.'+str(parts[0])+'.*.'+str(parts[3])+'.*'
	expVlan = re.compile(strVlan, re.IGNORECASE)

	if (not(dirprefix) and not(abspath)):
		proc = subprocess.Popen('ls -1 *.txt', stdout=subprocess.PIPE, shell=True)

	if dirprefix:
		cmd = 'ls -1 ./'+dirprefix+'/*.txt'
		#files = os.system(cmd)
		proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
	else:
		if abspath:
			cmd = 'ls -1 .'+abspath+'/*.txt'
			proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
			#files = os.system(cmd)
	
	files = list(proc.stdout.readlines())
	for f in files:
		if expVlan.match(f):
			print '#### '+f.rstrip('\n')+' ####\n'
			return f.rstrip('\n')

	return None
	

def readFile(f):
	fd = open(f, 'r')
	txt = fd.readlines()
	fd.close()
	return txt


def findNetRange(netrange, acl):
	if netrange:
		netrange = ip.ip_interface(unicode(netrange))
		ipandwildcard = str(netrange.ip) + " " + str(netrange.hostmask)
	else:
		ipandwildcard = None

	if exp2.match(acl):
		strToFind = '(permit|deny) (ip|tcp|udp) '+str(ipandwildcard)+'.*.host [0-9]{1,3}\..*'
		expToFind = re.compile(strToFind, re.IGNORECASE)
		if expToFind.match(acl):
                        #print "####### 3    " + i
			print acl.rstrip('\n')

	if exp3.match(acl):
		strToFind = '(permit|deny) (ip|tcp|udp) host [0-9]{1,3}\..*.'+str(ipandwildcard)+'.*'
		expToFind = re.compile(strToFind, re.IGNORECASE)
		if expToFind.match(acl):
			#print "####### 6    " + i
			print acl.rstrip('\n')

	if exp4.match(acl):
		strToFind = '(permit|deny) (ip|tcp|udp) '+str(ipandwildcard)+'.*.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3} [0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}.*'
		expToFind = re.compile(strToFind, re.IGNORECASE)
		if expToFind.match(acl):
			#print "####### 7    " + i
			print acl.rstrip('\n')
		else:
			strToFind = '(permit|deny) (ip|tcp|udp) [0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3} [0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}.*.'+str(ipandwildcard)+'.*'
			expToFind = re.compile(strToFind, re.IGNORECASE)
			if expToFind.match(acl):
				#print "####### 8    " + i
				print acl.rstrip('\n')

	if exp5.match(acl):
		strToFind = '(permit|deny) (ip|tcp|udp) any.*.'+str(ipandwildcard)+'.*'
		expToFind = re.compile(strToFind, re.IGNORECASE)
		if expToFind.match(acl):
			#print "####### 9    " + i
			print acl.rstrip('\n')

	if exp6.match(acl):
		strToFind = '(permit|deny) (ip|tcp|udp) '+str(ipandwildcard)+'.*.any.*'
		expToFind = re.compile(strToFind, re.IGNORECASE)
		if expToFind.match(acl):
			#print "####### 10    " + i
			print acl.rstrip('\n')
	return ""
	

def findIP(listipaddr, acl):
	for ipaddr in listipaddr:
		if exp1.match(acl):
			strToFind = '(permit|deny) (ip|tcp|udp) host '+ipaddr+'.*.host [0-9]{1,3}\..*'
			expToFind = re.compile(strToFind, re.IGNORECASE)
			if expToFind.match(acl):
				#print "####### 1    " + i
				print acl.rstrip('\n')
			else:
				strToFind = '(permit|deny) (ip|tcp|udp) host [0-9]{1,3}\..*.host '+ipaddr+'.*'
				expToFind = re.compile(strToFind, re.IGNORECASE)
				if expToFind.match(acl):
					#print "####### 2    " + i
					print acl.rstrip('\n')
		if exp2.match(acl):
			strToFind = '(permit|deny) (ip|tcp|udp) [0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3} [0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}.*.host '+ipaddr+'.*'
			expToFind = re.compile(strToFind, re.IGNORECASE)
			if expToFind.match(acl):
				#print "####### 4    " + i
				print acl.rstrip('\n')

		if exp3.match(acl):
			strToFind = '(permit|deny) (ip|tcp|udp) host '+ipaddr+'.*.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3} [0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}.*'
			expToFind = re.compile(strToFind, re.IGNORECASE)
			if expToFind.match(acl):
				#print "####### 5    " + i
				print acl.rstrip('\n')

		if exp7.match(acl):
			strToFind = '(permit|deny) (ip|tcp|udp) host '+ipaddr+'.*.any.*'
			expToFind = re.compile(strToFind, re.IGNORECASE)
			if expToFind.match(acl):
				#print "####### 11    " + i
				print acl.rstrip('\n')

		if exp8.match(acl):
			strToFind = '(permit|deny) (ip|tcp|udp) any.*.host '+ipaddr+'.*'
			expToFind = re.compile(strToFind, re.IGNORECASE)
			if expToFind.match(acl):
				#print "####### 12    " + i
				print acl.rstrip('\n')

		if exp9.match(acl):
			#print "####### 13    " + i
			print acl.rstrip('\n')
	return ""


def helpTxt(option, opt, value, parser):
	print "\n-i/--ip   	--> find exactly this ip address. input format eg.: 10.1.1.1"
	print "-r/--range  	--> find a line that matchs the range. input format eg.: 10.1.1.0/24 \n		It will find for 10.1.1.0 0.0.0.255"
	print "-a/--allips 	--> find all ips from a range line. input format eg.: 10.1.1.0/30 \n 		It will find for 10.1.1.1 and 10.1.1.2"
	print "-f/--file   	--> file name/path \n"
	print "-v/--vlan   	--> I'll guest the file name based on vlan number. input format eg.: DC01-BK-2559-OUT \n		It will find for vlan 2559 in datacenter rules DC01 and it is backnet BK"
	print "-d/--download 	--> I'll download acl files from site, so I can parse later. You must have ~/.wgetrc configured correctly \n"
	sys.exit(0)


def main():
	ipaddr	 = []
	netrange = None
	file	 = None
	vlan	 = None
	#file = "test.txt"

	parser = OptionParser()
	parser.add_option("-i", "--ip", dest="ipaddr", help="find exactly this ip address (eg.: 10.1.1.1)")
	parser.add_option("-r", "--range", dest="netrange", help="find a line that matchs the range (eg.: 10.1.1.0/24)")
	parser.add_option("-a", "--allips", dest="allips", help="find all ips from a range line (eg.: 10.1.1.0/24)")
	parser.add_option("-f", "--file", dest="file", help="file name/path where are the rules)")
	parser.add_option("-v", "--vlan", dest="vlan", help="saying this I'm going to guess the file. Yes, I know how todo magic!")
	parser.add_option("-d", "--download", action="store_true", dest="download", help="download acl files, must be called alone. Just --prefix and --abspath are supported for that", default=False)
	parser.add_option("--prefixdir", dest="prefixdir", help="prefix for opening or downloadin files")
	parser.add_option("--abspath", dest="abspath", help="absolute path for opening or downloading files")
	parser.add_option("-?", action="callback", callback=helpTxt, help="detailed help. -h/--help also work")
	(options, args) = parser.parse_args()

	if (not(options.ipaddr) and not(options.netrange) and not(options.allips) and not(options.download)):
		helpTxt("","","","")

	if options.download:
		print "I'll just download, no combined options are possible. Just --prefix and --abspath for saving those files."
		download(options.prefixdir, options.abspath)

	if not(options.file) and not(options.vlan):
		print "let me know the FILE I should check, I'm a dummy script.\nCall again using -f/--file or -v/--vlan\n"
		sys.exit(0)
	else:
		if options.file:
			file = options.file
		else:
			file = None
			vlan = options.vlan

	if vlan:
		file = guessFile(vlan, options.prefixdir, options.abspath)
	if not(file):
		print "I couldnt get the file for parse, please check vlan parameters. Maybe you should download before."

	if options.ipaddr:
		ipaddr.append(options.ipaddr)

	if options.allips:
		for i in ip.ip_network(unicode(options.allips)):
			ipaddr.append(str(i))

	if options.netrange:
		netrange = options.netrange
		
	res = readFile(file)

	if len(ipaddr) >= 1:
		print "Finding lines for "+str(len(ipaddr))+" ips... \n Maybe you can get dup lines, if there is more than one ip, \"any\" matchs every one, try \"sort\" and \"uniq\" the output.\n"
	if netrange:
		print "Finding lines for 1 range..."
	for idx, i in enumerate(res):
		if netrange:
			got = findNetRange(netrange, i)

		if ipaddr:
			got = findIP(ipaddr, i)


if __name__ == "__main__":
	main()
