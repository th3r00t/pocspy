#!/usr/bin/env python

from src.modules import Pages, Storage

# Set Log file directory
log_folder = '/home/raelon/mnt/homeserver/logs'

# Start paging system
Pager = Pages(log_folder)
# Get pages & print
# _pages = Pager.parse_pages()
_pages = Pager.queryset()

# Start storage system
storage = Storage()
storage.create_tables()
