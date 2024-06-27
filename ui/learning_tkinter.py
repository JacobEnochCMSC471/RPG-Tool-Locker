import tkinter as tk
import sqlite3
from database import locker_db
from locker_controller import lock_controls
import logging

# port = "/dev/ttyUSB0" # Used for Linux
port = "COM3"


def unlock_lockers(checkboxes: dict, current_user: tuple):
    global port

    print(len(checkboxes) + 1)

    for counter in range(1, len(checkboxes) + 1):
        if checkboxes[counter].get():
            curr_command = lock_controls.generate_unlock_code(
                header=lock_controls.unlock_header,
                board_addr=1,
                lock_addr=counter,
                function_code=lock_controls.fxn_code_unlock)

            log_msg = "{} with ID {} unlocked locker {}".format(current_user[1], current_user[0], counter)
            logging.info(log_msg)

            cmd_res = lock_controls.send_command(port=port, cmd_type='UI', command=curr_command[1])

    return


class LoginApp:
    def __init__(self, root, rows, cols):
        self.root = root
        self.root.geometry("800x480")
        self.root.resizable(False, False)
        self.root.title("Railway Products Group Tool Locker")
        self.root.overrideredirect(True)  # Remove the title bar
        self.rows = rows
        self.cols = cols

        self.current_user = None
        self.create_login_frame()

        self.show_icon = tk.PhotoImage(file="assets/hide.png")
        self.hide_icon = tk.PhotoImage(file="assets/hide.png")

    def create_login_frame(self):
        self.login_frame = tk.Frame(self.root)
        self.login_frame.pack(pady=10)
        self.login_frame.pack_propagate(False)
        self.login_frame.configure(height=480, width=750, bg="light gray")

        self.create_title_label()
        self.create_user_id_label()
        self.create_user_id_entry()
        self.create_login_button()
        self.create_clear_text_button()  # Add the Clear Text button

    def create_title_label(self):
        title_lbl = tk.Label(self.login_frame, text="Railway Products Group Tool Locker System",
                             font=("Bold", 24, "underline"), background="light gray", foreground="red")
        title_lbl.pack()

    def create_user_id_label(self):
        user_id_lbl = tk.Label(self.login_frame, text="Please Enter User ID:", font=("Bold", 15, "underline"),
                               background="light gray")
        user_id_lbl.pack(pady=10)

    def create_user_id_entry(self):
        self.user_id_entry = tk.Entry(self.login_frame, font=("Bold", 15), width=25, show="*",
                                      highlightcolor="#158aff", highlightthickness=2, highlightbackground="gray")
        self.user_id_entry.focus()
        self.user_id_entry.pack(pady=10)

    def create_login_button(self):
        login_button = tk.Button(self.login_frame, text="Login", command=self.login, width=20)
        login_button.pack(pady=5)

    def create_clear_text_button(self):
        clear_text_button = tk.Button(self.login_frame, text="Clear Text", command=self.clear_text, width=20)
        clear_text_button.pack(pady=5)

    def clear_text(self):
        self.user_id_entry.delete(0, tk.END)

    def login(self):
        emp_id = self.user_id_entry.get()
        conn = sqlite3.connect("test_db_ui.db")
        cursor = conn.cursor()

        employee = locker_db.get_employee(cursor, emp_id)

        if employee:
            self.current_user = employee
            self.show_main_page()
        else:
            self.show_error_message("Employee ID not found!")

        cursor.close()
        conn.close()

    def show_main_page(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        # print(type(self.current_user))

        main_frame = tk.Frame(self.root)
        main_frame.pack(fill="both", expand=True)

        user_details_frame = tk.Frame(main_frame, bg="light blue", width=200, height=50, borderwidth=2, relief="solid")
        user_details_frame.place(x=0, y=0)
        user_details_frame.pack_propagate(False)

        user_details_label = tk.Label(user_details_frame, text=f"Name: {self.current_user[1]}\n"
                                                               f"Access Level: {self.current_user[2]}",
                                      bg="light blue", font=("Arial", 10))
        user_details_label.pack(pady=10, padx=10)

        main_label = tk.Label(main_frame, text="Welcome to the Main Page!", font=("Arial", 20, "underline"))
        main_label.pack(pady=20)

        checkout_button = tk.Button(main_frame, text="Checkout Items", command=self.show_checkout_page, width=20)
        checkout_button.pack(pady=5)

        # Display config buttons only if user's permission level is >= 99
        if self.current_user[2] >= 99:
            user_config_button = tk.Button(main_frame, text="User Config", command=self.user_config, width=20)
            user_config_button.pack(pady=5)

            locker_config_button = tk.Button(main_frame, text="Locker Config", command=self.locker_config, width=20)
            locker_config_button.pack(pady=5)

        logout_button = tk.Button(main_frame, text="Logout", command=self.logout, width=20)
        logout_button.pack(pady=5)

    def show_checkout_page(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        self.menu_frame = tk.Frame(self.root)
        self.menu_frame.pack(fill="both", expand=True)

        checkboxes_frame = tk.Frame(self.menu_frame)
        checkboxes_frame.pack()

        checkboxes = {}
        locker_rows = self.rows  # Example row count, replace with your actual value
        locker_cols = self.cols  # Example column count, replace with your actual value

        locker_number = 1

        # Create labels and checkboxes in a grid
        for row in range(locker_rows):
            for col in range(locker_cols):
                label_text = f"Locker {locker_number}"
                label = tk.Label(checkboxes_frame, text=label_text, font=("Arial", 8))
                label.grid(row=row * 2, column=col, padx=10, pady=5)

                var = tk.IntVar()
                checkbox = tk.Checkbutton(checkboxes_frame, variable=var)
                checkbox.grid(row=row * 2 + 1, column=col, padx=10, pady=5)

                checkboxes[locker_number] = var
                locker_number += 1

        # Button to check the status of checkboxes
        check_button = tk.Button(self.menu_frame, text="Unlock Lockers",
                                 command=lambda: unlock_lockers(checkboxes, self.current_user),
                                 font=("Arial", 10), width=20)
        check_button.pack(pady=10)

        button_back = tk.Button(self.menu_frame, text="Back", command=self.show_main_menu, font=("Arial", 10), width=20)
        button_back.pack(pady=5)


    def checkout_items(self):
        self.show_checkout_page()

    def logout(self):
        self.current_user = None
        for widget in self.root.winfo_children():
            widget.destroy()
        self.create_login_frame()

    def user_config(self):
        print("User Config button clicked")

    def locker_config(self):
        print("Locker Config button clicked")

    def show_error_message(self, message):
        error_label = tk.Label(self.login_frame, text=message, fg="red", bg="light gray")
        error_label.pack()
        self.root.after(3000, error_label.destroy)

    def show_main_menu(self):
        self.show_main_page()


if __name__ == "__main__":
    locker_db.create_database("test_db_ui.db")
    locker_conn = sqlite3.connect("test_db_ui.db")
    locker_cursor = locker_conn.cursor()

    locker_db.add_employee(cursor=locker_cursor, list_of_employees=[("123", "Jake Enoch", 99)])
    root = tk.Tk()
    app = LoginApp(root, rows=6, cols=3)
    root.mainloop()
