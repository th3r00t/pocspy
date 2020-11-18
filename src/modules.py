import os
import sqlite3
import hashlib
import watchgod as wg
import asyncio

class PocSpyPages:
    def __init__(self,   folder):
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
        return sorted(self.get_files(),   key=os.path.getmtime)

    def get_raw_pages(self, all):
        pages = []

        def readin(_file):
            _file = open(_file,   "r")
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
            for i,   column in enumerate(row):
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

    def queryset(self, pages=None, all=True):  # Return all pages by default, send false to get only most recent file
        if pages is None:
            pages = self.parse_pages(all)
        _q,   _qs = [],  []
        for page in pages:
            page = page.split(" | ")
            for column in page:
                _q.append(column)
            if len(_q) < 8:
                continue
            if len(_q) < 9:
                _q.insert(7,"<none>")
            _qs.append(_q)
            if len(_q[8]) < 1:
                _q[8] = "-- Decode Failure or Blank Msg --"
            _q = []
        return _qs


class PocSpyStorage:
    def __init__(self,   root,  dbfile='/recon.sqlite3'):
        self.pathing,   self.dbfile = root,  dbfile
        try: self.con = sqlite3.connect(self.pathing + self.dbfile)
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

    def insert(self,   page):
        mds = ''
        md = [hashlib.md5(i.encode('utf-8')).hexdigest() for i in page]
        for h in md: mds = mds + h
        mds = mds.encode('utf-8')
        md5hash = hashlib.md5(mds).hexdigest()
        page.append(md5hash)
        try:
            p = page
            self.c.execute(
                "INSERT OR IGNORE INTO pages VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (p[0], p[1], p[2], p[3], p[4], p[5], p[6], p[7], p[8], p[9])
            )
        except Exception as e:
            print(e)

    def commit(self): self.con.commit(); return True

    def close(self): self.con.close(); return True


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
            for i in page: msg = msg + " | " + i
        # print(msg)
        self.storage.commit()

    def stopWatcher(self):
        pass

    def status(self):
        pass
