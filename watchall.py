#!/usr/bin/python

"""
Mohammad Fatemipopur
m.fatemipour@gmail.com
watchall is a tool same is linux watch with scrolling capability.
"""

import curses

import sys
import random
import time
import argparse
import subprocess
from threading import Thread, Lock
import signal
from mercurial.transaction import active

run = True




class Watchall(object):
    # DOWN = 1
    # UP = -1
    # SPACE_KEY = 32
    ESC_KEY = 27

    def __init__(self, stdscr, args):
        self.thread = Thread(target=self.update_lines)
        self.stdscr = stdscr
        self.active = True
        self.interval = args.interval
        self.differences = args.differences
        self.pre_output_lines = []
        self.cur_output_lines = []
        self.mutex = Lock()

        self.cmd = args.Command[0]
        for item in args.Args:
            self.cmd += ' ' + item

    def run(self):
        self.thread.start()
        try:
            while self.active is True:
                # self.displayScreen()
                # # get user command
                # c = self.screen.getch()
                # if c == curses.KEY_UP:
                #     self.updown(self.UP)
                # elif c == curses.KEY_DOWN:
                #     self.updown(self.DOWN)
                # elif c == self.SPACE_KEY:
                #     self.markLine()
                # elif c == self.ESC_KEY:
                #     self.active = False
                #     self.thread.join()
                #     break
                # self.displayScreen()
                # get user command
                c = self.stdscr.getch()
                if c == self.ESC_KEY:
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
        # print('retcode: {}'.format(retcode))
        if retcode:
            # stop.set()
            print('ERROR')
            raise subprocess.CalledProcessError(retcode, self.cmd, output=output[0])

        return output.splitlines()

    def refresh_screen(self, update_pad = False):
        try:
            self.mutex.acquire()

            if update_pad is True:
                y, x = self.stdscr.getmaxyx()
                self.pad = curses.newpad(y, x)

                for i in range(0, len(self.cur_output_lines)):
                    line = self.cur_output_lines[i]
                    for j in range(0, len(line)):
                        if self.differences and len(self.pre_output_lines) > i and len(self.pre_output_lines[i]) > j \
                                and self.pre_output_lines[i][j] != self.cur_output_lines[i][j]:
                            self.pad.addstr(self.cur_output_lines[i][j], curses.A_REVERSE)
                        else:
                            self.pad.addstr(self.cur_output_lines[i][j])
                    self.pad.addstr('\n')

            self.pad.refresh(0, 0, 0, 0, y, x)
        finally:
            self.mutex.release()

    # def markLine(self):
    #     linenum = self.topLineNum + self.highlightLineNum
    #     if linenum in self.markedLineNums:
    #         self.markedLineNums.remove(linenum)
    #     else:
    #         self.markedLineNums.append(linenum)
    #
    # def getOutputLines(self):
    #     ### !!!
    #     ### This is where you would write a function to parse lines into rows
    #     ### and columns. For this demo, I'll just create a bunch of random ints
    #     ### !!!
    #     self.outputLines = [x.strip() for x in open('lines.txt').readlines()]
    #     self.nOutputLines = len(self.outputLines)
    #
    # def displayScreen(self):
    #     # clear screen
    #     self.screen.erase()
    #
    #     # now paint the rows
    #     top = self.topLineNum
    #     bottom = self.topLineNum + curses.LINES
    #     for (index, line,) in enumerate(self.outputLines[top:bottom]):
    #         linenum = self.topLineNum + index
    #         if linenum in self.markedLineNums:
    #             prefix = self.PREFIX_SELECTED
    #         else:
    #             prefix = self.PREFIX_DESELECTED
    #
    #         line = '%s %s' % (prefix, line,)
    #
    #         # highlight current line
    #         if index != self.highlightLineNum:
    #             self.screen.addstr(index, 0, line)
    #         else:
    #             self.screen.addstr(index, 0, line, curses.A_BOLD)
    #     self.screen.refresh()
    #
    # # move highlight up/down one line
    # def updown(self, increment):
    #     nextLineNum = self.highlightLineNum + increment
    #
    #     # paging
    #     if increment == self.UP and self.highlightLineNum == 0 and self.topLineNum != 0:
    #         self.topLineNum += self.UP
    #         return
    #     elif increment == self.DOWN and nextLineNum == curses.LINES and (
    #         self.topLineNum + curses.LINES) != self.nOutputLines:
    #         self.topLineNum += self.DOWN
    #         return
    #
    #     # scroll highlight line
    #     if increment == self.UP and (self.topLineNum != 0 or self.highlightLineNum != 0):
    #         self.highlightLineNum = nextLineNum
    #     elif increment == self.DOWN and (
    #             self.topLineNum + self.highlightLineNum + 1) != self.nOutputLines and self.highlightLineNum != curses.LINES:
    #         self.highlightLineNum = nextLineNum
    #

    def stop(self):
        self.active = False
        self.thread.join()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-d', '--differences', action='store_true', help='highlight differences')
    parser.add_argument('-n', '--interval', type=int, help='interval', required=False, default=2)
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


        #
        #
        # import curses
        # import sys
        # import random
        # import locale
        # import threading
        # import subprocess
        # import time
        # locale.setlocale(locale.LC_ALL,"")
        #
        # class UnixWatchCommand:
        #     DOWN = 1
        #     UP = -1
        #     SPACE_KEY = 32
        #     ESC_KEY = 27
        #
        #     PREFIX_SELECTED = '-'
        #     PREFIX_DESELECTED = ''
        #
        #     outputLines = []
        #     screen = None
        #
        #     def __init__(self, command):
        #         self.stop = threading.Event()
        #         self.timer=threading.Thread(target=self.display)
        #         self.command = ' '.join(command)
        #         self.screen = curses.initscr()
        #         curses.noecho()
        #         curses.cbreak()
        #         self.screen.keypad(1)
        #         self.screen.border(0)
        #         self.topLineNum = 0
        #         self.highlightLineNum = 0
        #         self.markedLineNums = []
        #         self.getOutputLines()
        #         self.timer.start()
        #         self.run()
        #         self.timer.join()
        #
        #     def display(self):
        #         while not self.stop.is_set():
        #             try:
        #                 self.displayScreen()
        #                 time.sleep(1)
        #             except:
        #                 break
        #
        #     def run(self):
        #         while True:
        #             try:
        #                 self.displayScreen()
        #                 # get user command
        #                 c = self.screen.getch()
        #                 if c == curses.KEY_UP:
        #                     self.updown(self.UP)
        #                 elif c == curses.KEY_DOWN:
        #                     self.updown(self.DOWN)
        #                 elif c == self.SPACE_KEY:
        #                     self.markLine()
        #                 elif c == self.ESC_KEY:
        #                     self.stop.set()
        #                     break
        #             except:
        #                 self.stop.set()
        #                 break
        #
        #
        #     def markLine(self):
        #         linenum = self.topLineNum + self.highlightLineNum
        #         if linenum in self.markedLineNums:
        #             self.markedLineNums.remove(linenum)
        #         else:
        #             self.markedLineNums.append(linenum)
        #
        #     def check_output(self, command):
        #
        #         process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE,
        #                                    stderr=subprocess.STDOUT,
        #                                    universal_newlines=True)
        #         output,stderr = process.communicate()
        #         retcode = process.poll()
        #
        #         if retcode:
        #                 self.stop.set()
        #                 self.restoreScreen()
        #                 raise subprocess.CalledProcessError(retcode, command,
        #                                                     output=output[0])
        #         return output.splitlines()
        #
        #     def getOutputLines(self):
        #         self.outputLines = self.check_output(self.command)
        #         self.nOutputLines = len(self.outputLines)
        #
        #     def displayScreen(self):
        #         # clear screen
        #         self.screen.clear()
        #         self.getOutputLines()
        #         # now paint the rows
        #         top = self.topLineNum
        #         bottom = self.topLineNum+curses.LINES
        #         for (index,line,) in enumerate(self.outputLines[top:bottom]):
        #             linenum = self.topLineNum + index
        #             if linenum in self.markedLineNums:
        #                 prefix = self.PREFIX_SELECTED
        #             else:
        #                 prefix = self.PREFIX_DESELECTED
        #
        #             #line = '%s %s' % (prefix, line,)
        #             # highlight current line
        #             if index != self.highlightLineNum:
        #                 self.screen.addstr(index, 0, line)
        #             else:
        #                 self.screen.addstr(index, 0, line, curses.A_BOLD)
        #         self.screen.refresh()
        #
        #     # move highlight up/down one line
        #     def updown(self, increment):
        #         nextLineNum = self.highlightLineNum + increment
        #
        #         # paging
        #         if increment == self.UP and self.highlightLineNum == 0\
        #            and self.topLineNum != 0:
        #             self.topLineNum += self.UP
        #             return
        #         elif increment == self.DOWN and nextLineNum == curses.LINES\
        #              and (self.topLineNum+curses.LINES) != self.nOutputLines:
        #             self.topLineNum += self.DOWN
        #             return
        #
        #         # scroll highlight line
        #         if increment == self.UP and (self.topLineNum != 0 or\
        #                                      self.highlightLineNum != 0):
        #             self.highlightLineNum = nextLineNum
        #         elif increment == self.DOWN and\
        #              (self.topLineNum+self.highlightLineNum+1) != self.nOutputLines\
        #              and self.highlightLineNum != curses.LINES:
        #             self.highlightLineNum = nextLineNum
        #
        #     def restoreScreen(self):
        #         curses.initscr()
        #         curses.nocbreak()
        #         curses.echo()
        #         curses.endwin()
        #
        #     # catch any weird termination situations
        #     def __del__(self):
        #         self.restoreScreen()
        #
        #
        # if __name__ == '__main__':
        #     ih = UnixWatchCommand(sys.argv[1:])
        #