#  Image Attribution for eye icons: icons created by th studio
import tkinter as tk
import sqlite3
from database import locker_db


class LoginApp:
    def __init__(self, root):
        self.root = root
        self.root.geometry("800x480")
        self.root.resizable(False, False)
        self.root.title("Railway Products Group Tool Locker")

        self.current_user = None
        self.create_login_frame()

    def create_login_frame(self):
        self.login_frame = tk.Frame(self.root)
        self.login_frame.pack(pady=10)
        self.login_frame.pack_propagate(False)
        self.login_frame.configure(height=480, width=750, bg="light gray")

        self.create_title_label()
        self.create_user_id_label()
        self.create_user_id_entry()
        self.create_login_button()

    def create_title_label(self):
        title_lbl = tk.Label(self.login_frame, text="Railway Products Group Tool Locker System",
                             font=("Bold", 24, "underline"), background="light gray", foreground="red")
        title_lbl.pack()

    def create_user_id_label(self):
        user_id_lbl = tk.Label(self.login_frame, text="Please Enter User ID:", font=("Bold", 12, "underline"),
                               background="light gray")
        user_id_lbl.pack(pady=25)

    def create_user_id_entry(self):
        self.user_id_entry = tk.Entry(self.login_frame, font=("Bold", 15), width=25, show="*",
                                      highlightcolor="#158aff", highlightthickness=2, highlightbackground="gray")
        self.user_id_entry.focus()
        self.user_id_entry.pack()

    def create_login_button(self):
        login_button = tk.Button(self.login_frame, text="Login", command=self.login)
        login_button.pack()

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

        main_frame = tk.Frame(self.root)
        main_frame.pack(fill="both", expand=True)

        user_details_frame = tk.Frame(main_frame, bg="light blue", width=200, height=100)
        user_details_frame.place(x=10, y=10)
        user_details_frame.pack_propagate(False)

        user_details_label = tk.Label(user_details_frame, text=f"User ID: {self.current_user[0]}\n"
                                                               f"Name: {self.current_user[1]}\n"
                                                               f"Access Level: {self.current_user[2]}",
                                      bg="light blue", font=("Arial", 10))
        user_details_label.pack(pady=10, padx=10)

        main_label = tk.Label(main_frame, text="Welcome to the Main Page!")
        main_label.pack(pady=20)

        checkout_button = tk.Button(main_frame, text="Checkout Items", command=self.checkout_items)
        checkout_button.pack(pady=5)

        logout_button = tk.Button(main_frame, text="Logout", command=self.logout)
        logout_button.pack(pady=5)

        # Display config buttons only if user's permission level is >= 99
        if self.current_user[2] >= 99:
            user_config_button = tk.Button(main_frame, text="User Config", command=self.user_config)
            user_config_button.pack(pady=5)

            locker_config_button = tk.Button(main_frame, text="Locker Config", command=self.locker_config)
            locker_config_button.pack(pady=5)

    def checkout_items(self):
        print("Checkout Items button clicked")

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


if __name__ == "__main__":
    root = tk.Tk()
    app = LoginApp(root)
    root.mainloop()