## dnsmgmt.py
Designed for providing EC2 hosts auto-registration on DNS zone that all belongs.
EC2 hosts must have role access to route53, of course, using credentials you can run it from anywhere.

You can run it without parameters so it will registry the current machine on DNS.
Also some parameters are supported:

	-a/--add   	--> ADD action
	-r/--remove  	--> REMOVE action
	-n/--name 	--> HOSTNAME to add
	-i/--ip   	--> IPADDR to add
