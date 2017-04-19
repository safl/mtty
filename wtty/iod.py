#!/usr/bin/env python
# -*- coding: ascii -*-
from subprocess import Popen, PIPE
import threading
import select
import logging
import fcntl
import time
import sys
import os

TTY_OPTS="-icrnl -onlcr -imaxbel -opost -isig -icanon -echo line 0 kill ^H min 100 time 2 brkint 115200"
READERS = []
WRITERS = []
SELECT_TO = 1

def tty_set_opts(dev, opts):
    """Set tty options"""

    cmd = ["stty", "-F", dev] + opts.split(" ")

    prcs = Popen(cmd, stdout=PIPE,stderr=PIPE)
    out, err = prcs.communicate()

    if out:
        logging.info(out)

    if err:
        logging.error(err)

    return prcs.returncode

class TTYWorker(threading.Thread):

    def __init__(self, dev, root):
        threading.Thread.__init__(self)

        self.tty = os.path.basename(dev)
        self.dev = dev
        self.root = root
        self.keep_running = True

    def stop(self):
        self.keep_running = False

    def run(self):
        raise Exception("Not implemented")

class TTYReader(TTYWorker):
    """Reads tty output to file"""

    def run(self):

        tty_out_path = os.sep.join([self.root, "%s.log" % self.tty])
        logging.info("tty_out_path(%s)" % tty_out_path)

        while self.keep_running:

            err = not os.path.exists(self.dev)
            if err:
                logging.error("dev(%s) does not exist" % self.dev)
                time.sleep(1)
                continue

            err = not os.path.exists(self.root)
            if err:
                logging.error("root(%s) does not exist" % self.root)
                time.sleep(1)
                continue

            err = tty_set_opts(self.dev, TTY_OPTS)
            if err:
                logging.error("failed stty err(%d)", err)
                time.sleep(1)
                continue

            try:

                with open(self.dev, "rb", 0) as dev_r, \
                     open(tty_out_path, "ab", 0) as tty_out:

                    while self.keep_running and \
                        os.fstat(dev_r.fileno()).st_nlink and \
                        os.fstat(tty_out.fileno()).st_nlink:

                        ready, _, _ = select.select(
                            [tty_out.fileno()], [], [], SELECT_TO
                        )

                        if not ready:
                            continue

                        payload = dev_r.read(1)
                        if payload is None:
                            break

                        tty_out.write(payload)
            except:
                logging.error("error(%s)" % str(sys.exc_info()))

class TTYWriter(TTYWorker):
    """Write commands to tty"""

    def run(self):

        tty_in_path = os.sep.join([self.root, "%s.in" % self.tty])
        logging.info("tty_in(%s)" % tty_in_path)

        while self.keep_running:

            err = not os.path.exists(self.dev)
            if err:
                logging.error("dev(%s) does not exist" % self.dev)
                time.sleep(1)
                continue

            err = not os.path.exists(self.root)
            if err:
                logging.error("root(%s) does not exist" % self.root)
                time.sleep(1)
                continue

            err = not os.path.exists(tty_in_path)
            if err:
                logging.error("tty_in_path(%s) does not exist" % tty_in_path)
                time.sleep(1)
                continue

            err = tty_set_opts(self.dev, TTY_OPTS)
            if err:
                logging.error("failed stty err(%d)", err)
                time.sleep(1)
                continue

            try:
                with open(self.dev, "a", 0) as dev_w, \
                     open(tty_in_path, "r", 0) as tty_in:

                    tty_in.seek(0, 2)

                    while self.keep_running and \
                        os.fstat(dev_w.fileno()).st_nlink and \
                        os.fstat(tty_in.fileno()).st_nlink:

                        line = tty_in.readline()

                        if not line:
                            time.sleep(0.1)
                            continue

                        dev_w.write(line.strip())
                        time.sleep(0.1)
                        dev_w.write('\r')
            except:
                logging.error("error(%s)" % str(sys.exc_info()))

def main(cfg, state):
    """Entry point for wtty-iod"""

    logging.info("Creating workers")
    for tty in cfg["devices"]:
        READERS.append(TTYReader(tty, cfg["roots"]["reader"]))
        WRITERS.append(TTYWriter(tty, cfg["roots"]["writer"]))

    logging.info("Starting workers")
    for worker in READERS + WRITERS:
        worker.start()

    while (state["keep_running"]):
        time.sleep(0.1)

    logging.info("Stopping and joining workers")
    for worker in WRITERS + READERS:
        worker.stop()
        worker.join()

    logging.info("DONE")
