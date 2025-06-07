import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3  # Use SQLite instead of pyodbc
import os
import sys  # Ensure sys is imported

# Update database path to handle PyInstaller's temporary directory
if getattr(sys, 'frozen', False):  # Check if running as a PyInstaller bundle
    BASE_DIR = sys._MEIPASS  # Temporary directory created by PyInstaller
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DB_PATH = os.path.join(BASE_DIR, "login.db")

try:
    import serial.tools.list_ports  # Import for COM port detection
except ModuleNotFoundError:
    messagebox.showerror("Module Error", "The 'pyserial' module is not installed. Please install it using 'pip install pyserial'.")
    exit()

# DB config
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "login.db")

def connect_db():
    try:
        con = sqlite3.connect(DB_PATH)
        return con
    except Exception as e:
        messagebox.showerror("Database Error", f"Connection failed: {e}")
        return None

# ---------- GUI ----------
root = tk.Tk()
root.title("Admin Dashboard - User Management")
root.state("zoomed")  # Maximize the window
root.config(bg="white")  # Set consistent background color

# ---------- Colors ----------
BLUE1 = "#0047AB"
BLUE2 = "#0066FF"
WHITE = "#FFFFFF"

# ---------- Top Bar with Burger Menu ----------
top_bar = tk.Frame(root, bg=BLUE2, height=40)
top_bar.pack(side="top", fill="x")

# ---------- Global Variables ----------
user_id = tk.StringVar()
sidebar_visible = False  # Start with sidebar hidden

# ---------- Frames ----------
# Main container that will hold both sidebar and main area
main_container = tk.Frame(root)
main_container.pack(fill="both", expand=True)

# Create both frames but don't pack them yet
sidebar = tk.Frame(main_container, bg=BLUE1, width=180)
main_area = tk.Frame(main_container, bg=WHITE)

# Pack main area first (this is key for left-side behavior)
main_area.pack(side="left", fill="both", expand=True)

# Burger Menu Button
def toggle_sidebar():
    global sidebar_visible
    if sidebar_visible:
        sidebar.pack_forget()
        sidebar_visible = False
    else:
        sidebar.pack(side="left", fill="y")
        main_area.pack_forget()
        main_area.pack(side="left", fill="both", expand=True)
        sidebar_visible = True

burger_btn = tk.Button(top_bar, text="☰", font=("Arial", 14, "bold"), bg=BLUE2, fg=WHITE,
                      relief="flat", command=toggle_sidebar)
burger_btn.pack(side="left", padx=10)


def dummy_action():
    messagebox.showinfo("Info", "This button does nothing yet.")

def show_user_management():
    # Show the form and buttons when "Create User" is clicked
    form_frame.pack(pady=20)
    btn_frame.pack(pady=10)
    refresh_users()  # Refresh the table data

# ---------- Sidebar Buttons ----------
# Replace the sidebar buttons creation with this:
def show_user_interface():
    form_frame.pack(pady=20)
    btn_frame.pack(pady=10)
    tree_frame.pack(padx=10, pady=20, fill="both", expand=True)
    refresh_users()

def logout_user():
    confirm = messagebox.askyesno("Logout", "Are you sure you want to log out?")
    if confirm:
        root.destroy()
        import subprocess
        subprocess.Popen(["python", os.path.join(BASE_DIR, "login.py")])
        # messagebox.showinfo("Logged Out", "You have been logged out successfully.")

# Sidebar Buttons with Input Fields
for text in ["User Logout", "Add User"]:
    if text == "User Logout":
        command = logout_user
    elif text == "Add User":
        command = show_user_interface
    else:
        command = dummy_action

    tk.Button(sidebar, text=text, bg='#0047AB', fg='white', font=("Arial", 10, "bold"),  # Updated color
              relief="flat", height=2, command=command).pack(fill="x", padx=10, pady=8)

# ---------- User Form ----------
form_frame = tk.Frame(main_area, bg=WHITE)
btn_frame = tk.Frame(main_area, bg=WHITE)
tree_frame = tk.Frame(main_area, bg=WHITE)

tk.Label(form_frame, text="Username:", bg=WHITE, fg=BLUE1, font=("Arial", 10)).grid(row=0, column=0, sticky="e", pady=5)
tk.Label(form_frame, text="Password:", bg=WHITE, fg=BLUE1, font=("Arial", 10)).grid(row=1, column=0, sticky="e", pady=5)
tk.Label(form_frame, text="Name:", bg=WHITE, fg=BLUE1, font=("Arial", 10)).grid(row=2, column=0, sticky="e", pady=5)

username_entry = tk.Entry(form_frame, width=30)
password_entry = tk.Entry(form_frame, width=30, show="*")
fname_entry = tk.Entry(form_frame, width=30)

username_entry.grid(row=0, column=1, padx=10)
password_entry.grid(row=1, column=1, padx=10)
fname_entry.grid(row=2, column=1, padx=10)

tk.Label(form_frame, text="Role:", bg=WHITE, fg=BLUE1, font=("Arial", 10)).grid(row=3, column=0, sticky="e", pady=5)
role_var = tk.StringVar(value="operator")  # Default value
role_dropdown = ttk.Combobox(form_frame, textvariable=role_var, values=["operator", "supervisor"], state="readonly", width=28)
role_dropdown.grid(row=3, column=1, padx=10)

# ---------- DB Actions ----------
def refresh_users():
    for row in tree.get_children():
        tree.delete(row)
    con = connect_db()
    if con:
        cursor = con.cursor()
        cursor.execute("SELECT id, username, name, employee_type FROM users")
        for row in cursor.fetchall():
            tree.insert("", "end", values=row)
        con.close()

def create_user():
    uname = username_entry.get().strip()
    pwd = password_entry.get().strip()
    fname = fname_entry.get().strip()
    role = role_var.get()

    if not uname or not pwd or not fname or not role:
        messagebox.showerror("Error", "All fields are required.")
        return

    con = connect_db()
    if con:
        cursor = con.cursor()
        try:
            cursor.execute("INSERT INTO users (username, password, name, employee_type) VALUES (?, ?, ?, ?)", 
                           (uname, pwd, fname, role))
            con.commit()
            refresh_users()
            clear_form()
            messagebox.showinfo("Success", "User created successfully!")
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Username already exists.")
        con.close()

def edit_user():
    selected = tree.focus()
    if not selected:
        messagebox.showerror("Error", "Select a user to edit.")
        return

    values = tree.item(selected, "values")
    user_id.set(values[0])  # Save ID for update
    username_entry.delete(0, tk.END)
    fname_entry.delete(0, tk.END)
    password_entry.delete(0, tk.END)  # Must be re-entered
    role_var.set(values[3])  # Set role dropdown value

    username_entry.insert(0, values[1])
    fname_entry.insert(0, values[2])

    # Show Save button
    save_btn.grid(row=0, column=4, padx=5)

def save_user():
    uid = user_id.get()
    uname = username_entry.get().strip()
    pwd = password_entry.get().strip()
    fname = fname_entry.get().strip()
    role = role_var.get()

    if not uid or not uname or not pwd or not fname or not role:
        messagebox.showerror("Error", "All fields are required.")
        return

    con = connect_db()
    if con:
        cursor = con.cursor()
        cursor.execute("UPDATE users SET username=?, password=?, name=?, employee_type=? WHERE id=?",
                       (uname, pwd, fname, role, uid))
        con.commit()
        con.close()
        refresh_users()
        clear_form()
        messagebox.showinfo("Success", "User updated successfully!")
        save_btn.grid_forget()  # Hide Save button after done

def delete_user():
    selected = tree.focus()
    if not selected:
        messagebox.showerror("Error", "Select a user to delete.")
        return

    values = tree.item(selected, "values")
    uid = values[0]

    confirm = messagebox.askyesno("Confirm", f"Are you sure you want to delete user ID {uid}?")
    if confirm:
        con = connect_db()
        if con:
            cursor = con.cursor()
            cursor.execute("DELETE FROM users WHERE id=?", (uid,))
            con.commit()
            con.close()
            refresh_users()
            clear_form()
            messagebox.showinfo("Deleted", "User deleted successfully!")

def clear_form():
    username_entry.delete(0, tk.END)
    password_entry.delete(0, tk.END)
    fname_entry.delete(0, tk.END)
    user_id.set("")
    save_btn.grid_forget()

# ---------- Buttons ----------
btn_frame = tk.Frame(main_area, bg=WHITE)

tk.Button(btn_frame, text="Create", bg=BLUE2, fg=WHITE, width=12, command=create_user).grid(row=0, column=0, padx=5)
tk.Button(btn_frame, text="Edit", bg=BLUE2, fg=WHITE, width=12, command=edit_user).grid(row=0, column=1, padx=5)
tk.Button(btn_frame, text="Delete", bg=BLUE2, fg=WHITE, width=12, command=delete_user).grid(row=0, column=2, padx=5)
tk.Button(btn_frame, text="Clear", bg=WHITE, fg=BLUE2, width=12, command=clear_form).grid(row=0, column=3, padx=5)

# Save button (initially hidden)
save_btn = tk.Button(btn_frame, text="Save", bg="#28A745", fg="white", width=12, command=save_user)

# ---------- Treeview (User Table) ----------
tree_frame = tk.Frame(main_area, bg=WHITE)
tree_frame.pack(padx=10, pady=20, fill="both", expand=True)
def hide_user_interface():
    form_frame.pack_forget()
    btn_frame.pack_forget()
    tree_frame.pack_forget()

columns = ("ID", "Username", "Name", "Role")
tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
for col in columns:
    tree.heading(col, text=col)
    tree.column(col, anchor="center")

tree.pack(fill="both", expand=True)

# ---------- Select Row to Form ----------
def on_tree_select(event):
    selected = tree.focus()
    if selected:
        values = tree.item(selected, "values")
        username_entry.delete(0, tk.END)
        fname_entry.delete(0, tk.END)
        password_entry.delete(0, tk.END)
        role_var.set(values[3])  # Set role dropdown value

        username_entry.insert(0, values[1])
        fname_entry.insert(0, values[2])

tree.bind("<<TreeviewSelect>>", on_tree_select)

# ---------- Baud Rate and COM Port Popup ----------
def open_baud_com_popup():
    """Open a popup window for Baud Rate and COM Port settings."""
    popup = tk.Toplevel(root)
    popup.title("Baud Rate and COM Port Settings")
    popup.geometry("300x200")
    popup.config(bg=WHITE)

    tk.Label(popup, text="Enter Baud Rate:", bg=WHITE, fg=BLUE1, font=("Arial", 10)).grid(row=0, column=0, sticky="e", pady=10, padx=10)
    baud_rate_var = tk.StringVar()
    baud_rate_entry = tk.Entry(popup, textvariable=baud_rate_var, width=20)
    baud_rate_entry.grid(row=0, column=1, padx=10)

    tk.Label(popup, text="Select COM Port:", bg=WHITE, fg=BLUE1, font=("Arial", 10)).grid(row=1, column=0, sticky="e", pady=10, padx=10)
    com_port_var = tk.StringVar(value="Select COM Port")
    com_port_dropdown = ttk.Combobox(popup, textvariable=com_port_var, state="readonly", width=18)
    com_port_dropdown.grid(row=1, column=1, padx=10)
    refresh_com_ports_dropdown(com_port_dropdown, com_port_var)

    tk.Button(popup, text="Save", bg=BLUE2, fg=WHITE, width=12, 
              command=lambda: messagebox.showinfo("Info", f"Baud Rate: {baud_rate_var.get()}, COM Port: {com_port_var.get()}")).grid(row=2, column=0, columnspan=2, pady=20)

def refresh_com_ports_dropdown(dropdown, var):
    """Refresh the COM port dropdown values dynamically."""
    com_ports = [port.device for port in serial.tools.list_ports.comports()]
    dropdown["values"] = com_ports
    if com_ports:
        var.set(com_ports[0])  # Set the first COM port as default
    else:
        var.set("No COM Ports Available")

# Add a button to open the popup in the sidebar
tk.Button(sidebar, text="Communication", bg='#0047AB', fg='white', font=("Arial", 10, "bold"),
          relief="flat", height=2, command=open_baud_com_popup).pack(fill="x", padx=10, pady=8)

hide_user_interface() 
refresh_users()
tree_frame.pack(padx=10, pady=20, fill="both", expand=True)  # Show table immediately
refresh_users()  # Load data
root.mainloop()
