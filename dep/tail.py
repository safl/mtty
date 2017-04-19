#!/usr/bin/env python
import time
import sys
import os

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

def main():
    for char in tailf("/tmp/something"):
        print(char)

if __name__ == "__main__":
    main()
