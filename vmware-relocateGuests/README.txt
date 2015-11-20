## relocateWindowsGuests

 It basically move VMWARE guests from SRC_CLUSTER to DST_CLUSTER.
 Those should belong to same vcenter.
 It was done for moving Windows guests from SRC_CLUSTER, because they always must stay at DST_CLUSTER. But people can by pass things sometimes :)
 So, let it running and moving things...


 Running as cron job:
	10 * * * * /usr/local/bin/relocateWindowsGuests.pl 2>&1 >>/var/log/relocateWindowsGuests.log
