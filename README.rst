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

Update and upgrade packages and run raspi-config::

  apt-get update
  apt-get upgrade -y
  apt-get dist-upgrade -y
  apt-get install raspi-config
  raspi-config

In raspi-config change:

  * 2 Hostname
  * 4 Localization > I2 Change Timezone
  * 7 Advanced Options > A1 Expand Filesystem
  * <Finish> and reboot

After reboot continue installing and cleanup::
  
  apt-get install \
    make git vim-nox logrotate \
    python python-yaml python-flask python-socketio python-pip
  apt-get autoclean
  apt-get clean

Then create wtty filesystem::

  mkdir /srv/wtty

Edit `vim /etc/fstab`, adding the following to make it available on boot::

  /dev/sda1 /srv/wtty ext4 errors=remount-ro,noatime,nodiratime,commit=120 0 1
  
Mount it:

  mount /srv/wtty

Install wtty::

  mkdir -p $HOME/git
  cd $HOME/git
  git clone https://github.com/safl/wtty.git
  cd wtty
  make install

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
