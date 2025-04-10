import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3  # Use SQLite instead of pyodbc

# DB config
DB_PATH = "d:\\Engineering\\Manish\\manish\\login.db"

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
root.geometry("900x600")
root.config(bg="white")

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
        # Pack sidebar to the left (before main area in packing order)
        sidebar.pack(side="left", fill="y")
        # Re-pack main area to maintain proper layout
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

# Create User button with special command
tk.Button(sidebar, text="Create User", bg=BLUE2, fg=WHITE, font=("Arial", 10, "bold"),
          relief="flat", height=2, 
          command=lambda: [form_frame.pack(pady=20), btn_frame.pack(pady=10)]).pack(fill="x", padx=10, pady=8)

# Other buttons remain with dummy_action
for text in ["User Logout", "Settings", "Baud Rate"]:
    btn = tk.Button(sidebar, text=text, bg=BLUE2, fg=WHITE, font=("Arial", 10, "bold"), 
                   relief="flat", height=2, command=dummy_action)
    btn.pack(fill="x", padx=10, pady=8)

# ---------- User Form ----------
form_frame = tk.Frame(main_area, bg=WHITE)
btn_frame = tk.Frame(main_area, bg=WHITE)
tree_frame = tk.Frame(main_area, bg=WHITE)

tk.Label(form_frame, text="Username:", bg=WHITE, fg=BLUE1, font=("Arial", 10)).grid(row=0, column=0, sticky="e", pady=5)
tk.Label(form_frame, text="Password:", bg=WHITE, fg=BLUE1, font=("Arial", 10)).grid(row=1, column=0, sticky="e", pady=5)
tk.Label(form_frame, text="First Name:", bg=WHITE, fg=BLUE1, font=("Arial", 10)).grid(row=2, column=0, sticky="e", pady=5)
tk.Label(form_frame, text="Last Name:", bg=WHITE, fg=BLUE1, font=("Arial", 10)).grid(row=3, column=0, sticky="e", pady=5)

username_entry = tk.Entry(form_frame, width=30)
password_entry = tk.Entry(form_frame, width=30, show="*")
fname_entry = tk.Entry(form_frame, width=30)
lname_entry = tk.Entry(form_frame, width=30)

username_entry.grid(row=0, column=1, padx=10)
password_entry.grid(row=1, column=1, padx=10)
fname_entry.grid(row=2, column=1, padx=10)
lname_entry.grid(row=3, column=1, padx=10)

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
    lname = lname_entry.get().strip()

    if not uname or not pwd or not fname or not lname:
        messagebox.showerror("Error", "All fields are required.")
        return

    con = connect_db()
    if con:
        cursor = con.cursor()
        try:
            cursor.execute("INSERT INTO users (username, password, name, employee_type) VALUES (?, ?, ?, ?)", 
                           (uname, pwd, f"{fname} {lname}", "user"))
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
    lname_entry.delete(0, tk.END)
    password_entry.delete(0, tk.END)  # Must be re-entered

    username_entry.insert(0, values[1])
    fname, lname = values[2].split(" ", 1) if " " in values[2] else (values[2], "")
    fname_entry.insert(0, fname)
    lname_entry.insert(0, lname)

    # Show Save button
    save_btn.grid(row=0, column=4, padx=5)

def save_user():
    uid = user_id.get()
    uname = username_entry.get().strip()
    pwd = password_entry.get().strip()
    fname = fname_entry.get().strip()
    lname = lname_entry.get().strip()

    if not uid or not uname or not pwd or not fname or not lname:
        messagebox.showerror("Error", "All fields are required.")
        return

    con = connect_db()
    if con:
        cursor = con.cursor()
        cursor.execute("UPDATE users SET username=?, password=?, name=?, employee_type=? WHERE id=?",
                       (uname, pwd, f"{fname} {lname}", "user", uid))
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
    lname_entry.delete(0, tk.END)
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

columns = ("ID", "Username", "First Name", "Last Name")
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
        lname_entry.delete(0, tk.END)
        password_entry.delete(0, tk.END)

        username_entry.insert(0, values[1])
        fname, lname = values[2].split(" ", 1) if " " in values[2] else (values[2], "")
        fname_entry.insert(0, fname)
        lname_entry.insert(0, lname)

tree.bind("<<TreeviewSelect>>", on_tree_select)

hide_user_interface() 
refresh_users()
tree_frame.pack(padx=10, pady=20, fill="both", expand=True)  # Show table immediately
refresh_users()  # Load data
root.mainloop()
