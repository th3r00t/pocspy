import os
import sqlite3
from hashlib import md5


class Pages:
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

    def get_raw_pages(self):
        pages = []
        for _file in self.sort_files():
            _file = open(_file, "r")
            for line in _file:
                line = line.rstrip()
                if len(line) > 0:
                    pages.append(line)
            _file.close()
        return pages

    def parse_pages(self):
        _pages = self.get_raw_pages()
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

    def queryset(self, pages=None):
        if pages is None:
            pages = self.parse_pages()
        _q, _qs = [], []
        for page in pages:
            page = page.split(" | ")
            for column in page:
                _q.append(column)
            _qs.append(_q)
            _q = []
        return _qs


class Storage:
    def __init_(self, db="../pages.db"):
        try:
            self.con = sqlite3.connect(os.path.dirname(self.__file__) + db)
        except FileNotFoundError:
            open(os.path.dirname(self.__file__) + db)
            self.con = sqlite3.connect(os.path.dirname(self.__file__) + db)
        self.c = self.con.cursor()

    def create_tables(self):
        self.c.execute(
            """CREATE TABLE IF NOT EXISTS pages
                    (pager int, time timestamp, date date, mode text,
                    modetype text, bits int, from text, addr text, msg text,
                    md5hash blob, UNIQUE(md5hash)
                    )"""
        )
        return True

    def insertPage(self, page):
        try:
            self.c.execute(
                "INSERT OR IGNORE INTO pages VALUES(?)",
                page.append(md5.new(page).digest()),
            )
            print(self.c.fetchone())
        except Exception as e:
            print(e)
        self.c.close()
