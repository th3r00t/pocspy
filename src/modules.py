import os
import sqlite3
import hashlib
import watchgod as wg
import asyncio

import curses as c
from curses import wrapper


class PocSpyPages:
    def __init__(self, folder):
        self._log_dir = folder
        self._monitor = False
        self._pages = []

    def monitor(self):
        self._monitor = not self._monitor
        return self._monitor

    def get_files(self):
        _f = []
        for _fn in os.scandir(self._log_dir):
            _f.append(_fn)
        return _f

    def sort_files(self):
        return sorted(self.get_files(), key=os.path.getmtime)

    def get_raw_pages(self, all):
        pages = []

        def readin(_file):
            _file = open(_file, "r")
            for line in _file:
                line = line.rstrip()
                if len(line) > 0:
                    pages.append(line)
            _file.close()

        if all:
            for _file in self.sort_files():
                readin(_file)
        else:
            files = self.sort_files()
            readin(files[-1])
        return pages

    def parse_pages(self, all):
        _pages = self.get_raw_pages(all)
        _ppages = []
        formatted = ""
        for page in _pages:
            row = page.split(" ")
            for i, column in enumerate(row):
                if i <= 11:
                    if len(column) > 1:
                        formatted = formatted + (column + " | ")
                    elif len(column) >= 1:
                        pass
                else:
                    formatted = formatted + (column + " ")
            _ppages.append(formatted)
            formatted = ""
        return _ppages

    def queryset(
        self, pages=None, all=True
    ):  # Return all pages by default, send false to get only most recent file
        if pages is None:
            pages = self.parse_pages(all)
        _q, _qs = [], []
        for page in pages:
            page = page.split(" | ")
            for column in page:
                _q.append(column)
            if len(_q) < 8:
                continue
            if len(_q) < 9:
                _q.insert(7, "<none>")
            _qs.append(_q)
            if len(_q[8]) < 1:
                _q[8] = "-- Decode Failure or Blank Msg --"
            _q = []
        return _qs


class PocSpyStorage:
    def __init__(self, root, dbfile="/recon.sqlite3"):
        self.pathing, self.dbfile = root, dbfile
        try:
            self.con = sqlite3.connect(self.pathing + self.dbfile)
        except FileNotFoundError:
            open(self.pathing + self.dbfile)
            self.con = sqlite3.connect(self.pathing + self.dbfile)
        self.c = self.con.cursor()
        self.create_tables()

    def create_tables(self):
        self.c.execute(
            """CREATE TABLE IF NOT EXISTS pages
                    (pager int,   time timestamp,  date date,  mode text,
                    modetype text,   bits int,  sender text,  addr text,  msg text,
                    md5hash blob,   UNIQUE(md5hash)
                    )"""
        )
        return True

    def insert(self, page):
        mds = ""
        md = [hashlib.md5(i.encode("utf-8")).hexdigest() for i in page]
        for h in md:
            mds = mds + h
        mds = mds.encode("utf-8")
        md5hash = hashlib.md5(mds).hexdigest()
        page.append(md5hash)
        try:
            p = page
            self.c.execute(
                "INSERT OR IGNORE INTO pages VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (p[0], p[1], p[2], p[3], p[4], p[5], p[6], p[7], p[8], p[9]),
            )
        except Exception as e:
            print(e)

    def commit(self):
        self.con.commit()
        return True

    def close(self):
        self.con.close()
        return True


class PocSpyDispatcher:
    def __init__(self, logs, Pager, Storage):
        self.logs = logs
        self.pager = Pager
        self.storage = Storage

    async def startWatcher(self):
        async for changes in wg.awatch(self.logs):
            self.triggerHook()

    def triggerHook(self):
        pages = self.pager.queryset(all=False)
        for page in pages:
            msg = ""
            self.storage.insert(page)
            for i in page:
                msg = msg + " | " + i
        # print(msg)
        self.storage.commit()

    def stopWatcher(self):
        pass

    def status(self):
        pass


class UI:
    def __init__(self):
        self.scr = None
        self.max_y, self.max_x = 0, 0
        self.center = []
        self.out_main = None
        self.in_main = None

    def initialize(self):
        self.scr = c.initscr()
        self.max_y, self.max_x = self.scr.getmaxyx()
        self.center = [(self.max_y / 2), (self.max_x / 2)]
        c.noecho()
        c.cbreak()
        c.start_color()
        self.scr.keypad(True)
        self.scr.clear()

    def exit(self):
        c.nocbreak()
        self.scr.keypad(False)
        c.echo()
        c.endwin()

    def abs_center(self, text, offset=0):
        posxy = [
            round(self.center[0]) + offset,
            round((self.center[1] - (text.__len__() / 2))),
        ]
        return posxy[0], posxy[1], text

    def draw_home(self):
        banner_1 = self.abs_center("PocSpy PDW Log Interface", -2)
        banner_2 = self.abs_center("V0.0.01 EarlyEagle", -1)
        banner_3 = self.abs_center("github.com/th3r00t/PocSpy", 0)
        banner_4 = self.abs_center("press any key", 1)
        self.scr.addstr(*banner_1)
        self.scr.addstr(*banner_2)
        self.scr.addstr(*banner_3)
        self.scr.addstr(*banner_4)
        self.scr.refresh()
        self.scr.getkey()

    def draw_main_interface(self):
        self.scr.clear()
        self.scr.refresh()
        self.out_main = c.newwin(self.max_y - 3, self.max_x, 0, 0)
        self.out_main.idlok(True)
        self.out_main.scrollok(True)
        self.out_main.refresh()

    def draw_input_interface(self):
        self.in_main = c.newwin(3, self.max_x, self.max_y - 3, 0)
        self.in_main.border(0)
        self.in_main.addstr(1, 2, "Pages ")
        self.in_main.refresh()

    def main(self):
        self.initialize()
        self.draw_home()
        self.draw_main_interface()
        self.draw_input_interface()
        return self
