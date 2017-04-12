#!/usr/bin/env python
import random
import time

SOURCE_PATH="pseudo_source"
TARGET_PATH="/tmp/something"

def main():

    lines = open(SOURCE_PATH, 'r').readlines()

    while True:

        with open(TARGET_PATH, "w+") as tfd:
            tfd.truncate()

        for i in xrange(0, 100):
            with open(TARGET_PATH, "a+") as tfd:
                tfd.write(lines[random.randint(0, len(lines))])

            time.sleep(1)

if __name__ == "__main__":
    main()
