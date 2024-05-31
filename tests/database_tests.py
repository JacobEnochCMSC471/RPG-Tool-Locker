import database.locker_db
import sqlite3
from database import locker_db
import os
# os.remove("demofile.txt")

import unittest


class TestDatabaseFuncs(unittest.TestCase):

    # Unit Test to test that the database and tables are being created correctly.
    def test_create_db(self) -> None:
        # Create a brand new locker DB file using SQLite3
        test1 = database.locker_db.create_database('test.db')

        # Attempt to create a duplicate DB with the same name
        test2 = database.locker_db.create_database('test.db')

        self.assertEqual(test1, True, 'Test1 Create DB Fail')
        self.assertEqual(test2, False, 'Test2 Create DB Fail')

        test_db_conn = sqlite3.connect('test.db')
        test_db_cursor = test_db_conn.cursor()

        # Selecting count(*) from a table will return the number of tables that have the name specified.
        # 1 = the table exists, 0 = the table does not exist

        # Check that the table "employees" was created successfully
        test3 = \
            test_db_cursor.execute(
                "SELECT count(*) from sqlite_master WHERE type='table' AND name='employees'"). \
            fetchone()[0]

        # Check that the table "items" was created successfully
        test4 = \
            test_db_cursor.execute("SELECT count(*) from sqlite_master WHERE type='table' AND name='items'"). \
            fetchone()[0]

        # Check that the table "locker_doors" was created successfully
        test5 = \
            test_db_cursor.execute("SELECT count(*) from sqlite_master WHERE type='table' AND name='locker_doors'"). \
            fetchone()[0]

        self.assertEqual(test3, 1, "Test3 Fail - Employees table not present.\n")
        self.assertEqual(test4, 1, "Test4 Fail - Items table not present.\n")
        self.assertEqual(test5, 1, "Test5 Fail - Locker Doors table not present.\n")

        return


class TestEmployeeCRUD(unittest.TestCase):

    def test_insert_func_single(self):
        return
