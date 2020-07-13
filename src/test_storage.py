import os
import unittest

from modules import Storage


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
