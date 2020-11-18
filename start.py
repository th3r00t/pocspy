#!/usr/bin/env python
import os
import asyncio
from src.modules import PocSpyPages
from src.modules import PocSpyStorage
from src.modules import PocSpyDispatcher

ROOT = os.path.dirname(__file__)  # Set Project Root
LOGS = '/mnt/homeserver/logs'  # Set Log file directory
Storage = PocSpyStorage(ROOT)  # Initialize storage system
Pager = PocSpyPages(LOGS)  # Start paging system
Dispatcher = PocSpyDispatcher(LOGS, Pager, Storage)  # Start dispatcher
'''
Now we will scan the entire directory and via a sql
INSERT OR IGNORE statement ensure all pages exist in the db
'''
_pages = Pager.queryset()  # Get initial page set
for page in _pages:
    Storage.insert(page)  # Insert each page in _pages
Storage.commit()  # Commit the transaction

# Dispatcher.startWatcher()  # Start the watcher service
loop = asyncio.get_event_loop()
loop.run_until_complete(Dispatcher.startWatcher())

Storage.close()  # Close any remaining connection
