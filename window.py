#!/usr/bin/env python

import os, sys, re
import curses
import curses.textpad
import curses.wrapper
import time
from threading import Thread

class TermMenu(object):
    (_statuswin, _menuwin, _promptwin, _messagewin) = (None, None, None, None)

    _statuses = []
    _menus = []
    _message = ""
    
    def __init__(self):
        self.win = curses.initscr()
        self._updatethread = self.UpdateThread(self)
        self._log = open("input.log", "w")

    def assign_statuses(self, starr):
        # TODO: Check type and statuses are executable correctly
        self._statuses = starr
        return True

    def assign_menus(self, marr):
        # TODO: Check type and validate structure
        self._menus = marr
        return True

    def assign_prompt(self, prmt):
		self._prompt = prmt
		return True
      
    def cleanup(self):
        self._updatethread.stop()
        curses.endwin()
        self._log.close()

    def init_windows(self, stdscr):
        (height, width) = self.win.getmaxyx()
        
        # TODO: Optional status window / message window
        # TODO: Eventually we want to have a scrolling menu window
        st_rows = len(self._statuses) + 2
        mn_rows = len(self._menus) + 2
        
        self._statuswin = curses.newwin(st_rows, width, 0, 0)
        self._menuwin = curses.newwin(mn_rows, width, st_rows, 0)
        self._promptwin = curses.newwin(1, width, height - 2, 0)
        self._prompt = curses.textpad.Textbox(self._promptwin)
        self._messagewin = curses.newwin(1, width, height - 1, 0)

    def output_line(self, y, win, line):
        x = 10

        for el in line:
            output = el
            if hasattr(el, "__call__"): 
                # TODO: Map dynamically for lambda argument length
                output = el(self.args[el.func_code.co_varnames[0]])
            win.addstr(y, x, str(output))
            x += len(str(output)) + 2

    def print_message(self, message = "No current message"):
        self._messagewin.addstr(0, 0, message)
        self.refresh()
        
    def print_menu(self):
        y = 2
        for line in self._menus:
            key = line[0]
            text = line[1:-1]
            func = line[-1]
            self.output_line(y, self._menuwin, text)
            y += 1
        self.refresh()

    def print_status(self):
        y = 2
        for line in self._statuses:
            self.output_line(y, self._statuswin, line)
            y += 1
        self.refresh()

    def prompt(self, msg = "Make your selection: "):
        self._promptwin.clear()
    	self._promptwin.addstr(0, 10, msg)
        self.refresh()

        if not self._updatethread.is_alive():
            self._updatethread.start()
            
        #return self._promptwin.getstr(0, len(text) + 12)
        text = self._prompt.edit()
        ret = re.split("\s", text, 1)[0]
        self._log.write("INPUT {0} {1}\n".format(type(ret), ret))
        return ret

    def refresh(self):
        self._statuswin.refresh()
        self._menuwin.refresh()
        self._messagewin.refresh()
        self._promptwin.refresh()

    def start_window(self, args):
        istr = ''
        self.args = args

        curses.wrapper(self.init_windows)
        graceful = True
        
        while istr != 'q':
            self.print_status()
            self.print_menu()
            
            # TODO: Needs to heed to another threads prompting
            istr = self.prompt()
        
            # TODO: Clean this up
            sel = filter(lambda i: i[0] != None and i[0] == istr, self._menus)
            if len(sel) > 0 and hasattr(sel[0][-1], "__call__"):
                sel[0][-1](self.args[sel[0][-1].func_code.co_varnames[0]])
                       
        self.cleanup()
        
    def update(self):
        self.print_status()
        self.refresh()
        
    class UpdateThread(Thread):
        term_menu = None
        running = False
        
        def __init__(self, menu):
            super(TermMenu.UpdateThread, self).__init__()
            self.term_menu = menu
            
        def run(self):
            self.running = True
            while self.running: 
                self.term_menu.update()
                time.sleep(0.1)
                
        def stop(self):
            self.running = False

def main():
    def inc():
        from datetime import datetime
        return datetime.now()
        
    win = TermMenu()
    win.assign_statuses([
        [ "A)", "AAAA", lambda u: str(inc())  ],
        [ "B1", "BBBB"  ],
    ])
    win.assign_menus([
        [ "A)", "AAAA"  ],
        [ "B1", "BBBB"  ],
        [],
        [ "Q)", "Quit"  ],
    ])
    win.start_window({
        'u':    None,
    })
    print "END"

if __name__ == "__main__":
    main()
