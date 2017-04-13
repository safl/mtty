#!/usr/bin/env python
import random
import time

SOURCE_PATH="pseudo_source"
TARGET_PATHS=[
    "/tmp/ttyUSB0.log",
    "/tmp/ttyUSB1.log",
    "/tmp/ttyUSB2.log",
    "/tmp/ttyUSB3.log"
]

def main():

    lines = []
    for line in open(SOURCE_PATH, 'r').readlines():
        if not line.strip():
            continue

        n = 80
        for sline in (line[i:i+n] for i in xrange(0, len(line), n)):
            lines.append(sline)
        #lines.append(line)

    while True:

        for tpath in TARGET_PATHS:
            with open(tpath, "w+") as tfd:
                tfd.truncate()

        for i in xrange(0, 1000):
            for tpath in TARGET_PATHS:
                with open(tpath, "a+") as tfd:
                    tfd.write(lines[random.randint(0, len(lines) - 1)])

            time.sleep(0.1)

if __name__ == "__main__":
    main()
