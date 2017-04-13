#!/usr/bin/env python
import argparse
import lockfile
import daemon
import time
import os

def main():
	"""..."""

	while True:
	    print("HEJ")
	    time.sleep(1)

def daemonize(args):
    """Daemonize the main entry"""

    with open(args.log, "w+") as output:

        with daemon.DaemonContext(
            pidfile=lockfile.FileLock(args.pid),
            working_directory="/tmp",
            stdout=output,
            stderr=output) as ctx:
            main()

def expand_path(path):
    """Expand variables and guess absolute path"""

    return os.path.abspath(os.path.expandvars(os.path.expanduser(path)))

if __name__ == "__main__":
    PRSR = argparse.ArgumentParser(description='wtty-io daemon')
    PRSR.add_argument(
        "--cfg",
        type=argparse.FileType('r'),
        required=True
    )
    args = PRSR.parse_args()

    daemonize(args)
