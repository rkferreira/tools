
This was made with the intent to scan all VCENTER and return a list of all VMs Guest and some predetermined infos.
 Properties I care about on this are:
 - VM name
 - VM stat
 - VM GuestID (O.S.)
 - VM number of vCPUs
 - VM total ram mem
 - VM num of vdks
 - VM total size of all VDKs
 - VM immediate parent Resource Pool name

 You can extend:
 - https://www.vmware.com/support/developer/viperltoolkit/
 - https://www.vmware.com/support/developer/vc-sdk/visdk25pubs/ReferenceGuide/left-pane.html


Output example:

NAME,STATE,GUESTID,CPUS,MEMSIZE_MB,NUMVDKS,TOTALVDKSSIZE_MB,RPOOL
fin-vm01,poweredOn,win2000ServGuest,1,512,1,34736.5322265625,Financial
ldap01,poweredOn,rhel5Guest,1,512,1,10240,Infrastructure
ActiveDirectory01,poweredOn,win2000ServGuest,1,512,1,10240,Windows Infrastructure



*** Added vmInventoryList.pl, same base as above. But more fields and options.
