#!/usr/bin/python

#############################################################
## VMWare migration script.
#Usage:
#	./script guestName dataCenter
#
#Author:  Rodrigo Kellermann Ferreira
#Version: 0.3
#Date:    Jan/13/2015
#

import os, sys, string, time, paramiko
from pysphere import VIServer

####### CONFIG
userLDAP		=	"userldap"
passLDAP		=	"passldap"
server1			=	"vcenterserver.mydomain.com"
splitOrigemHost		=	"transferServerOriginInternalNetwork.mydomain.com"
splitOrigemHostFr	=	"transferServerOriginExternalNetwork.mydomain.com"
splitDestHost		=	"transferServerDestination.mydomain.com"
splitDestPath		=	"/cache/transfer/"
vmOrigemHost		=	"esxOriginServer.mydomain.com"
vmDestHost		=	"esxDestServer.mydomain.com"
vmDestDataStore		=	"DATASTORE_DESTINATION_NAME"
vmRPool			=	""
#vmRPool		=	"pool1538"
#cat /etc/vmware/hostd/pools.xml


def cleanUp(host=None, path=None, user=userLDAP, passw=passLDAP):
	if host is not None and path is not None and len(path) > 3:
		ssh = paramiko.SSHClient()
		ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		ssh.connect(host, username=user, password=passw, timeout=5)
		stdin, stdout, stderr = ssh.exec_command(' if [ -d "%s" ]; then rm -rf "%s" ;fi ' % (path, path) )
		for i in stderr.readlines():
			print i.strip()
		ssh.close()
		return 0
	else:
		return 1

def registerVM(ssh=None, remote=None, path=None, name=None, rpool=None):
	print "Welcome to registerVM function"
	if ssh is not None and path is not None:
		if rpool is None:
			print "if rpool is None..."
			command = '/bin/grep -i -A1 DSV-HLG /etc/vmware/hostd/pools.xml | grep -i -E -o pool.*[0-9]'
			print "Running remote command %s on host %s" % (command, remote)
			##command = '/bin/grep -i -A1 "DSV-HLG" /etc/vmware/hostd/pools.xml | grep -i pool | cut -d">" -f2 | cut -d"<" -f1'
			stdin, stdout, stderr = ssh.exec_command('ssh root@%s "%s" ' % (remote, command) )
			for i in stdout.readlines():
				print i
				a = str(i)
				rpool = a.strip()
			for i in stderr.readlines():
				print i

		else:
			print "rpool is not none, rpool: %s. Continue..." % rpool

		try:
			r = rpool.find('pool')
			print "rpool: %s" % (rpool)
			print "rpool find pool, r is: %s" % (r)
		except:
			print "No find rpool, got exception!"
			rpool = None
			r = -1
			pass

		if rpool is not None and r is not -1:
			print "rpool is not None and is pool"
			command = 'if [ -e "%s" ]; then vim-cmd solo/registervm "%s" "%s" %s ;fi' % (path, path, name, rpool)
			print "Running remote command %s on host %s" % (command, remote)
			stdin, stdout, stderr = ssh.exec_command('ssh root@%s \'%s\' ' % (remote, command) )
			#stdin, stdout, stderr = ssh.exec_command('ssh root@%s "%s" ' % (remote, command) )
			##stdin, stdout, stderr = ssh.exec_command('ssh root@%s "if [ -e %s ]; then  vim-cmd solo/registervm %s %s %s ;fi" ' % (remote, path, path, name, rpool) )
			for i in stderr.readlines():
				print i.strip()
			for i in stdout.readlines():
				print i.strip()
		else:
			print "rpool is  still None, lets register without resourcepool parameter"
			command = 'if [ -e "%s" ]; then vim-cmd solo/registervm "%s" "%s" ;fi' % (path, path, name)
			print "Running remote command %s on host %s" % (command, remote)
			stdin, stdout, stderr = ssh.exec_command('ssh root@%s \'%s\' ' % (remote, command) )
			#stdin, stdout, stderr = ssh.exec_command('ssh root@%s "%s" ' % (remote, command) )
			##stdin, stdout, stderr = ssh.exec_command('ssh root@%s "if [ -e %s ]; then  vim-cmd solo/registervm %s %s ;fi" ' % (remote, path, path, name) )
			for i in stderr.readlines():
				 print i.strip()
			for i in stdout.readlines():
				print i.strip()
		
		return 0

	return 1


def main():
	####### MAIN #######
	t0 = time.clock()

	if len(sys.argv) == 3:
		vm1Guest	= sys.argv[1]
		vm1DataCenter	= sys.argv[2]
	else:
		print "Usage: ./script guestName dataCenter \n\n dataCenter is ABC, DEF or FGH \n\n" 
		exit()

	print " -->> Begin"

	server = VIServer()
	server.connect(server1, userLDAP, passLDAP)

	print "VMGuest    : %s" % vm1Guest
	print "Datacenter : %s" % vm1DataCenter

	vm1 = server.get_vm_by_name(vm1Guest, vm1DataCenter)

	vm1Path = vm1.get_property('path', from_cache=False)
	vm1Path = vm1Path.split(' ', 1);

	vm1DataStore = vm1Path[0].strip('[]')
	vm1FolderTmp = vm1Path[1].split('/')
	vm1Folder    = vm1FolderTmp[0].strip()

	print "VMDataStore: %s" % vm1DataStore
	print "VMFolder   : %s" % vm1Folder
	print "VMStatus   : %s" % vm1.get_status(basic_status=True)

	if vm1.is_powered_on():
		print "%s is powered ON" % vm1Guest
		vm1.power_off()

	t1 = time.clock()
	while vm1.is_powering_off():
		print "waiting power of..."
		t = time.clock() - t1
		print "%f seconds", t

	print "%s is NOW powered OFF" % vm1Guest

	if vm1.is_powered_off() and vm1DataStore is not None and vm1Folder is not None:
		server.disconnect()
		ssh = paramiko.SSHClient()
		ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		print "Connecting to %s" % splitOrigemHost
		ssh.connect(splitOrigemHost, username=userLDAP, password=passLDAP, timeout=5)
		vm1Path   = '/vmfs/volumes/%s/%s/' % (vm1DataStore, vm1Folder)
		print "Copying files from %s to %s" % (vm1Path, splitDestPath)

		stdin, stdout, stderr = ssh.exec_command('scp -p -r root@%s:"\'%s\'" %s && echo "Scp Done!" && chmod -R 755 %s/"%s"/ ' % (vmOrigemHost, vm1Path, splitDestPath, splitDestPath, vm1Folder) )
		for i in stdout.readlines():
			print i.strip()
		for i in stderr.readlines():
			print i.strip()
			print "We got something on stderr, aborting script. Probably errors on SCP."
			exit()

		stdin1, stdout1, stderr1 = ssh.exec_command('ls -1sSh %s"%s"/' % (splitDestPath, vm1Folder) )
		for i in stdout1.readlines():
			print i.strip()

		stdin2, stdout2, stderr2 = ssh.exec_command('ls -1 %s"%s"/' % (splitDestPath, vm1Folder) )
		filesArray = []
		for i in stdout2.readlines():
			filesArray.append(i.strip())

		ssh.close()

		print "Everything DONE for first copy phase, now get files on other side"
		print "Connecting to %s" % splitDestHost
		ssh.connect(splitDestHost, username=userLDAP, password=passLDAP, timeout=5)
		for i in filesArray:
			print "\nDownloading at %s, from %s. File: %s" % (splitDestHost, splitOrigemHostFr, i)
			stdin, stdout, stderr = ssh.exec_command('aria2c --conditional-get=true --max-concurrent-downloads=16 --max-connection-per-server=16 --split=16 --continue=true --connect-timeout=300 --max-tries=5 --dir="%s%s/" \'http://%s/%s/%s\' && echo "Download OK!"' % (splitDestPath, vm1Folder, splitOrigemHostFr, vm1Folder, i) )
			for j in stdout.readlines():
				print "ARIA2C log: %s" % j.strip()
			for j in stderr.readlines():
				print "ARIA2C stderr log: %s" % j.strip()

		print "Download at %s was OK!" % splitDestHost

		if vmDestDataStore is not None and vm1Folder is not None:
			vm1Path   = '/vmfs/volumes/%s/' % (vmDestDataStore)
			print "Sending files from %s:%s%s/, to %s:%s" % (splitDestHost, splitDestPath, vm1Folder, vmDestHost, vm1Path)
			stdin, stdout, stderr = ssh.exec_command('scp -p -r \'%s%s/\' root@%s:"%s" && echo "Scp Done!" ' % (splitDestPath, vm1Folder, vmDestHost, vm1Path) )
			for i in stderr.readlines():
				print i.strip()

		print "Registering guest on VMWare"
		vm1Path = '/vmfs/volumes/%s/%s/' % (vmDestDataStore, vm1Folder)
		stdin, stdout, stderr = ssh.exec_command('ssh root@%s ls -1 "\'%s\'"*.vmx' % (vmDestHost, vm1Path) )
		vmxArray = []
		for i in stdout.readlines():
			vmxArray.append(i.strip())
		#default guests name are guest01-abc, guest02-def, guest01-fgh , so "name-datacenter"
		#just replace datacenter string
		r = vm1Guest.find('-abc')
		if r == -1:
			regName = '%s-def' % vm1Guest
		else:
			regName = vm1Guest.replace('-abc', '-def')

		if vmRPool:
			print "Using predefined vmRPool: %s" % vmRPool
			print "Registering path %s, name %s, pool %s" % (vmxArray[0], regName, vmRPool)
			r = registerVM(ssh, vmDestHost, vmxArray[0], regName, vmRPool)
		else:
			print "Using automatic vmRPool automatic discover"
			print "Registering path %s, name %s" % (vmxArray[0], regName)
			r = registerVM(ssh, vmDestHost, vmxArray[0], regName, None)

		if r == 0:
			print "Guest is registered!"
		else:
			print "Error registering Guest."

		ssh.close()
	
	print "\nRunning cleanup of folder %s, path %s on %s and %s" % (vm1Folder, splitDestPath, splitOrigemHost, splitDestHost)
	cleanPath = '%s%s/' % (splitDestPath, vm1Folder)
	r = cleanUp(splitOrigemHost, cleanPath)
	r = cleanUp(splitDestHost, cleanPath)
	print "\nTotal running time: %f" % (time.clock() - t0)
	print " -->> Done"



####### START #######
if __name__ == "__main__":
	main()
