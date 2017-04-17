#! /bin/sh
# /etc/init.d/wtty.app

### BEGIN INIT INFO
# Provides:          wtty-app
# Required-Start:    $remote_fs $syslog
# Required-Stop:     $remote_fs $syslog
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: wtty IO daemon 
# Description:       tty <--> file
### END INIT INFO

NAME="wtty-appd"
PID="/tmp/$NAME.pid"
LOG="/tmp/$NAME.log"

case "$1" in
  start)
    echo "# Starting $NAME"
    wtty-appd --pid $PID --log $LOG
    ;;
  stop)
    echo "# Stopping $NAME"
    kill $(cat $PID)
    ;;
  *)
    echo "Usage: /etc/init.d/wtty-app {start|stop|restart}"
    exit 1
    ;;
esac

exit 0
