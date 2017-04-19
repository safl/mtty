#!/usr/bin/env python
from __future__ import print_function

ANSI_FULL_RESET = 0
ANSI_INTENSITY_INCREASED = 1
ANSI_INTENSITY_REDUCED = 2
ANSI_INTENSITY_NORMAL = 22
ANSI_STYLE_ITALIC = 3
ANSI_STYLE_NORMAL = 23
ANSI_BLINK_SLOW = 5
ANSI_BLINK_FAST = 6
ANSI_BLINK_OFF = 25
ANSI_UNDERLINE_ON = 4
ANSI_UNDERLINE_OFF = 24
ANSI_CROSSED_OUT_ON = 9
ANSI_CROSSED_OUT_OFF = 29
ANSI_VISIBILITY_ON = 28
ANSI_VISIBILITY_OFF = 8
ANSI_FOREGROUND_CUSTOM_MIN = 30
ANSI_FOREGROUND_CUSTOM_MAX = 37
ANSI_FOREGROUND_256 = 38
ANSI_FOREGROUND_DEFAULT = 39
ANSI_BACKGROUND_CUSTOM_MIN = 40
ANSI_BACKGROUND_CUSTOM_MAX = 47
ANSI_BACKGROUND_256 = 48
ANSI_BACKGROUND_DEFAULT = 49
ANSI_NEGATIVE_ON = 7
ANSI_NEGATIVE_OFF = 27

ANSI_FG_GREEN
ANSI_FG_GREEN
CODES = {
    "0": lambda x: "",      # off: everything reset
    "1": lambda x: "<b>",        # on: bold
    "2": lambda x: "<i>",        # on: italics
    "3": lambda x: "<u>",        # on: underline
    "4": lambda x: "<s>",        # on: strikethrough
    lambda x: "</span>",    # Reset
    lambda x: "</span>",    # Reset
    lambda x: "</span>",    # Reset
    lambda x: "</span>",    # Reset
    lambda x: "</span>",    # Reset
    lambda x: "</span>",    # Reset
    lambda x: "</span>",    # Reset
}

class AnsiState(object):

    def __init__(self):
        pass



ASCII_CODE_ESC = chr(27)
ASCII_CODE_BGN = '['
ASCII_CODE_END = 'm'

def handle_code(code):

    if 

def ansi2html(text):

    html = []

    nchars = len(text)
    cur = 0
    while cur < nchars:

        if text[cur] is ASCII_CODE_ESC and text[cur + 1] is ASCII_CODE_BGN:

            if text[cur + 3] is ASCII_CODE_END:
                code = text[cur + 2]
                cur += 4
                html.append()
                continue
            elif text[cur + 4] is ASCII_CODE_END:
                code = text[cur + 2 : cur + 4]
                cur += 5
                continue
            else:
                print("PSR ERR")

        html.append(text[cur])
        cur += 1

    return "".join(html)

def main():

    with open("/tmp/wtty/output/ttyUSB0.log") as tgt:

        count = 0
        for line in tgt.readlines():
            if "000d:" not in line:
                continue

            count = count + 1

            if count > 10:
                break
            print(ansi2html(line))

if __name__ == "__main__":
    main()
