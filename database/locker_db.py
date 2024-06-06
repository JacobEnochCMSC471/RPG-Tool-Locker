import sqlite3
from sqlite3 import Error
import os
import logging

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
    # Add items by using list of tuples [()], each individual tuple is one item
    # Ex: [(12345, 'Jake Enoch', 4), (54321, 'Mark Treadwell', 7)]
    try:
        insert_statement = "INSERT INTO employees VALUES (?, ?, ?)"

        if len(list_of_employees) < 1 or len(list_of_employees[0]) == 0:
            print("Attempting to add 0 items to database. Check syntax and try again.\n")
            return False

        count = 1

        for employee in list_of_employees:

            # Short-circuit evaluation instead of using ANDs
            if type(employee[0]) != str or type(employee[1]) != str or type(employee[2]) != int:
                error_msg = "Employee #{} is not formatted correctly. Correct Format is (id (string), name (string), " \
                            "perm_level (int)".format(count)

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
        if type(emp_id) is not str:
            err_msg = "ID is {} when it should be type string. Check formatting and try again.".format(type(emp_id))
            print(err_msg)
            return False

        # Define the SQL delete statement
        delete_statement = 'DELETE FROM employees WHERE id = ?'

        # Execute the command with the supplied user_id
        res = cursor.execute(delete_statement, (emp_id,))

        # Print a message and return false if the ID was not found
        if res.rowcount == 0:
            err_msg = "Employee with ID {} not found! Delete was not performed.".format(emp_id)
            # No commit is needed here since nothing changed in the database
            print(err_msg)
            return False

        # Commit the changes to the database
        cursor.connection.commit()
        return True

    except Error as e:
        cursor.connection.rollback()
        print("Error has occurred! Check logs for answers.")
        print(e)
        return False


def update_employee(cursor: sqlite3.Cursor, emp_id: str, new_details: tuple) -> bool:
    try:
        # Define the SQL update statements
        exec_statement_name = 'UPDATE employees SET name = ? WHERE id = ?'
        exec_statement_perm = 'UPDATE employees SET max_perm_level = ? WHERE id = ?'

        # Execute the commands with the supplied user_id
        cursor.execute(exec_statement_name, (new_details[0], emp_id))
        cursor.execute(exec_statement_perm, (new_details[1], emp_id))

        # Commit the changes to the database
        cursor.connection.commit()
        return True

    except Error as e:
        print("Error has occurred! Check logs for answers.")
        print(e)
        return False


def get_employee(cursor: sqlite3.Cursor, emp_id: str) -> tuple:
    try:
        select_statement = 'SELECT * FROM employees WHERE id = ?'
        cursor.execute(select_statement, (emp_id,))
        search_res = cursor.fetchone()

        if search_res is None:
            print("Employee with ID: {} not found!".format(emp_id))

        return search_res

    except Error as e:
        print("Error has occurred! Check logs for answers.")
        print(e)
        return ()


def get_all_employees(cursor: sqlite3.Cursor) -> list:
    try:
        select_statement = 'SELECT * FROM employees'
        return cursor.execute(select_statement).fetchall()

    except Error as e:
        print("Error has occurred! Check logs for answers.")
        print(e)
        return []


'''
------------------------------EMPLOYEE CRUD FUNCTIONS END------------------------------
'''

'''ldb = "locker.db"

temp_emps = [("12345678", "Jake Enoch", 5)]
create_database(ldb)

db_conn = sqlite3.connect(ldb)
db_cursor = db_conn.cursor()

add_employee(db_cursor, temp_emps)
print(get_all_employees(db_cursor))
print(get_employee(db_cursor, "123"))
update_employee(db_cursor, "12345678", ("John Enoch", 3))
print(get_all_employees(db_cursor))
remove_employee(db_cursor, "12345678")

db_conn.close()
# remove_employee("12345678", "locker.db")'''
