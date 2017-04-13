#!/usr/bin/env python
import inspect
from flask import Flask, render_template, session, request
from flask import send_from_directory
import flask_socketio as fsio
import select
import glob
import time
import sys
import os

# Set this variable to "threading", "eventlet" or "gevent" to test the
# different async modes, or leave it set to None for the application to choose
# the best option based on installed packages.
#ASYNC_MODE = None
#ASYNC_MODE = "eventlet"
ASYNC_MODE = "gevent"

APP = Flask(__name__)
APP.config['SECRET_KEY'] = 'secret!'
SIO = fsio.SocketIO(APP, async_mode=ASYNC_MODE)

TTYS = ["ttyUSB0", "ttyUSB1", "ttyUSB2", "ttyUSB3"]
#TTYS = []
WORKERS = []

def tailf(fpath):
    """Generate stream of bytes from files"""

    POLL_EXISTS = 0.5
    POLL_CONTENT = 0.1

    while True:
        try:
            with open(fpath, 'r') as fin:
                read = 0
                while read <= os.stat(fpath).st_size:
                    char = fin.read()

                    if char:
                        read += 1
                        yield char

                    time.sleep(POLL_CONTENT)
        except OSError:
            time.sleep(POLL_EXISTS)
        except IOError:
            time.sleep(POLL_EXISTS)

def background_thread(tty):
    """Example of how to send server generated events to clients."""

    for chunk in tailf("/tmp/%s.log" % tty):
        payload = {
            'data': chunk
        }
        SIO.emit('wtty_out', payload, room=tty, broadcast=True)

@APP.route('/wtty<string:dev>')
def index(dev):
    "Serve the client-side application."""

    tty = "tty" + dev

    return render_template(
        'wtty.html',
        async_mode=SIO.async_mode,
        tty=tty
    )

@APP.route('/', defaults={"path": None})
@APP.route('/<path:path>')
def logs(path):
    """Serve the log files in their raw form"""

    logs_root = os.sep.join(["", "tmp"])

    if path is None:
        listing = {}
        
        for tty in TTYS:
            pattern = os.sep.join([logs_root, "%s*.log" % tty])
            paths = glob.glob(pattern)
            stats = [os.stat(path) for path in paths]
            listing[tty] = [(
                os.path.basename(fname),
                stat.st_size,
                time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(stat.st_mtime))
                ) for fname, stat in zip(paths, stats)
            ]
            listing[tty].sort()

        return render_template(
            'index.html',
            ttys=TTYS,
            listing=listing,
            strftime=time.strftime
        )

    abs_path = os.sep.join([logs_root, os.path.basename(path)])
    if not os.path.exists(abs_path):
        return "path(%s) DOES NOT EXIST" % path

    return send_from_directory(logs_root, os.path.basename(path))

@SIO.on('wtty_dev')
def wtty_dev(message):

    tty = message["data"]

    print("Got: %s" % str(message))
    fsio.join_room(tty)

@SIO.on('wtty_in')
def wtty_in(message):
    print(inspect.currentframe().f_code.co_name)

    print("Got: %s" % str(message))

    session['receive_count'] = session.get('receive_count', 0) + 1

    payload = {
        'data': "Got your message",
        'count': session['receive_count']
    }
    fsio.emit('wtty_info', payload)

@SIO.on('connect')
def wtty_connect():
    print(inspect.currentframe().f_code.co_name)

    payload = {
        'data': 'Connected',
        'count': 0
    }
    fsio.emit('wtty_info', payload)

    print("Client connected")

@SIO.on('disconnect')
def wtty_disconnect():
    print(inspect.currentframe().f_code.co_name)

    print('Client disconnected', request.sid)

@SIO.on('ping')
def ping_pong():
    print(inspect.currentframe().f_code.co_name)

    fsio.emit('pong')

def main():

    for tty in TTYS:
        WORKERS.append(
            SIO.start_background_task(target=background_thread, tty=tty)
        )

    SIO.run(APP, debug=True)

if __name__ == '__main__':
    main()
