## watchdog-fs ##

Keep watching a folder for modifications (write).

I'm currently running it under "daemontools" (supervise), so it keeps process always up (it makes things a lit bit different than the SH here).
Also doing logging using "multilog" under daemontools.

Requires "python-inotify".


/var/service/sample
	run
/var/service/sample/log
	run
