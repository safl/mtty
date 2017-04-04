====
mtty
====

Tool to monitor output from tty.

Install and Usage
=================

Modify init-script(mtty) and set DEVICES and LOG_ROOT.

Install::

  cp mtty /dev/init.d/
  cp mtty.sh /usr/bin/
  update-rc.d mtty defaults

Now start it with::

  service mtty start

And stop it with::

  service mtty stop

Log-rotation
------------

Create file "/etc/logrotate.d/mtty" containing::

  /var/www/html/*.log {
    daily
    copytruncate
    rotate 7
    missingok
  }

Usage
-----

Download the output via web::

  wget "http://host/ttyUSB0.log"

Or tail it over ssh::

  ssh root@host "tail -f /var/www/html/ttyUSB0.log"

Raspberry PI setup
==================

Download "minibian" distro (https://minibianpi.wordpress.com/) for Raspberry PI.
Flash it::

  sudo dd if=2016-03-12-jessie-minibian.img of=/dev/sdb

Log into the device root/raspberry.

Change password::

  passwd

Install packages::

  apt-get upgrade -y
  apt-get dist-upgrade -y
  apt-get install vim-nox lighttpd raspi-config logrotate
  apt-get clean

Run raspi-config, change hostname and resize filesystem, then reboot.

Configure::

  lighttpd-enable-mod dir-listing
  service lighttpd restart
