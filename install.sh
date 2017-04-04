Install
=======

Modify init-script(mtty) and set DEVICES, to contain the tty devices to monitor.

Install start init-script(mtty) and monitoring script(mtty.sh):

	cp mtty /dev/init.d/
	cp mtty.sh /usr/bin/
	update-rc.d mtty defaults

Now start it with:

	service mtty start

And stop it with:

	service mtty stop
