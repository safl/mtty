#!/usr/bin/env python
import inspect
from flask import Flask, render_template, session, request
from flask import send_from_directory
import flask_socketio as fsio
import logging
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
APP.config["SERVER_HOST"] = "0.0.0.0"
APP.config["SERVER_PORT"] = 80
SIO = fsio.SocketIO(APP, async_mode=ASYNC_MODE)

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

def background_thread(dev):
    """Example of how to send server generated events to clients."""

    tty_name = os.path.basename(dev)
    tty_out = os.sep.join([
        APP.config["wtty"]["roots"]["reader"], "%s.log" % tty_name
    ])

    for chunk in tailf(tty_out):
        payload = {'data': chunk}

        SIO.emit('wtty_out', payload, room=tty_name, broadcast=True)

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

    if path is None:
        listing = {}

        tty_names = [
            os.path.basename(dev) for dev in APP.config["wtty"]["devices"]
        ]

        for tty_name in tty_names:
            pattern = os.sep.join([
                APP.config["wtty"]["roots"]["reader"], "%s.*" % tty_name
            ])
            paths = glob.glob(pattern)
            stats = [os.stat(path) for path in paths]
            listing[tty_name] = [(
                os.path.basename(fname),
                stat.st_size,
                time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(stat.st_mtime))
                ) for fname, stat in zip(paths, stats)
            ]
            listing[tty_name].sort()

        return render_template(
            'index.html',
            ttys=tty_names,
            listing=listing,
            strftime=time.strftime
        )

    fname = os.path.basename(path)
    abs_path = os.sep.join([APP.config["wtty"]["roots"]["reader"], fname])
    if not os.path.exists(abs_path):
        return "path(%s) DOES NOT EXIST" % path

    return send_from_directory(APP.config["wtty"]["roots"]["reader"], fname)

@SIO.on('wtty_dev')
def wtty_dev(message):

    tty = message["data"]

    logging.info("Got: %s", str(message))
    fsio.join_room(tty)

@SIO.on('wtty_in')
def wtty_in(message):

    tty_name = message["tty_name"]  # Write to tty_in
    tty_outp = os.sep.join([
        APP.config["wtty"]["roots"]["writer"], "%s.in" % tty_name
    ])

    with open(tty_outp, "a") as tty_outf:
        tty_outf.write("%s\n" % message["data"])

    session['receive_count'] = session.get('receive_count', 0) + 1

    payload = {
        'data': "Got your message",
        'count': session['receive_count']
    }
    fsio.emit('wtty_info', payload)

@SIO.on('connect')
def wtty_connect():

    payload = {
        'data': 'Connected',
        'count': 0
    }
    fsio.emit('wtty_info', payload)

    logging.info("Client connected")

@SIO.on('disconnect')
def wtty_disconnect():

    logging.info('Client disconnected request.sid(%s)', str(request.sid))

@SIO.on('ping')
def ping_pong():

    fsio.emit('pong')

def main(cfg, state):

    logging.critical("Starting...")

    APP.config["wtty"] = cfg

    for dev in APP.config["wtty"]["devices"]:
        WORKERS.append(
            SIO.start_background_task(target=background_thread, dev=dev)
        )

    SIO.run(
        APP,
        debug=True,
        host=APP.config.get("SERVER_HOST"),
        port=APP.config.get("SERVER_PORT")
    )

    logging.critical("Stopped.")
