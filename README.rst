======
 wtty
======

Tool to monitor output from ttyUSB

wtty on Raspberry PI setup
==========================

Download "minibian" distro (https://minibianpi.wordpress.com/) for Raspberry PI.
Flash it::

  sudo dd if=2016-03-12-jessie-minibian.img of=/dev/sdb

Log into the device root/raspberry.

Change password::

  passwd

Install packages::

  apt-get update
  apt-get upgrade -y
  apt-get dist-upgrade -y
  apt-get autoclean
  apt-get clean
  apt-get install raspi-config git vim-nox logrotate make
  apt-get install python python-yaml python-flask python-socketio python-pip
  apt-get autoclean
  apt-get clean

Run raspi-config, change hostname, timezone and resize filesystem.

Install wtty::

  mkdir -p $HOME/git
  cd $HOME/git
  git clone https://github.com/safl/mtty.git
  cd mtty
  make install

Then create wtty filesystem::

  mkdir /srv/wtty

Edit `vim /etc/fstab`, adding the following to make it available on boot::

  /dev/sda1 /srv/wtty ext4 errors=remount-ro,noatime,nodiratime,commit=120 0 1

Reboot to check that everything starts up correctly on boot.

Log-rotation
------------

Create file "/etc/logrotate.d/wtty" containing::

  /srv/wtty/output/*.log {
    daily
    copytruncate
    rotate 7
    missingok
  }

  /srv/wtty/input/*.log {
    daily
    copytruncate
    rotate 7
    missingok
  }

  /srv/wtty/*.log {
    daily
    copytruncate
    rotate 7
    missingok
  }


OLD
===

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

Usage
-----

Download the output via web::

  wget "http://host/ttyUSB0.log"

Or tail it over ssh::

  ssh root@host "tail -f /var/www/html/ttyUSB0.log"

Provide into via screen::

  screen /dev/ttyUSB0 115200,cs8,inclr
