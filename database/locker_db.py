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

        # Check if the database file exists already
        if os.path.isfile(db_name):
            return False

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


# Create a new employee and add it to the database
def add_employee(list_of_employees: list, db_name: str) -> bool:
    # Add items by using list of tuples [()], each individual tuple is one item
    # Ex: [(12345, 'Jake Enoch', 4), (54321, 'Mark Treadwell', 7)]

    try:
        if isSqlite3Db(db_name):
            db_conn = sqlite3.connect(db_name)
            db_cursor = db_conn.cursor()

            insert_statement = "INSERT INTO employees values(?,?,?)"

            if len(list_of_employees) < 1 or len(list_of_employees[0]) == 0:
                print("Attempting to add 0 items to database. Check syntax and try again.\n")
                return False

            elif len(list_of_employees) == 1:
                db_cursor.execute(insert_statement, list_of_employees.pop())

            else:
                db_cursor.executemany(insert_statement, list_of_employees)

            db_conn.commit()
            db_conn.close()

            return True

        else:
            print("Existing database not found. Initialize databases before attempting to modify them.\n")
            return False

    except Error as e:
        print(e)
        return False


def remove_employee(emp_id: str, db_name: str) -> bool:
    try:
        if isSqlite3Db(db_name):
            # Create a connection + cursor
            db_conn = sqlite3.connect(db_name)
            db_cursor = db_conn.cursor()

            # Define the SQL delete statement
            delete_statement = 'DELETE FROM employees WHERE id = ?'

            # Execute the command with the supplied user_id
            db_cursor.execute(delete_statement, (emp_id,))

            # Commit the changes to the database + close the connection
            db_conn.commit()
            db_conn.close()

            return True

        else:
            print("Existing database not found. Initialize databases before attempting to modify them.\n")
            return False

    except Error as e:
        print("Error has occurred! Check logs for answers.")
        print(e)
        return False


# new_details has format [name, perm_level]
def update_employee(emp_id: str, db_name: str, new_details: list) -> bool:
    try:
        if isSqlite3Db(db_name):
            # Create a connection + cursor
            db_conn = sqlite3.connect(db_name)
            db_cursor = db_conn.cursor()

            # Define the SQL delete statement
            exec_statement_name = 'UPDATE employees SET name = ? WHERE id = ?'
            exec_statement_perm = 'UPDATE employees SET max_perm_level = ? WHERE id = ?'

            # Execute the command with the supplied user_id
            print(new_details[0])
            db_cursor.execute(exec_statement_name, (new_details[0], emp_id))
            db_cursor.execute(exec_statement_perm, (new_details[1], emp_id))

            # Commit the changes to the database + close the connection
            db_conn.commit()
            db_conn.close()

            return True

        else:
            print("Existing database not found. Initialize databases before attempting to modify them.\n")
            return False

    except Error as e:
        print("Error has occurred! Check logs for answers.")
        print(e)
        return False


# Utility function to retrieve all employees from the table
def get_all_employees(db_name: str) -> list:
    try:
        if isSqlite3Db(db_name):
            # Create a connection + cursor
            db_conn = sqlite3.connect(db_name)
            db_cursor = db_conn.cursor()

            # Define the SQL delete statement
            select_statement = 'SELECT * FROM employees'

            # Execute the command with the supplied user_id
            search_res = db_cursor.execute(select_statement).fetchall()

            # Commit the changes to the database + close the connection
            db_conn.commit()
            db_conn.close()

            return search_res

        else:
            print("Existing database not found. Initialize databases before attempting to modify them.\n")
            return []

    except Error as e:
        print("Error has occurred! Check logs for answers.")

        return []


'''
------------------------------EMPLOYEE CRUD FUNCTIONS END------------------------------
'''

'''ldb = "locker.db"

temp_emps = [("12345678", "Jake Enoch", 5)]
create_database(ldb)
add_employee(temp_emps, ldb)
get_all_employees(ldb)
update_employee("12345678", ldb, ["John Enoch", 3])
remove_employee("12345", ldb)
remove_employee("12345678", ldb)
# remove_employee("12345678", "locker.db")'''
