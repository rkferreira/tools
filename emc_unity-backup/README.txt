## DELLEMC Unity backup ##

Requires "UnisphereCLI-Linux".

Schedule a crontab:
	1 14 * * 1,2,3,4,5,6,7 /usr/local/bin/unity01Bkp.sh >/dev/null 2>&1
