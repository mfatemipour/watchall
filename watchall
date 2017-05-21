#!/usr/bin/python

"""
Mohammad Fatemipopur
m.fatemipour@gmail.com
watchall is a tool same is linux watch with scrolling capability.
"""

import curses

import time
import argparse
import subprocess
from threading import Thread, Lock
import signal

class Watchall(object):
    ESC_KEY = 27

    def __init__(self, stdscr, args):
        self.thread = Thread(target=self.update_lines)
        self.stdscr = stdscr
        self.active = True
        self.interval = args.interval
        self.differences = args.differences
        self.max_line_scroll = args.max_line_scroll
        self.pre_output_lines = []
        self.cur_output_lines = []
        self.mutex = Lock()
        self.first_showing_line = 0
        self.cursor_position = [0, 0]



        self.cmd = args.Command[0]
        for item in args.Args:
            self.cmd += ' ' + item

    def run(self):
        self.thread.start()
        try:
            while self.active is True:
                c = self.stdscr.getch()
                if c == curses.KEY_UP:
                    self.first_showing_line =  max (0, self.first_showing_line - 1)
                    self.refresh_screen(update_pad=False)
                elif c == curses.KEY_DOWN:
                    self.first_showing_line = min(self.cursor_position[0], self.first_showing_line + 1)
                    self.refresh_screen(update_pad=False)
                elif c == curses.KEY_RESIZE:
                    self.refresh_screen(update_pad=False)
                elif c == self.ESC_KEY:
                    self.active = False
                    self.thread.join()
                    break
        except:
            pass


    def update_lines(self):
        global run
        while self.active is True:
            self.pre_output_lines = self.cur_output_lines
            ret = self.execute_cmd()
            self.cur_output_lines = ret
            self.refresh_screen(update_pad=True)
            for i in range(1, self.interval*4, 1):
                if self.active is False:
                    break
                time.sleep(0.25)

    def execute_cmd(self):
        process = subprocess.Popen(self.cmd , shell=True, stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT,
                                   universal_newlines=True)

        output, stderr = process.communicate()
        retcode = process.poll()
        if retcode:
            # stop.set()
            print('ERROR')
            raise subprocess.CalledProcessError(retcode, self.cmd, output=output[0])

        return output.splitlines()

    def refresh_screen(self, update_pad = False):
        try:
            self.mutex.acquire()
            y, x = self.stdscr.getmaxyx()

            if update_pad is True:
                self.pad = curses.newpad(self.max_line_scroll, x)

                for i in range(0, len(self.cur_output_lines)):
                    line = self.cur_output_lines[i]
                    for j in range(0, len(line)):
                        if self.differences and len(self.pre_output_lines) > i and len(self.pre_output_lines[i]) > j \
                                and self.pre_output_lines[i][j] != self.cur_output_lines[i][j]:
                            self.pad.addch(self.cur_output_lines[i][j], curses.A_REVERSE)
                        else:
                            self.pad.addch(self.cur_output_lines[i][j])
                    self.pad.addch('\n')

                self.cursor_position = self.pad.getyx()
            try:
                stdscr.addstr(0, 0, "Every {}s: {}, first line: {}/{}".format(self.interval, self.cmd,
                              self.first_showing_line, self.cursor_position[0]))
                stdscr.refresh()
                self.pad.refresh(self.first_showing_line, 0, 1, 0, y-2, x)

            except Exception as e:
                print e.message
        finally:
            self.mutex.release()

    def stop(self):
        self.active = False
        self.thread.join()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-d', '--differences', action='store_true', help='highlight differences')
    parser.add_argument('-n', '--interval', type=int, help='interval', required=False, default=2)
    parser.add_argument('-m', '--max_line_scroll', type=int, help='max_line_scroll', required=False, default=200)
    parser.add_argument('Command', metavar='Command', type=str, nargs=1, help='Command')
    parser.add_argument('Args', metavar='Arguments', type=str, nargs='*', help='Command arguments')

    # --------------------------------- Global variables ------------------------
    args = parser.parse_args()

    stdscr = curses.initscr()
    curses.noecho(); curses.cbreak(); curses.curs_set(0); stdscr.keypad(1)
    w = Watchall(stdscr, args)

    def handler(signum, frame):
        w.stop()
    signal.signal(signal.SIGINT, handler)

    try:
        w.run()
    finally:
        curses.nocbreak(); stdscr.keypad(0); curses.curs_set(1); curses.echo(); curses.endwin()