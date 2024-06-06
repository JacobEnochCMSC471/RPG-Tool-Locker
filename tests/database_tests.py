# import database.locker_db
import sqlite3
from database import locker_db
import os
# os.remove("demofile.txt")

import unittest


class TestDatabaseFuncs(unittest.TestCase):
    # Unit Test to test that the database and tables are being created correctly.

    def test_create_db(self) -> None:
        # Create a brand-new locker DB file using SQLite3
        test1 = locker_db.create_database("test.db")

        # Attempt to create a duplicate DB with the same name
        test2 = locker_db.create_database("test.db")

        self.assertEqual(True, test1, "Test1 Create DB Fail")
        self.assertEqual(True, test2, "Test2 Create Duplicate DB Fail")

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

        self.assertEqual(1, test3, "Test3 Fail - Employees table not present.\n")
        self.assertEqual(1, test4, "Test4 Fail - Items table not present.\n")
        self.assertEqual(1, test5, "Test5 Fail - Locker Doors table not present.\n")

        # Close the connection before trying to do anything to the file - DOY!!!
        test_db_cursor.close()
        test_db_conn.close()
        return

    def test_is_sql_db(self) -> None:
        # This is here in case tearDown() deletes it before it can be accessed for some reason
        locker_db.create_database("test.db")

        test6 = locker_db.isSqlite3Db("test.db")
        test7 = locker_db.isSqlite3Db("database_tests.py")

        self.assertEqual(True, test6, "Test6 Is_SQL_DB Fail")
        self.assertEqual(False, test7, "Test7 Is_SQL_DB Fail")

    '''def tearDown(self) -> None:
        # Delete the database file for teardown (if it exists)


        if os.path.exists("test.db"):
            os.remove("test.db")'''


class TestEmployeeCRUD(unittest.TestCase):
    locker_db.create_database("test.db")
    db_conn = sqlite3.connect("test.db")
    db_cursor = db_conn.cursor()

    # Test a single insert + edge cases for an employee
    def test_insert_func_single_correct(self) -> None:
        single_insert_correct = [("12345", "Jake Enoch", 5)]

        test8 = locker_db.add_employee(self.db_cursor, single_insert_correct)

        test9 = self.db_cursor.execute("SELECT * FROM employees").fetchall()

        self.assertEqual(True, test8, "Test8 Failed: Single Insert Correct True Return")

        self.assertEqual([('123', 'John Enoch', 4), ('124', 'Nick Enoch', 3), ('12345', 'Jake Enoch', 5)], test9,
                         "Test9 Failed: Single Insert Correct")

    def test_insert_func_single_incorrect(self) -> None:
        single_insert_incorrect = [(12345, "Jake Enoch", 5)]

        test10 = locker_db.add_employee(self.db_cursor, single_insert_incorrect)

        test11 = self.db_cursor.execute("SELECT * FROM employees").fetchall()

        self.assertEqual(False, test10, "Test 10 Failed: Single Insert Incorrect False Return")
        self.assertEqual([('123', 'John Enoch', 4), ('124', 'Nick Enoch', 3), ('12345', 'Jake Enoch', 5)], test11,
                         "Test11 Failed: Single Insert Incorrect")

    def test_insert_func_multiple_correct(self) -> None:
        multiple_insert_correct = [("123", "John Enoch", 4), ("124", "Nick Enoch", 3)]

        test12 = locker_db.add_employee(self.db_cursor, multiple_insert_correct)

        test13 = self.db_cursor.execute("SELECT * FROM employees").fetchall()

        self.assertEqual(True, test12, "Test12 Failed: Multi Insert True Return")

        self.assertListEqual([("123", "John Enoch", 4), ("124", "Nick Enoch", 3)], test13,
                             "Test13 Failed: Multi Insert")

    def test_multi_insert_multiple_incorrect(self) -> None:
        multiple_insert_incorrect = [("125", "Thomas Saddler", "4"), ("126", "Nick Enoch", 3)]

        test14 = locker_db.add_employee(self.db_cursor, multiple_insert_incorrect)

        test15 = self.db_cursor.execute("SELECT * FROM employees").fetchall()

        self.assertEqual(False, test14, "Test14 Failed: Multi Insert Incorrect False Return")

        self.assertListEqual([('123', 'John Enoch', 4), ('124', 'Nick Enoch', 3), ('12345', 'Jake Enoch', 5)], test15,
                             "Test15 Failed: Multi Insert Incorrect")

    def test_delete_existing_employee_correct(self) -> None:
        test16 = locker_db.remove_employee(self.db_cursor, "123")

        test17 = self.db_cursor.execute("SELECT * FROM employees").fetchall()

        self.assertEqual(True, test16, "Test16 Failed: Remove Existing Employee Return Value")

        self.assertListEqual([('124', 'Nick Enoch', 3), ('12345', 'Jake Enoch', 5)], test17, "Test17 Failed: Remove "
                                                                                             "Existing Employee")

    def test_delete_existing_employee_incorrect(self) -> None:
        test18 = locker_db.remove_employee(self.db_cursor, 124)

        test19 = self.db_cursor.execute("SELECT * FROM employees").fetchall()

        self.assertEqual(False, test18, "Test18 Failed: Remove Existing Employee Incorrect Format Return Value")

        self.assertListEqual([('124', 'Nick Enoch', 3), ('12345', 'Jake Enoch', 5)], test19, "Test19 Failed: Remove "
                                                                                             "Existing Employee Wrong "
                                                                                             "Type")

    def test_delete_nonexistent_employee(self) -> None:
        test20 = locker_db.remove_employee(self.db_cursor, "123456789")

        test21 = self.db_cursor.execute("SELECT * FROM employees").fetchall()

        self.assertEqual(False, test20, "Test20 Fail: Remove Nonexistent Employee Return Value")

        self.assertListEqual([('124', 'Nick Enoch', 3), ('12345', 'Jake Enoch', 5)], test21, "Test21 Fail: Remove "
                                                                                             "Nonexistent Employee")

    def test_update_employee_correct(self) -> None:
        test22 = locker_db.update_employee(self.db_cursor, "124", ("Dave Enoch", 5))
        test23 = test21 = self.db_cursor.execute("SELECT * FROM employees").fetchall()


