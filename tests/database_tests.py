# import database.locker_db
import sqlite3
from database import locker_db
import os
# os.remove("demofile.txt")

import unittest


class TestDatabaseFuncs(unittest.TestCase):
    # Unit Test to test that the database and tables are being created correctly.

    def test_create_db(self) -> None:
        # Create a brand new locker DB file using SQLite3
        test1 = locker_db.create_database("test.db")

        # Attempt to create a duplicate DB with the same name
        test2 = locker_db.create_database("test.db")

        self.assertEqual(test1, True, "Test1 Create DB Fail")
        self.assertEqual(test2, False, "Test2 Create DB Fail")

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

        # Close the connection before trying to do anything to the file - DOY!!!
        test_db_conn.close()
        return

    def test_is_sql_db(self) -> None:
        # This is here in case tearDown() deletes it before it can be accessed for some reason
        locker_db.create_database("test.db")

        test1 = locker_db.isSqlite3Db("test.db")
        test2 = locker_db.isSqlite3Db("database_tests.py")

        self.assertEqual(test1, True, "Test1 Is_SQL_DB Fail")
        self.assertEqual(test2, False, "Test2 Is_SQL_DB Fail")


'''    def tearDown(self) -> None:
        # Delete the database file for teardown (if it exists)
        if os.path.exists("test.db"):
            os.remove("test.db")'''


class TestEmployeeCRUD(unittest.TestCase):

    # Test a single insert + edge cases for an employee
    def test_insert_func_single(self):


        return
