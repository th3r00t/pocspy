import os
import unittest

from modules import Pages, Storage


class PagesTestCase(unittest.TestCase):
    def test_monitor(self):
        _log_dir = "/home/raelon/mnt/homeserver/logs"
        self.assertEqual(Pages(_log_dir).monitor(), True)

    def test_get_files(self):
        _log_dir = "/home/raelon/mnt/homeserver/logs"
        self.assertGreater(len(Pages(_log_dir).get_files()), 0)

    def test_sort_files(self):
        _log_dir = "/home/raelon/mnt/homeserver/logs"
        self.assertGreater(len(Pages(_log_dir).sort_files()), 0)

    def test_get_raw_pages(self):
        _log_dir = "/home/raelon/mnt/homeserver/logs"
        raw_pages = Pages(_log_dir).get_raw_pages()
        self.assertGreater(len(raw_pages), 0)

    def test_parse_pages(self):
        _log_dir = "/home/raelon/mnt/homeserver/logs"
        self.assertGreater(len(Pages(_log_dir).parse_pages()), 0)

    def test_queryset(self):
        _log_dir = "/home/raelon/mnt/homeserver/logs"
        self.assertGreater(len(Pages(_log_dir).queryset()), 0)


class StorageTestCase(unittest.TestCase):
    def __init__(self):
        self.test_db = "../test.db"

    def test_create_tables(self):
        database = Storage(self.test_db)
        self.assertTrue(Storage(self.test_db).create_tables(), True)

#    def teaddown_function(self):
#        os.remove((os.path.dirname(self.__file__)+self.test_db))



if __name__ == "__main__":
    unittest.TestSuite().debug()
