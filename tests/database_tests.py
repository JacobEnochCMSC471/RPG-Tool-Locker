import unittest
import sqlite3
import os
from database import locker_db


class TestDatabaseFuncs(unittest.TestCase):
    def setUp(self) -> None:
        # Ensure there is no leftover test database file
        if os.path.exists("test.db"):
            os.remove("test.db")

    def tearDown(self) -> None:
        # Clean up the test database file after each test
        if os.path.exists("test.db"):
            os.remove("test.db")

    def test_create_db(self) -> None:
        # Create a brand-new locker DB file using SQLite3
        test1 = locker_db.create_database("test.db")

        # Attempt to create a duplicate DB with the same name
        test2 = locker_db.create_database("test.db")

        self.assertEqual(True, test1, "Test1 Create DB Fail")
        self.assertEqual(True, test2, "Test2 Create Duplicate DB Fail")

        test_db_conn = sqlite3.connect('test.db')
        test_db_cursor = test_db_conn.cursor()

        # Check that the table "employees" was created successfully
        test3 = \
            test_db_cursor.execute(
                "SELECT count(*) from sqlite_master WHERE type='table' AND name='employees'").fetchone()[
                0]

        # Check that the table "items" was created successfully
        test4 = \
            test_db_cursor.execute("SELECT count(*) from sqlite_master WHERE type='table' AND name='items'").fetchone()[
                0]

        # Check that the table "locker_doors" was created successfully
        test5 = test_db_cursor.execute(
            "SELECT count(*) from sqlite_master WHERE type='table' AND name='locker_doors'").fetchone()[0]

        self.assertEqual(1, test3, "Test3 Fail - Employees table not present.\n")
        self.assertEqual(1, test4, "Test4 Fail - Items table not present.\n")
        self.assertEqual(1, test5, "Test5 Fail - Locker Doors table not present.\n")

        test_db_cursor.close()
        test_db_conn.close()

    def test_is_sql_db(self) -> None:
        locker_db.create_database("test.db")

        test6 = locker_db.isSqlite3Db("test.db")
        test7 = locker_db.isSqlite3Db("database_tests.py")

        self.assertEqual(True, test6, "Test6 Is_SQL_DB Fail")
        self.assertEqual(False, test7, "Test7 Is_SQL_DB Fail")


class TestEmployeeCRUD(unittest.TestCase):
    def setUp(self) -> None:
        locker_db.create_database("test.db")
        self.db_conn = sqlite3.connect("test.db")
        self.db_cursor = self.db_conn.cursor()
        self.db_cursor.execute("DELETE FROM employees")

    def tearDown(self) -> None:
        self.db_cursor.close()
        self.db_conn.close()
        if os.path.exists("test.db"):
            os.remove("test.db")

    def test_insert_func_single_correct(self) -> None:
        single_insert_correct = [("12345", "Jake Enoch", 5)]

        test8 = locker_db.add_employee(self.db_cursor, single_insert_correct)

        test9 = self.db_cursor.execute("SELECT * FROM employees").fetchall()

        self.assertEqual(True, test8, "Test8 Failed: Single Insert Correct True Return")
        self.assertListEqual([('12345', 'Jake Enoch', 5)], test9, "Test9 Failed: Single Insert Correct")

    def test_insert_func_single_incorrect(self) -> None:
        single_insert_incorrect = [(12345, "Jake Enoch", 5)]

        locker_db.add_employee(self.db_cursor, [("12345", "Jake Enoch", 5)])  # Insert a correct record first

        test10 = locker_db.add_employee(self.db_cursor, single_insert_incorrect)

        test11 = self.db_cursor.execute("SELECT * FROM employees").fetchall()

        self.assertEqual(False, test10, "Test 10 Failed: Single Insert Incorrect False Return")
        self.assertListEqual([('12345', 'Jake Enoch', 5)], test11, "Test11 Failed: Single Insert Incorrect")

    def test_insert_func_multiple_correct(self) -> None:
        multiple_insert_correct = [("123", "John Enoch", 4), ("124", "Nick Enoch", 3)]

        locker_db.add_employee(self.db_cursor, [("12345", "Jake Enoch", 5)])  # Insert a correct record first

        test12 = locker_db.add_employee(cursor=self.db_cursor, list_of_employees=multiple_insert_correct)

        test13 = self.db_cursor.execute("SELECT * FROM employees").fetchall()

        self.assertEqual(True, test12, "Test12 Failed: Multi Insert True Return")
        self.assertListEqual([('12345', 'Jake Enoch', 5), ("123", "John Enoch", 4), ("124", "Nick Enoch", 3)], test13,
                             "Test13 Failed: Multi Insert")

    def test_multi_insert_multiple_incorrect(self) -> None:
        multiple_insert_incorrect = [("125", "Thomas Saddler", "4"), ("126", "Nick Enoch", 3)]

        locker_db.add_employee(self.db_cursor, [("12345", "Jake Enoch", 5), ("123", "John Enoch", 4),
                                                ("124", "Nick Enoch", 3)])  # Insert correct records first

        test14 = locker_db.add_employee(cursor=self.db_cursor, list_of_employees=multiple_insert_incorrect)

        test15 = self.db_cursor.execute("SELECT * FROM employees").fetchall()

        self.assertEqual(False, test14, "Test14 Failed: Multi Insert Incorrect False Return")
        self.assertListEqual([('12345', 'Jake Enoch', 5), ('123', 'John Enoch', 4), ('124', 'Nick Enoch', 3)], test15,
                             "Test15 Failed: Multi Insert Incorrect")

    def test_delete_existing_employee_correct(self) -> None:
        locker_db.add_employee(self.db_cursor, [("12345", "Jake Enoch", 5), ("123", "John Enoch", 4),
                                                ("124", "Nick Enoch", 3)])  # Insert records first

        test16 = locker_db.remove_employee(cursor=self.db_cursor, emp_id="123")

        test17 = self.db_cursor.execute("SELECT * FROM employees").fetchall()

        self.assertEqual(True, test16, "Test16 Failed: Remove Existing Employee Return Value")
        self.assertListEqual([('12345', 'Jake Enoch', 5), ('124', 'Nick Enoch', 3)], test17,
                             "Test17 Failed: Remove Existing Employee")

    def test_delete_existing_employee_incorrect(self) -> None:
        locker_db.add_employee(self.db_cursor,
                               [("12345", "Jake Enoch", 5), ("124", "Nick Enoch", 3)])  # Insert records first

        test18 = locker_db.remove_employee(cursor=self.db_cursor, emp_id=124)

        test19 = self.db_cursor.execute("SELECT * FROM employees").fetchall()

        self.assertEqual(False, test18, "Test18 Failed: Remove Existing Employee Incorrect Format Return Value")
        self.assertListEqual([('12345', 'Jake Enoch', 5), ('124', 'Nick Enoch', 3)], test19,
                             "Test19 Failed: Remove Existing Employee Wrong Type")

    def test_delete_nonexistent_employee(self) -> None:
        locker_db.add_employee(self.db_cursor,
                               [("12345", "Jake Enoch", 5), ("124", "Nick Enoch", 3)])  # Insert records first

        test20 = locker_db.remove_employee(cursor=self.db_cursor, emp_id="123456789")

        test21 = self.db_cursor.execute("SELECT * FROM employees").fetchall()

        self.assertEqual(False, test20, "Test20 Fail: Remove Nonexistent Employee Return Value")
        self.assertListEqual([('12345', 'Jake Enoch', 5), ('124', 'Nick Enoch', 3)], test21,
                             "Test21 Fail: Remove Nonexistent Employee")

    def test_update_employee_correct(self) -> None:
        locker_db.add_employee(self.db_cursor,
                               [("12345", "Jake Enoch", 5), ("124", "Nick Enoch", 3)])  # Insert records first

        test22 = locker_db.update_employee(cursor=self.db_cursor, emp_id="124", new_details=("Dave Enoch", 5))

        test23 = self.db_cursor.execute("SELECT * FROM employees WHERE id = 124").fetchall()

        self.assertEqual(True, test22, "Test22 Fail: Update Employee Correct Return Value")
        self.assertListEqual([("124", "Dave Enoch", 5)], test23, "Test23 Fail: Update Employee Check")

    def test_update_employee_incorrect(self) -> None:
        locker_db.add_employee(self.db_cursor, [("12345", "Jake Enoch", 5)])  # Insert a correct record first

        # (name, perm_level) is correct formatting
        incorrect_update = (4, "Paul Enoch")

        test24 = locker_db.update_employee(cursor=self.db_cursor, emp_id="12345", new_details=incorrect_update)

        test25 = self.db_cursor.execute("SELECT * FROM employees WHERE id = 12345").fetchall()

        self.assertEqual(False, test24, "Test24 Failed: Incorrect Update Return Value")
        self.assertListEqual([("12345", "Jake Enoch", 5)], test25, "Test25 Failed: Incorrect Update")

        incorrect_update = ("Paul Enoch", 4, "This should not be here")

        test26 = locker_db.update_employee(cursor=self.db_cursor, emp_id="12345", new_details=incorrect_update)

        test27 = self.db_cursor.execute("SELECT * FROM employees WHERE id = 12345").fetchall()

        self.assertEqual(False, test26, "Test26 Fail: Incorrect Update Return Value, 3 parameters")
        self.assertListEqual([("12345", "Jake Enoch", 5)], test27, "Test27 Fail: Incorrect Update 3 Parameters")

    def test_get_employee_exists(self) -> None:
        locker_db.add_employee(self.db_cursor, [("12345", "Jake Enoch", 5)])  # Insert a correct record first

        test28 = locker_db.get_employee(cursor=self.db_cursor, emp_id="12345")

        self.assertEqual(('12345', 'Jake Enoch', 5), test28, "Test28 Failed: Get Employee (Exists)")

    def test_get_employee_dne(self) -> None:
        locker_db.add_employee(self.db_cursor, [("12345", "Jake Enoch", 5)])  # Insert a correct record first

        test29 = locker_db.get_employee(cursor=self.db_cursor, emp_id="007")

        self.assertEqual(None, test29, "Test29 Failed: Get Employee (does not exist)")

    def test_get_all_employees(self) -> None:
        locker_db.add_employee(self.db_cursor,
                               [("12345", "Jake Enoch", 5), ("124", "Dave Enoch", 5)])  # Insert correct records first

        test30 = locker_db.get_all_employees(self.db_cursor)

        self.assertListEqual([("12345", "Jake Enoch", 5), ("124", "Dave Enoch", 5)], test30,
                             "Test30 Failed: Get All Employees Return")


class TestItemCRUD(unittest.TestCase):

    def setUp(self) -> None:
        locker_db.create_database("test.db")
        self.db_conn = sqlite3.connect("test.db")
        self.db_cursor = self.db_conn.cursor()
        self.db_cursor.execute("DELETE FROM items")

    def tearDown(self) -> None:
        self.db_cursor.close()
        self.db_conn.close()
        if os.path.exists("test.db"):
            os.remove("test.db")
