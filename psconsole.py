#!/usr/bin/env python
"""
A few examples of displaying a bottom toolbar.

The ``prompt`` function takes a ``bottom_toolbar`` attribute.
This can be any kind of formatted text (plain text, HTML or ANSI), or
it can be a callable that takes an App and returns an of these.

The bottom toolbar will always receive the style 'bottom-toolbar', and the text
inside will get 'bottom-toolbar.text'. These can be used to change the default
style.
"""
import sqlite3
from prompt_toolkit import prompt
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.styles import Style

QUERY = "SELECT * FROM pages"

class Data:
    def __init__(self):
        self.db = 'recon.sqlite3'

    def connection(self):
        return sqlite3.connect(self.db)

    def results(self):
        return self.connection().execute(QUERY)


def bottom_bar(count=0, matches=0):
    style = Style.from_dict(
        {
            "bottom-toolbar": "#aaaa00 bg:#ff0000",
            "bottom-toolbar.text": "#aaaa44 bg:#aa4444",
        }
    )
    text = prompt(
        "> ",
        bottom_toolbar=HTML(
            f'  <b>Page Count: <i>{count}</i> Search Matches: <i>{matches}</i></b>'),
        style=style
    )
    print("You said: %s" % text)


def main():
    data = Data()
    while True:
        r = data.results().fetchall()
        for i in r:
            print(f'{i[2]} {i[1]} {i[8]}')
        bottom_bar(r.__len__())

if __name__ == "__main__":
    main()