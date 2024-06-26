import sqlite3
from sqlite3 import Error
import os
import logging
from typing import Union

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO, filename='database.log')


def isSqlite3Db(db: str) -> bool:
    # Source: https://stackoverflow.com/questions/12932607/how-to-check-if-a-sqlite3-database-exists-in-python

    if not os.path.isfile(db):
        return False

    sz = os.path.getsize(db)

    # file is empty, give benefit of the doubt that its sqlite
    # New sqlite3 files created in recent libraries are empty!
    if sz == 0:
        return True

    # SQLite database file header is 100 bytes
    if sz < 100:
        return False

    # Validate file header
    with open(db, 'rb') as fd:
        header = fd.read(100)

    return header[:16] == b'SQLite format 3\x00'


def create_database(db_name: str) -> bool:
    try:
        # Connect to the SQLite database (or create it if it doesn't exist)
        conn = sqlite3.connect(db_name)

        # Create a cursor object to access database functions
        cursor = conn.cursor()

        # Create table for employees
        cursor.execute(
            '''CREATE TABLE IF NOT EXISTS employees (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                max_perm_level INTEGER NOT NULL
            )'''
        )

        # Create table for locker doors
        cursor.execute(
            '''CREATE TABLE IF NOT EXISTS locker_doors (
                locker_number INTEGER PRIMARY KEY,
                locker_perm_level INTEGER NOT NULL
            )'''
        )

        # Create table for items
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS items (
                item_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                min_perm_level INTEGER NOT NULL,
                borrowed_by TEXT,
                locker_number INTEGER,
                FOREIGN KEY(borrowed_by) REFERENCES employees(id),
                FOREIGN KEY(locker_number) REFERENCES locker_doors(locker_number)
            )
        ''')

        # Commit the changes and close the connection
        conn.commit()
        conn.close()

        return True

    except sqlite3.OperationalError:
        print("Database already initialized.\n")
        return False

    except sqlite3.Error as e:
        print("Fatal error has occurred! Check logs.")
        print(e)
        return False


def wipe_table(db_name: str, table: str) -> None:
    db_conn = sqlite3.connect(db_name)
    db_cursor = db_conn.cursor()

    db_cursor.execute(f'DELETE FROM {table}')
    db_conn.commit()
    db_conn.close()


'''
------------------------------EMPLOYEE CRUD FUNCTIONS------------------------------
'''


def add_employee(cursor: sqlite3.Cursor, list_of_employees: list) -> bool:
    # Add employees by using list of tuples [()], each individual tuple is one item
    # Ex: [(12345, 'Jake Enoch', 4), (54321, 'Mark Treadwell', 7)]
    try:
        insert_statement = "INSERT INTO employees VALUES (?, ?, ?)"

        if len(list_of_employees) < 1 or len(list_of_employees[0]) == 0:
            print("Attempting to add 0 items to database. Check syntax and try again.\n")
            return False

        count = 1

        for employee in list_of_employees:

            if not (isinstance(employee[0], str) and isinstance(employee[1], str) and isinstance(employee[2], int) and
                    len(employee) == 3):
                error_msg = f"Employee #{count} is not formatted correctly. Correct Format is (id (string), " \
                            "name (string) perm_level (int))"

                print(error_msg)
                print("No employees added.")

                cursor.connection.rollback()

                return False

            cursor.execute(insert_statement, employee)
            count += 1

        cursor.connection.commit()
        return True

    except Error as e:
        print(e)
        return False


def remove_employee(cursor: sqlite3.Cursor, emp_id: str) -> bool:
    try:

        # Make sure that the emp_id is a string
        if not isinstance(emp_id, str):
            err_msg = f"ID is {type(emp_id)} when it should be type string. Check formatting and try again."
            print(err_msg)
            return False

        # Define the SQL delete statement
        delete_statement = "DELETE FROM employees WHERE id = ?"

        # Execute the command with the supplied user_id
        res = cursor.execute(delete_statement, (emp_id,))

        # Print a message and return false if the ID was not found
        if res.rowcount == 0:
            err_msg = f"Employee with ID {emp_id} not found! Delete was not performed."
            # No commit is needed here since nothing changed in the database
            print(err_msg)
            return False

        # Commit the changes to the database
        cursor.connection.commit()
        return True

    except sqlite3.Error as e:
        print("Error has occurred! Check logs for answers.")
        print(e)
        return False


def update_employee(cursor: sqlite3.Cursor, emp_id: str, new_details: tuple) -> bool:
    try:
        if not (isinstance(new_details[0], str) and isinstance(new_details[1], int) and len(new_details) == 2):
            err_msg = f"Employee with ID {emp_id} not updated! Use a tuple with types (str, int) to update employee!"
            print(err_msg)
            return False

        # Search for the employee and verify that it exists before trying to update
        search_emp_statement = "SELECT * FROM employees WHERE id = ?"

        search_res = cursor.execute(search_emp_statement, (emp_id,))

        # If the employee doesn't exist, print msg and return False
        if search_res.fetchone() is None:
            err_msg = f"Employee with ID {emp_id} was not found! Only attempt to update employees that exist!"
            print(err_msg)
            return False

        # Define the SQL update statements
        exec_statement = "UPDATE employees SET name = ?, max_perm_level = ? WHERE id = ?"

        # Execute the commands with the supplied user_id
        cursor.execute(exec_statement, (new_details[0], new_details[1], emp_id))

        # Commit the changes to the database
        cursor.connection.commit()

    except sqlite3.Error as e:
        print("Error has occurred! Check logs for answers.")
        print(e)
        return False

    return True


def get_employee(cursor: sqlite3.Cursor, emp_id: str) -> Union[tuple, None]:
    try:
        select_statement = "SELECT * FROM employees WHERE id = ?"

        cursor.execute(select_statement, (emp_id,))
        search_res = cursor.fetchone()

        if search_res is None:
            print(f"Employee with ID: {emp_id} not found!")

        return search_res

    except sqlite3.Error as e:
        print("Error has occurred! Check logs for answers.")
        print(e)
        return None


def get_all_employees(cursor: sqlite3.Cursor) -> list:
    try:
        select_statement = 'SELECT * FROM employees'
        return cursor.execute(select_statement).fetchall()

    except sqlite3.Error as e:
        print("Error has occurred! Check logs for answers.")
        print(e)
        return []


'''
------------------------------EMPLOYEE CRUD FUNCTIONS END------------------------------
'''

'''
------------------------------ITEM CRUD FUNCTIONS BEGIN------------------------------
'''


def add_item(cursor: sqlite3.Cursor, list_of_items: list[tuple[str, str, str, int, str, int]]) -> bool:
    try:
        if len(list_of_items) == 0:
            print("Item list is empty! Ensure that you're adding items correctly!")
            return False

        insert_statement = "INSERT INTO items VALUES (?, ?, ?, ?, ?, ?)"
        count = 1

        for item in list_of_items:
            if len(item) == 0:
                print("Attempting to add empty item to table. Check syntax and try again!")
                cursor.connection.rollback()
                return False

            if len(item) != 6:
                print(f"Incorrect formatting for item {count}. Check formatting is (str, str, str, int, str, int)!")
                cursor.connection.rollback()
                return False

            if not (isinstance(item[0], str) and isinstance(item[1], str) and isinstance(item[2], str) and
                    isinstance(item[3], int) and isinstance(item[4], str) and isinstance(item[5], int)):
                print(f"Incorrect formatting for item {count}. Check formatting is (str, str, str, int, str, int)!")
                cursor.connection.rollback()
                return False

            item = (item[0].upper(), item[1], item[2], item[3], item[4], item[5])

            print(item)

            cursor.execute(insert_statement, item)
            count += 1

        cursor.connection.commit()
        return True

    except sqlite3.Error as e:
        print(e)
        cursor.connection.rollback()
        return False


def remove_item(cursor: sqlite3.Cursor, item_id: str) -> bool:
    try:
        if not isinstance(item_id, str):
            item_id_type = str(type(item_id))
            err_msg = f"Item ID {item_id} is type {item_id_type} when it should be type string. Check formatting and try again."
            print(err_msg)
            return False

        delete_statement = "DELETE FROM items WHERE item_id = ?"

        res = cursor.execute(delete_statement, (item_id,))

        if res.rowcount == 0:
            err_msg = f"Item with ID {item_id} not found! Delete was not performed."
            print(err_msg)
            return False

        cursor.connection.commit()

    except sqlite3.Error as e:
        print("Error has occurred! Check logs for answers.")
        print(e)
        return False

    return True


def update_item(cursor: sqlite3.Cursor, item_id: str, new_details: tuple) -> bool:
    try:
        if (not isinstance(new_details[0], str) or
                not isinstance(new_details[1], str) or
                not isinstance(new_details[2], int) or
                not isinstance(new_details[3], str) or
                not isinstance(new_details[4], int)):
            print("Item with ID {item_id} not updated! Use a tuple with types (str, str, int, str, str) to update!")
            return False

        search_item_statement = "SELECT * FROM items WHERE item_id = ?"

        search_res = cursor.execute(search_item_statement, (item_id,))

        if search_res.fetchone() is None:
            err_msg = f"Item with ID {item_id} not found! Only attempt to update items that exist!"
            print(err_msg)
            return False

        exec_statement = "UPDATE items SET name = ?, description = ?, min_perm_level = ?, borrowed_by = ?, locker_number = ? WHERE item_id = ?"

        cursor.execute(exec_statement,
                       (new_details[0], new_details[1], new_details[2], new_details[3], new_details[4], item_id))

        cursor.connection.commit()

    except sqlite3.Error as e:
        print("Error has occurred! Check logs for answers.")
        print(e)

        return False

    return True


def get_item(cursor: sqlite3.Cursor, item_id: str) -> Union[tuple, None]:
    try:
        select_statement = "SELECT * FROM items WHERE item_id = ?"

        cursor.execute(select_statement, (item_id,))
        search_res = cursor.fetchone()

        if search_res is None:
            print("Item with ID: {} not found!".format(item_id))
            return None

        return search_res

    except sqlite3.Error as e:
        print("Error has occurred! Check logs for answers.")
        print(e)
        return None


def get_all_items(cursor: sqlite3.Cursor) -> list:
    try:
        select_statement = 'SELECT * FROM items'
        return cursor.execute(select_statement).fetchall()

    except sqlite3.Error as e:
        print("Error has occurred! Check logs for answers.")
        print(e)
        return []

'''
------------------------------ITEM CRUD FUNCTIONS END------------------------------
'''
