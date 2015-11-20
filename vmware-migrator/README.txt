## vmware-mig

It was created for moving vmware guests from one geographical location to another.
Because some hugh machines, sometimes MIGRATE function of vcenter fail.
So, it copies machines files from VMWARE Datastore and send them thru internet.
After that register transfered guest on vcenter destination.

You should setup some ssh keys on servers for scp files inside a side.
ARIA2C is used for parallel download of files.
