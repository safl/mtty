#!/usr/bin/env python
# -*- coding: ascii -*-
from __future__ import print_function
import argparse
import logging
import signal
import yaml
import time
import os
from daemon import DaemonContext
from daemon.pidfile import PIDLockFile

logging.basicConfig(
    format="%(asctime)s-%(filename)s-%(funcName)s: %(message)s",
    level=logging.ERROR
)

NAME="wtty"
VERSION = "0.1"
DESCR = "wtty io"
DESCR_LONG = "wtty io"
AUTHOR = "Simon A. F. Lund"
AUTHOR_EMAIL = "safl@safl.dk"
URL="https://github.com/safl/mtty"

CFG_NAME="wtty.conf"
CFG_SEARCH=["$HOME/.wtty", "/usr/local/etc", "/etc"]

def expand_path(path):
    """Expand user and environment variables in path and guess absolute path"""

    if path is None:
        return None

    return os.path.abspath(os.path.expandvars(os.path.expanduser(path)))

def load_conf(cpath):
    """Load configuration from file"""

    spaths = CFG_SEARCH
    if cpath is not None:
        spaths = [cpath]

    for spath in spaths:
        cpath = expand_path(os.sep.join([spath, CFG_NAME]))

        if os.path.exists(cpath):
            with open(cpath) as yfd:
                return yaml.load(yfd)

    return None

def daemonify(descr, action):
    """Turn the given 'action' into a UNIX-like daemon with CLI"""

    prsr = argparse.ArgumentParser(description=descr)   # CLI
    prsr.add_argument(
        "--conf",
        type=argparse.FileType('r'),
    )
    prsr.add_argument("--pid", type=str, required=True)
    prsr.add_argument("--log", type=str, required=True)
    args = prsr.parse_args()

    conf = load_conf(args.conf)                         # CONF
    if conf is None:
        print("# FAILED: Loading args.conf(%s)" % args.conf)
        return

    conf["pid"] = expand_path(args.pid)
    conf["log"] = expand_path(args.log)

    if os.path.exists(conf["pid"]):                     # FIX STALE PID
        try:
            pid = int(open(conf["pid"]).read())
            os.kill(pid, 0)
            logging.critical("??? Already running pid:%d path: %s" % (
                pid, conf["pid"])
            )
            #exit(1)
        except OSError:
            os.remove(conf["pid"])

    state = {"keep_running": True}                      # STATE

    def daemon_terminate(signum, frame):
        if signum in [signal.SIGHUP, signal.SIGTERM]:
            state["keep_running"] = False
                                                        # SPAWN!
    with open(conf["log"], "a+") as log, \
        DaemonContext(
            pidfile=PIDLockFile(conf["pid"]),
            stdout=log, stderr=log,
            signal_map = {
                signal.SIGHUP: daemon_terminate,
                signal.SIGTERM: daemon_terminate
            }
        ) as ctx:
            action(conf, state)
