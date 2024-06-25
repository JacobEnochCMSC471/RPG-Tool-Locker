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

        self.assertTrue(test1, "Test1 Create DB Fail")
        self.assertTrue(test2, "Test2 Create Duplicate DB Fail")

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

        self.assertTrue(test6, "Test6 Is_SQL_DB Fail")
        self.assertFalse(test7, "Test7 Is_SQL_DB Fail")


class TestEmployeeCRUD(unittest.TestCase):
    def setUp(self) -> None:
        # Before each test, create, connect to and retrieve a cursor object from the database. Wipe employee table.
        locker_db.create_database("test.db")
        self.db_conn = sqlite3.connect("test.db")
        self.db_cursor = self.db_conn.cursor()
        self.db_cursor.execute("DELETE FROM employees")

    def tearDown(self) -> None:
        # After each test, close connection and cursor to database and delete the database file if present.
        self.db_cursor.close()
        self.db_conn.close()
        if os.path.exists("test.db"):
            os.remove("test.db")

    def test_insert_func_single_correct(self) -> None:
        # Test a single correct employee item insert. Check return value and presence in employees table.
        # Should return True and the table should have one item in it.

        single_insert_correct = [("12345", "Jake Enoch", 5)]

        test8 = locker_db.add_employee(self.db_cursor, single_insert_correct)

        test9 = self.db_cursor.execute("SELECT * FROM employees").fetchall()

        self.assertTrue(test8, "Test8 Failed: Single Insert Correct True Return")
        self.assertListEqual([('12345', 'Jake Enoch', 5)], test9, "Test9 Failed: Single Insert Correct")

    def test_insert_func_single_incorrect(self) -> None:
        # Test a single incorrect employee item insert. Check return value and presence in employees table.
        # Should return False and the table should be empty.

        single_insert_incorrect = [(12345, "Jake Enoch", 5)]

        locker_db.add_employee(self.db_cursor, [("12345", "Jake Enoch", 5)])  # Insert a correct record first

        test10 = locker_db.add_employee(self.db_cursor, single_insert_incorrect)

        test11 = self.db_cursor.execute("SELECT * FROM employees").fetchall()

        self.assertFalse(test10, "Test 10 Failed: Single Insert Incorrect False Return")
        self.assertListEqual([('12345', 'Jake Enoch', 5)], test11, "Test11 Failed: Single Insert Incorrect")

    def test_insert_func_multiple_correct(self) -> None:
        # Test inserting multiple correctly formatted employees into the table. Check return value and presence
        # in table.

        # Should return True and the employees table should have 2 items in it.

        multiple_insert_correct = [("123", "John Enoch", 4), ("124", "Nick Enoch", 3)]

        locker_db.add_employee(self.db_cursor, [("12345", "Jake Enoch", 5)])  # Insert a correct record first

        test12 = locker_db.add_employee(cursor=self.db_cursor, list_of_employees=multiple_insert_correct)

        test13 = self.db_cursor.execute("SELECT * FROM employees").fetchall()

        self.assertTrue(test12, "Test12 Failed: Multi Insert True Return")
        self.assertListEqual([('12345', 'Jake Enoch', 5), ("123", "John Enoch", 4), ("124", "Nick Enoch", 3)], test13,
                             "Test13 Failed: Multi Insert")

    def test_multi_insert_multiple_incorrect(self) -> None:
        # Test inserting multiple incorrectly formatted employees into employee table. Check return val and presence
        # in table.

        # Should return False and there should be no employees in the table.

        multiple_insert_incorrect = [("125", "Thomas Saddler", "4"), ("126", "Nick Enoch", 3)]

        locker_db.add_employee(self.db_cursor, [("12345", "Jake Enoch", 5), ("123", "John Enoch", 4),
                                                ("124", "Nick Enoch", 3)])  # Insert correct records first

        test14 = locker_db.add_employee(cursor=self.db_cursor, list_of_employees=multiple_insert_incorrect)

        test15 = self.db_cursor.execute("SELECT * FROM employees").fetchall()

        self.assertFalse(test14, "Test14 Failed: Multi Insert Incorrect False Return")
        self.assertListEqual([('12345', 'Jake Enoch', 5), ('123', 'John Enoch', 4), ('124', 'Nick Enoch', 3)], test15,
                             "Test15 Failed: Multi Insert Incorrect")

    def test_delete_existing_employee_correct(self) -> None:
        # Test deleting an employee that exists in the table. Add employee first. Check return value + presence in table.
        # Should return True and there should be 2 employees in the employees table after successful deletion.

        locker_db.add_employee(self.db_cursor, [("12345", "Jake Enoch", 5), ("123", "John Enoch", 4),
                                                ("124", "Nick Enoch", 3)])  # Insert records first

        test16 = locker_db.remove_employee(cursor=self.db_cursor, emp_id="123")

        test17 = self.db_cursor.execute("SELECT * FROM employees").fetchall()

        self.assertTrue(test16, "Test16 Failed: Remove Existing Employee Return Value")
        self.assertListEqual([('12345', 'Jake Enoch', 5), ('124', 'Nick Enoch', 3)], test17,
                             "Test17 Failed: Remove Existing Employee")

    def test_delete_existing_employee_incorrect(self) -> None:
        # Attempt to delete an item in the table using an incorrectly typed employee ID.
        # Check return value and presence of employee with id "124" in table.

        # Should return False and the employee with ID "124" should still be in the employees table. 2 records total.

        locker_db.add_employee(self.db_cursor,
                               [("12345", "Jake Enoch", 5), ("124", "Nick Enoch", 3)])  # Insert records first

        test18 = locker_db.remove_employee(cursor=self.db_cursor, emp_id=124)

        test19 = self.db_cursor.execute("SELECT * FROM employees").fetchall()

        self.assertFalse(test18, "Test18 Failed: Remove Existing Employee Incorrect Format Return Value")
        self.assertListEqual([('12345', 'Jake Enoch', 5), ('124', 'Nick Enoch', 3)], test19,
                             "Test19 Failed: Remove Existing Employee Wrong Type")

    def test_delete_nonexistent_employee(self) -> None:
        # Attempt to delete an employee that doesn't exist in the employees table. Check return value and
        # presence in table.

        # Should return False and the number of employees in the table should remain at 2.

        locker_db.add_employee(self.db_cursor,
                               [("12345", "Jake Enoch", 5), ("124", "Nick Enoch", 3)])  # Insert records first

        test20 = locker_db.remove_employee(cursor=self.db_cursor, emp_id="123456789")

        test21 = self.db_cursor.execute("SELECT * FROM employees").fetchall()

        self.assertFalse(test20, "Test20 Fail: Remove Nonexistent Employee Return Value")
        self.assertListEqual([('12345', 'Jake Enoch', 5), ('124', 'Nick Enoch', 3)], test21,
                             "Test21 Fail: Remove Nonexistent Employee")

    def test_update_employee_correct(self) -> None:
        # Test correctly updating an employee's data. Check return value and verify that changes occurred to record.

        # Should return True and the employee with id "124" should have their name and permission levels changed.
        # The id should remain the same.

        locker_db.add_employee(self.db_cursor,
                               [("12345", "Jake Enoch", 5), ("124", "Nick Enoch", 3)])  # Insert records first

        test22 = locker_db.update_employee(cursor=self.db_cursor, emp_id="124", new_details=("Dave Enoch", 5))

        test23 = self.db_cursor.execute("SELECT * FROM employees WHERE id = 124").fetchall()

        self.assertTrue(test22, "Test22 Fail: Update Employee Correct Return Value")
        self.assertListEqual([("124", "Dave Enoch", 5)], test23, "Test23 Fail: Update Employee Check")

    def test_update_employee_incorrect(self) -> None:
        # Test attempting to update employee record with incorrectly formatted tuples. Check return val and
        # update status in table.

        # Should return False for all return val tests and the records should remain unchanged.

        locker_db.add_employee(self.db_cursor, [("12345", "Jake Enoch", 5)])  # Insert a correct record first

        # (name, perm_level) is correct formatting
        incorrect_update = (4, "Paul Enoch")

        test24 = locker_db.update_employee(cursor=self.db_cursor, emp_id="12345", new_details=incorrect_update)

        test25 = self.db_cursor.execute("SELECT * FROM employees WHERE id = 12345").fetchall()

        self.assertFalse(test24, "Test24 Failed: Incorrect Update Return Value")
        self.assertListEqual([("12345", "Jake Enoch", 5)], test25, "Test25 Failed: Incorrect Update")

        incorrect_update = ("Paul Enoch", 4, "This should not be here")

        test26 = locker_db.update_employee(cursor=self.db_cursor, emp_id="12345", new_details=incorrect_update)

        test27 = self.db_cursor.execute("SELECT * FROM employees WHERE id = 12345").fetchall()

        self.assertFalse(test26, "Test26 Fail: Incorrect Update Return Value, 3 parameters")
        self.assertListEqual([("12345", "Jake Enoch", 5)], test27, "Test27 Fail: Incorrect Update 3 Parameters")

    def test_get_employee_exists(self) -> None:
        # Test to make sure retrieving an employee is correct. Check return value (list).
        # Should return a tuple containing a single employee.

        locker_db.add_employee(self.db_cursor, [("12345", "Jake Enoch", 5)])  # Insert a correct record first

        test28 = locker_db.get_employee(cursor=self.db_cursor, emp_id="12345")

        self.assertTupleEqual(('12345', 'Jake Enoch', 5), test28, "Test28 Failed: Get Employee (Exists)")

    def test_get_employee_dne(self) -> None:
        # Test functionality of retrieve function when an employee does not exist. Check return type (list).
        # Should return None since there is nothing in the table to retrieve.

        locker_db.add_employee(self.db_cursor, [("12345", "Jake Enoch", 5)])  # Insert a correct record first

        test29 = locker_db.get_employee(cursor=self.db_cursor, emp_id="007")

        self.assertIsNone(test29, "Test29 Failed: Get Employee (does not exist)")

    def test_get_all_employees(self) -> None:
        # Test functionality of get_all_employees() function.
        # Should return a list of tuples of size 2.
        locker_db.add_employee(self.db_cursor,
                               [("12345", "Jake Enoch", 5), ("124", "Dave Enoch", 5)])  # Insert correct records first

        test30 = locker_db.get_all_employees(self.db_cursor)

        self.assertListEqual([("12345", "Jake Enoch", 5), ("124", "Dave Enoch", 5)], test30,
                             "Test30 Failed: Get All Employees Return")


class TestItemCRUD(unittest.TestCase):

    def setUp(self) -> None:
        # Before every test create a new database, connect to it, retrieve the cursor and remove any existent items
        # from DB.
        locker_db.create_database("test.db")
        self.db_conn = sqlite3.connect("test.db")
        self.db_cursor = self.db_conn.cursor()
        self.db_cursor.execute("DELETE FROM items")

    def tearDown(self) -> None:
        # After each test, close the connection and cursor and delete the database file if present.
        self.db_cursor.close()
        self.db_conn.close()
        if os.path.exists("test.db"):
            os.remove("test.db")

    def test_add_single_item_correct(self) -> None:
        # Test adding a single item correctly to the database.
        # Check return value and presence in table.

        items_to_add = [("TL001", "Flathead Screwdriver", "6in length", 0, "001", 1)]

        test31 = locker_db.add_item(cursor=self.db_cursor, list_of_items=items_to_add)

        test32 = self.db_cursor.execute("SELECT * FROM items").fetchall()

        self.assertTrue(test31, "Test 31 Failed - Single Insert Return Value")

        self.assertListEqual(items_to_add, test32, "Test 32 Failed - Single Insert")

    def test_add_single_item_incorrect(self) -> None:

        # Test to make sure we catch all possible type errors when a new item is being added.\
        # For each item, test return value and presence in table.
        items_to_add1 = [(1, "Flathead Screwdriver", "6in length", 0, "001", 1)]
        items_to_add2 = [("TL001", 1, "6in length", 0, "001", 1)]
        items_to_add3 = [("TL001", "Flathead Screwdriver", 1, 0, "001", 1)]
        items_to_add4 = [("TL001", "Flathead Screwdriver", "6in length", "0", "001", 1)]
        items_to_add5 = [("TL001", "Flathead Screwdriver", "6in length", 0, 1, 1)]
        items_to_add6 = [("TL001", "Flathead Screwdriver", "6in length", 0, "001", "1")]

        items_list = [items_to_add1, items_to_add2, items_to_add3, items_to_add4, items_to_add5, items_to_add6]

        counter = 33

        # Iteratively check all 6 items instead of using a big non-dynamic block of code to check each one individually.
        for item in items_list:
            curr_test_return = locker_db.add_item(self.db_cursor, list_of_items=item)
            curr_test_retrieve = self.db_cursor.execute("SELECT * FROM items").fetchall()

            self.assertFalse(curr_test_return, f"Test {counter} Failed - Bad Insert Return Value")

            counter += 1

            self.assertListEqual([], curr_test_retrieve, f"Test {counter} Failed - Bad Single Insert")

            counter += 1

        print(f"Test Counter: {counter}")

    def test_empty_insert(self) -> None:
        # Test if an empty list, a list with an empty tuple and an empty tuple can be added to the table.
        # Check return type and presence in table.

        counter = 46

        # Test whether these empty lists/tuples can be added to the item table
        item_to_insert1 = []
        item_to_insert2 = [()]
        item_to_insert3 = ()

        item_list = [item_to_insert1, item_to_insert2, item_to_insert3]

        for item in item_list:
            curr_test_return = locker_db.add_item(cursor=self.db_cursor, list_of_items=item)
            curr_test_retrieve = self.db_cursor.execute("SELECT * FROM items").fetchall()

            self.assertFalse(curr_test_return, f"Test {counter} Failed - Empty Insert Return Value")

            counter += 1

            self.assertListEqual([], curr_test_retrieve, f"Test {counter} Failed - Empty Insert")

            counter += 1

            print(counter)

    def test_add_multiple_correct_items(self) -> None:
        # Test adding multiple valid items to the database.
        items_to_add = [
            ("TL001", "Flathead Screwdriver", "6in length", 0, "001", 1),
            ("TL002", "Phillips Screwdriver", "6in length", 0, "002", 2),
            ("TL003", "Hammer", "16oz", 0, "003", 3)
        ]

        result = locker_db.add_item(cursor=self.db_cursor, list_of_items=items_to_add)
        items_in_db = self.db_cursor.execute("SELECT * FROM items").fetchall()

        self.assertTrue(result, "Test Failed - Multiple Insert Return Value")
        self.assertListEqual(items_to_add, items_in_db, "Test Failed - Multiple Insert")

    def test_add_mixed_valid_invalid_items(self) -> None:
        # Test adding a mix of valid and invalid items to the database.
        items_to_add = [
            ("TL001", "Flathead Screwdriver", "6in length", 0, "001", 1),
            ("TL002", "Phillips Screwdriver", 123, 0, "002", 2),  # Invalid item
            ("TL003", "Hammer", "16oz", 0, "003", 3)
        ]

        result = locker_db.add_item(cursor=self.db_cursor, list_of_items=items_to_add)
        items_in_db = self.db_cursor.execute("SELECT * FROM items").fetchall()

        self.assertFalse(result, "Test Failed - Mixed Insert Return Value")
        self.assertListEqual([], items_in_db, "Test Failed - Mixed Insert")

    def test_sql_error_handling(self):
        locker_db.add_item(self.db_cursor, [("TL001", "Flathead Screwdriver", "6in length", 0, "001", 1)])
        items_to_add = [
            ("TL001", "Duplicate ID", "6in length", 0, "001", 1)
        ]
        result = locker_db.add_item(cursor=self.db_cursor, list_of_items=items_to_add)
        self.assertFalse(result, "Test Failed - SQL Error Handling")
        items_in_db = self.db_cursor.execute("SELECT * FROM items").fetchall()
        self.assertEqual(len(items_in_db), 1, "Test Failed - SQL Error Handling")
