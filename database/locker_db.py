import sqlite3
from sqlite3 import Error
import os


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


def add_employees(employees: list, db_name: str) -> bool:
    # Add employee(s) by using a list of tuples. Each tuple represents an employee. Works for single or multiple people.

    # Create a connection to a database
    db_conn = sqlite3.connect(db_name)

    db_cursor = db_conn.cursor()

    try:
        for employee in employees:
            if len(employee) == 0:
                db_cursor.execute("INSERT INTO employees values(?,?,?)", employee)

    except sqlite3.ProgrammingError as e:
        print("Attempting to Insert Empty Item into DB - check syntax and try again.\n")


def remove_employee(id: str) -> bool:
    return False


def update_employee(id: str) -> bool:
    return False


temp_emps = [(12345, "Jake Enoch", 5), ()]
temp_employees_fr = [("0123456789", "Jake Enoch", 4)]
create_database("locker.db")
add_employees(temp_emps, "locker.db")
