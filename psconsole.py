#!/usr/bin/env python
import sqlite3
import asyncio
from src.modules import UI

QUERY = "SELECT * FROM pages"
LENGTH = 0
LAST_LENGTH = 0
FIRST_RUN = 1
INTERFACE = None


class Data:
    def __init__(self):
        self.db = "recon.sqlite3"

    def connection(self):
        return sqlite3.connect(self.db)

    def results(self):
        return self.connection().execute(QUERY)


async def update_pages(data):
    global LENGTH
    global LAST_LENGTH
    global FIRST_RUN
    global INTERFACE
    while True:
        r = data.results().fetchall()
        if FIRST_RUN:
            FIRST_RUN = 0
            r.reverse()
            INTERFACE = UI().main()
        if LENGTH == 0:
            LENGTH = r.__len__()
        if r.__len__() > LAST_LENGTH:
            LENGTH = r.__len__()
            _num_new = LENGTH - LAST_LENGTH
            LAST_LENGTH = LENGTH
            while _num_new > 0:
                _page = r.pop()
                INTERFACE.out_main.addstr(f"{_page[2]} {_page[1]} {_page[8]}\n")
                INTERFACE.out_main.refresh()
                INTERFACE.in_main.refresh()
                _num_new = _num_new - 1
            INTERFACE.in_main.clear()
            INTERFACE.in_main.border(0)
            INTERFACE.in_main.addstr(1, 2, f"Pages {LENGTH}")
            INTERFACE.in_main.refresh()
        await asyncio.sleep(5)


async def main():
    data = Data()
    data_loop = asyncio.create_task(update_pages(data))
    await data_loop


asyncio.run(main())
