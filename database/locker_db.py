import sqlite3
from sqlite3 import Error
import os


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


def create_database(db_name: str) -> None:
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

    except sqlite3.OperationalError:
        print("Database already initialized.\n")
        return

    except sqlite3.Error as e:
        print("Fatal error has occurred! Check logs.")
        print(e)
        return


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


def update_employee(emp_id: str, db_name: str) -> bool:
    return False


# Utility function to retrieve all employees from the table
def get_all_employees(db_name: str) -> bool:
    try:
        if isSqlite3Db(db_name):
            # Create a connection + cursor
            db_conn = sqlite3.connect(db_name)
            db_cursor = db_conn.cursor()

            # Define the SQL delete statement
            select_statement = 'SELECT * FROM employees'

            # Execute the command with the supplied user_id
            db_cursor.execute(select_statement)

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


temp_emps = [("12345", "Jake Enoch", 5)]
temp_employees_fr = [("0123456789", "Jake Enoch", 4)]
create_database("locker.db")
add_employee(temp_emps, "locker.db")

# remove_employee("12345", "locker.db")
