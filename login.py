import tkinter as tk
from tkinter import messagebox
import subprocess
import sqlite3  # Import SQLite library

# Main application window
root = tk.Tk()
root.title("Login - InThink Technologies")
root.geometry("800x500")
root.config(bg="#F5F5F5")

# Frame for the login box
login_frame = tk.Frame(root, bg="#0052CC", bd=0, relief="flat")
login_frame.place(relx=0.5, rely=0.5, anchor="center", width=300, height=400)

# User Icon (Placeholder using Label)
user_label = tk.Label(login_frame, text="👤", font=("Arial", 60), bg="#0052CC", fg="white")
user_label.pack(pady=20)

# Username Label
username_label = tk.Label(login_frame, text="USER", font=("Arial", 14, "bold"), bg="#0052CC", fg="white")
username_label.pack(pady=5)

# Clear placeholder text on focus
def clear_placeholder(event, entry, placeholder):
    if entry.get() == placeholder:
        entry.delete(0, tk.END)
        entry.config(fg="black")

# Restore placeholder text on focus out
def restore_placeholder(event, entry, placeholder):
    if entry.get() == "":
        entry.insert(0, placeholder)
        entry.config(fg="#C0C0C0")

# Username entry
username_entry = tk.Entry(login_frame, font=("Arial", 14), bd=0, justify="center")
username_entry.insert(0, "User Name")  # Updated placeholder
username_entry.config(fg="#C0C0C0")
username_entry.bind("<FocusIn>", lambda event: clear_placeholder(event, username_entry, "User Name"))
username_entry.bind("<FocusOut>", lambda event: restore_placeholder(event, username_entry, "User Name"))
username_entry.pack(pady=10, padx=20, ipady=5)

# Password entry
password_entry = tk.Entry(login_frame, font=("Arial", 14), bd=0, justify="center", show="*")
password_entry.insert(0, "Password")  # Updated placeholder
password_entry.config(fg="#C0C0C0")
password_entry.bind("<FocusIn>", lambda event: clear_placeholder(event, password_entry, "Password"))
password_entry.bind("<FocusOut>", lambda event: restore_placeholder(event, password_entry, "Password"))
password_entry.pack(pady=10, padx=20, ipady=5)

# Login button
login_button = tk.Button(login_frame, text="LOGIN", font=("Arial", 12, "bold"), bg="#FFFFFF", fg="#0052CC", width=15, command=lambda: login())
login_button.pack(pady=20)

# Forgot password link
forgot_password = tk.Label(login_frame, text="Forgot password?", fg="white", bg="#0052CC", font=("Arial", 10, "italic"), cursor="hand2")
forgot_password.pack(pady=5)

# Menu icon as a placeholder
menu_label = tk.Label(root, text="☰", font=("Arial", 24), bg="#F5F5F5", fg="#0052CC")
menu_label.place(x=20, y=20)

# Company logo text
logo_label = tk.Label(root, text="InThink\nTechnologies", fg="#333333", bg="#F5F5F5", font=("Arial", 14, "bold"), justify="right")
logo_label.place(x=650, y=20)

# Function to launch OperatorScreen
def launch_operator_screen():
    subprocess.Popen(["python", "d:\\Engineering\\manish\\Manish\\op.py"])

# Function to launch HamburgerMenuApp
def launch_supervisor_screen():
    subprocess.Popen(["python", "d:\\Engineering\\manish\\Manish\\supervisor.py"])

def launch_admin_screen():
    subprocess.Popen(["python", "d:\\Engineering\\manish\\Manish\\admin.py"])

def launch_manufacturer_screen():
    subprocess.Popen(["python", "d:\\Engineering\\manish\\Manish\\manufacturer.py"])

# Initialize SQLite database
def initialize_database():
    conn = sqlite3.connect("d:\\Engineering\\Manish\\manish\\login.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            employee_type TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

# Modified login function
def login():
    username = username_entry.get()
    password = password_entry.get()
    conn = sqlite3.connect("d:\\Engineering\\Manish\\manish\\login.db")
    cursor = conn.cursor()
    cursor.execute("SELECT employee_type FROM users WHERE username = ? AND password = ?", (username, password))
    result = cursor.fetchone()
    conn.close()
    
    if result:
        employee_type = result[0]
        root.destroy()
        if employee_type == "operator":
            launch_operator_screen()
        elif employee_type == "supervisor":
            launch_supervisor_screen()
        elif employee_type == "admin":
            launch_admin_screen()
        elif employee_type == "manufacturer":
            launch_manufacturer_screen()
        else:
            messagebox.showerror("Error", "Unknown employee type.")
    else:
        messagebox.showerror("Login Failed", "Invalid username or password.")

# Initialize database on application start
initialize_database()

# Bind Enter key to login button
root.bind("<Return>", lambda event: login())

root.mainloop()
