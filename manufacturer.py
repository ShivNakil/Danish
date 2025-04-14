import tkinter as tk
from tkinter import ttk, messagebox
from ttkbootstrap import Style
import serial.tools.list_ports  # Import for fetching COM ports
import serial  # Import pyserial for interaction with COM ports
import os  # Import os for running external scripts
import sqlite3  # Import SQLite for database operations
from tkinter import simpledialog, Toplevel  # Import for date selection dialog and custom date picker dialog

DB_PATH = "d:\\Engineering\\Manish\\manish\\login.db"  # Database path

def connect_db():
    """Connect to the SQLite database."""
    try:
        con = sqlite3.connect(DB_PATH)
        return con
    except Exception as e:
        messagebox.showerror("Database Error", f"Connection failed: {e}")
        return None

def toggle_settings():
    if settings_frame.winfo_ismapped():
        settings_frame.pack_forget()
    else:
        settings_frame.pack(fill='x', padx=10, pady=5)

def on_resize(event):
    if root.winfo_width() < 1000:
        for widget in menubar.winfo_children():
            if isinstance(widget, ttk.Button):
                widget.pack_forget()
    else:
        for widget in menubar.winfo_children():
            if isinstance(widget, ttk.Button):
                widget.pack(side='right', padx=10, pady=10)

root = tk.Tk()
root.title("Dashboard UI")
root.geometry("1200x800")
root.minsize(800, 600)
style = Style("cosmo")

# Configure grid for responsive layout
root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)

# Sidebar with blue background
sidebar = tk.Frame(root, bg='#0047ab', width=250)  # Ensure the background is blue
sidebar.grid(row=0, column=0, sticky='ns')  # Sidebar aligned to the left
sidebar.grid_propagate(False)

# Settings section with darker blue background
settings_frame = tk.Frame(sidebar, bg='#003f7d', padx=10, pady=5)
settings_frame.pack_forget()

# Report Generation Section with even darker blue
ttk.Button(settings_frame, text="Baud Rate", bootstyle='secondary', padding=12).pack(fill='x', padx=5, pady=4)
report_frame = tk.Frame(settings_frame, bg='#002f5d', padx=5, pady=2)
report_frame.pack(fill='x')

# Form fields with consistent styling
labels = ["Start Date", "End Date", "Username"]
for lbl in labels:
    frame = tk.Frame(report_frame, bg='#002f5d')
    frame.pack(fill='x', pady=4)
    tk.Label(frame, text=lbl, bg='#002f5d', fg='white', width=10, anchor='w').pack(side='left')
    ttk.Entry(frame).pack(fill='x', expand=True, padx=5)

ttk.Button(report_frame, text="Submit", bootstyle='success', padding=12).pack(fill='x', padx=5, pady=6)

# Main content area
main_frame = tk.Frame(root)
main_frame.grid(row=0, column=1, sticky='nsew')  # Main frame aligned next to the sidebar
main_frame.grid_rowconfigure(0, weight=0)  # Add a row for the order form
main_frame.grid_rowconfigure(1, weight=1)  # Ensure the table container row takes remaining space
main_frame.grid_columnconfigure(0, weight=1)

# Menubar with blue background
menubar = tk.Frame(main_frame, bg='#0047ab', height=80)
menubar.grid(row=0, column=0, sticky='ew', pady=0)  # Remove any padding above the menu
menubar.grid_propagate(False)

# Fix sidebar toggle functionality
sidebar_visible = False  # Start with sidebar hidden

def toggle_sidebar():
    global sidebar_visible
    if sidebar_visible:
        sidebar.grid_forget()  # Use grid_forget instead of pack_forget
        sidebar_visible = False
    else:
        sidebar.grid(row=0, column=0, sticky='ns')  # Re-grid the sidebar
        sidebar_visible = True

# Add Burger Menu Button to toggle sidebar
burger_btn = tk.Button(menubar, text="☰", font=("Arial", 14, "bold"), bg='#0047ab', fg='white',
                       relief="flat", command=toggle_sidebar)
burger_btn.pack(side="left", padx=10, pady=10)

# Add blue background to the menu
menubar.config(bg='#0047ab')

# Sidebar Buttons with Input Fields
def dummy_action():
    tk.messagebox.showinfo("Info", "This button does nothing yet.")

def logout_user():
    confirm = messagebox.askyesno("Logout", "Are you sure you want to log out?")
    if confirm:
        root.destroy()
        os.system("python d:\\Engineering\\Manish\\manish\\login.py")  # Open login.py after logout

def add_user():
    """Add a new user to the database and display the user table."""
    add_user_window = tk.Toplevel(root)
    add_user_window.title("Add User")
    add_user_window.geometry("600x500")
    add_user_window.config(bg="white")

    # Add User Form
    tk.Label(add_user_window, text="Username:", bg="white", font=("Arial", 10)).grid(row=0, column=0, pady=10, padx=10, sticky="e")
    tk.Label(add_user_window, text="Password:", bg="white", font=("Arial", 10)).grid(row=1, column=0, pady=10, padx=10, sticky="e")
    tk.Label(add_user_window, text="Name:", bg="white", font=("Arial", 10)).grid(row=2, column=0, pady=10, padx=10, sticky="e")
    tk.Label(add_user_window, text="Role:", bg="white", font=("Arial", 10)).grid(row=3, column=0, pady=10, padx=10, sticky="e")

    username_entry = tk.Entry(add_user_window, width=30)
    password_entry = tk.Entry(add_user_window, width=30, show="*")
    name_entry = tk.Entry(add_user_window, width=30)
    role_var = tk.StringVar(value="admin")
    role_dropdown = ttk.Combobox(add_user_window, textvariable=role_var, values=["admin"], state="readonly", width=28)

    username_entry.grid(row=0, column=1, pady=10, padx=10)
    password_entry.grid(row=1, column=1, pady=10, padx=10)
    name_entry.grid(row=2, column=1, pady=10, padx=10)
    role_dropdown.grid(row=3, column=1, pady=10, padx=10)

    def save_user():
        """Save the new user to the database."""
        username = username_entry.get().strip()
        password = password_entry.get().strip()
        name = name_entry.get().strip()
        role = role_var.get()

        if not username or not password or not name or not role:
            messagebox.showerror("Error", "All fields are required.")
            return

        con = connect_db()
        if con:
            cursor = con.cursor()
            try:
                cursor.execute("INSERT INTO users (username, password, name, employee_type) VALUES (?, ?, ?, ?)",
                               (username, password, name, role))
                con.commit()
                messagebox.showinfo("Success", "User added successfully!")
                refresh_users()  # Refresh the user table
            except sqlite3.IntegrityError:
                messagebox.showerror("Error", "Username already exists.")
            finally:
                con.close()

    tk.Button(add_user_window, text="Save", bg="#28A745", fg="white", font=("Arial", 10), command=save_user).grid(row=4, column=0, columnspan=2, pady=20)

    # User Table
    user_table_frame = tk.Frame(add_user_window, bg="white")
    user_table_frame.grid(row=5, column=0, columnspan=2, sticky="nsew", padx=10, pady=10)

    columns = ("ID", "Username", "Name", "Role")
    user_tree = ttk.Treeview(user_table_frame, columns=columns, show="headings")
    for col in columns:
        user_tree.heading(col, text=col)
        user_tree.column(col, anchor="center")

    scroll_y = ttk.Scrollbar(user_table_frame, orient="vertical", command=user_tree.yview)
    scroll_x = ttk.Scrollbar(user_table_frame, orient="horizontal", command=user_tree.xview)
    user_tree.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)

    user_tree.pack(side="left", fill="both", expand=True)
    scroll_y.pack(side="right", fill="y")
    scroll_x.pack(side="bottom", fill="x")

    def refresh_users():
        """Fetch and display all users in the table."""
        for row in user_tree.get_children():
            user_tree.delete(row)
        con = connect_db()
        if con:
            cursor = con.cursor()
            cursor.execute("SELECT id, username, name, employee_type FROM users")
            for row in cursor.fetchall():
                user_tree.insert("", "end", values=row)
            con.close()

    refresh_users()  # Populate the table initially

def set_baud_rate():
    """Set the baud rate based on user input."""
    try:
        baud_rate = int(baud_rate_var.get())
        messagebox.showinfo("Success", f"Baud Rate set to {baud_rate}")
    except ValueError:
        messagebox.showerror("Error", "Invalid Baud Rate. Please enter a number.")

def refresh_com_ports():
    """Refresh the COM port dropdown values dynamically."""
    com_ports = [port.device for port in serial.tools.list_ports.comports()]
    com_port_dropdown["values"] = com_ports
    if com_ports:
        com_port_var.set(com_ports[0])  # Set the first COM port as default
    else:
        com_port_var.set("No COM Ports Available")

def connect_to_com_port():
    """Connect to the selected COM port and display a message."""
    selected_port = com_port_var.get()
    if (selected_port == "No COM Ports Available" or not selected_port):
        messagebox.showerror("Error", "No valid COM port selected.")
        return
    try:
        with serial.Serial(selected_port, baudrate=int(baud_rate_var.get()), timeout=1) as ser:
            messagebox.showinfo("Success", f"Connected to {selected_port} at {ser.baudrate} baud.")
    except serial.SerialException as e:
        messagebox.showerror("Error", f"Failed to connect to {selected_port}: {e}")
    except ValueError:
        messagebox.showerror("Error", "Invalid Baud Rate. Please enter a valid number.")

for text in ["User Logout", "Add User", "Baud Rate", "COM Port"]:
    if text == "User Logout":
        command = logout_user
    elif text == "Add User":
        command = add_user
    elif text == "Baud Rate":
        baud_rate_var = tk.StringVar()
        baud_rate_entry = tk.Entry(sidebar, textvariable=baud_rate_var, width=20)
        baud_rate_entry.pack(fill="x", padx=10, pady=2)
        command = set_baud_rate
    elif text == "COM Port":
        com_port_var = tk.StringVar(value="Select COM Port")
        com_port_dropdown = ttk.Combobox(sidebar, textvariable=com_port_var, state="readonly", width=18)
        com_port_dropdown.pack(fill="x", padx=10, pady=2)
        refresh_com_ports()  # Refresh COM ports when the dropdown is created
        connect_button = tk.Button(sidebar, text="Connect", bg='#003f7d', fg='white', font=("Arial", 10, "bold"),
                                    relief="flat", height=2, command=connect_to_com_port)
        connect_button.pack(fill="x", padx=10, pady=4)
        command = lambda: messagebox.showinfo("Info", f"COM Port selected: {com_port_var.get()}")
    else:
        command = dummy_action

    tk.Button(sidebar, text=text, bg='#003f7d', fg='white', font=("Arial", 10, "bold"),
              relief="flat", height=2, command=command).pack(fill="x", padx=10, pady=8)

# Right-side buttons
ttk.Button(menubar, text="User Database", bootstyle='primary', padding=(15, 10)).pack(side='right', padx=10, pady=10)
ttk.Button(menubar, text="Generate Report", bootstyle='success', padding=(15, 10)).pack(side='right', padx=10, pady=10)

def create_orders_table():
    """Create the orders table in the database if it doesn't exist."""
    con = connect_db()
    if con:
        cursor = con.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                orderId INTEGER PRIMARY KEY AUTOINCREMENT,
                orderBy TEXT NOT NULL,
                componentName TEXT NOT NULL,
                orderDate TEXT NOT NULL,
                dueDate TEXT NOT NULL,
                lowAllowed INTEGER NOT NULL,
                peakAllowed INTEGER NOT NULL,
                quantity INTEGER NOT NULL
            )
        """)
        con.commit()
        con.close()

create_orders_table()  # Ensure the table exists

def create_parameters_table():
    """Create the parametersDetails table in the database if it doesn't exist."""
    con = connect_db()
    if con:
        cursor = con.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS parametersDetails (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                orderId INTEGER NOT NULL,
                parameterName TEXT NOT NULL,
                low REAL,
                high REAL,
                FOREIGN KEY (orderId) REFERENCES orders(orderId)
            )
        """)
        con.commit()
        con.close()

create_parameters_table()  # Ensure the table exists

def submit_order():
    """Submit a new order to the database."""
    order_by = order_by_entry.get().strip()
    component_name = component_name_entry.get().strip()
    order_date = order_date_entry.get().strip()
    due_date = due_date_entry.get().strip()
    low_allowed = low_allowed_entry.get().strip()
    peak_allowed = peak_allowed_entry.get().strip()
    quantity = quantity_entry.get().strip()

    if not all([order_by, component_name, order_date, due_date, low_allowed, peak_allowed, quantity]):
        messagebox.showerror("Error", "All fields are required.")
        return

    try:
        low_allowed = float(low_allowed)  # Allow float values
        peak_allowed = float(peak_allowed)  # Allow float values
        quantity = int(quantity)
    except ValueError:
        messagebox.showerror("Error", "Low Allowed and Peak Allowed must be numbers, and Quantity must be an integer.")
        return

    con = connect_db()
    if con:
        cursor = con.cursor()
        cursor.execute("""
            INSERT INTO orders (orderBy, componentName, orderDate, dueDate, lowAllowed, peakAllowed, quantity)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (order_by, component_name, order_date, due_date, low_allowed, peak_allowed, quantity))
        con.commit()
        con.close()
        messagebox.showinfo("Success", "Order submitted successfully!")
        refresh_orders()
        clear_order_form()

def clear_order_form():
    """Clear the order input form."""
    order_by_entry.delete(0, tk.END)
    component_name_entry.delete(0, tk.END)
    order_date_entry.delete(0, tk.END)
    due_date_entry.delete(0, tk.END)
    low_allowed_entry.delete(0, tk.END)
    peak_allowed_entry.delete(0, tk.END)
    quantity_entry.delete(0, tk.END)

def refresh_orders():
    """Fetch and display all orders in the table."""
    for row in orders_tree.get_children():
        orders_tree.delete(row)
    con = connect_db()
    if con:
        cursor = con.cursor()
        cursor.execute("SELECT * FROM orders")
        for row in cursor.fetchall():
            orders_tree.insert("", "end", values=row)
        con.close()

def view_order():
    """View the details of the selected order in a new frame."""
    selected_item = orders_tree.selection()
    if not selected_item:
        messagebox.showerror("Error", "No order selected.")
        return

    order_details = orders_tree.item(selected_item, "values")
    if not order_details:
        messagebox.showerror("Error", "Unable to fetch order details.")
        return

    # Create a new frame to display order details
    view_order_window = Toplevel(root)
    view_order_window.title("Order Details")
    view_order_window.geometry("600x600")
    view_order_window.config(bg="white")

    labels = ["Order ID", "Order By", "Component Name", "Order Date", "Due Date", "Low Allowed", "Peak Allowed", "Quantity"]
    for i, label in enumerate(labels):
        tk.Label(view_order_window, text=f"{label}:", bg="white", font=("Arial", 10, "bold")).grid(row=i, column=0, sticky="w", padx=10, pady=5)
        tk.Label(view_order_window, text=order_details[i], bg="white", font=("Arial", 10)).grid(row=i, column=1, sticky="w", padx=10, pady=5)

    # Frame for parameter inputs
    parameter_frame = tk.Frame(view_order_window, bg="white")
    parameter_frame.grid(row=len(labels), column=0, columnspan=2, pady=10, padx=10, sticky="nsew")

    tk.Label(parameter_frame, text="Parameter Name", bg="white", font=("Arial", 10, "bold")).grid(row=0, column=0, padx=5, pady=5)

    parameter_entries = []

    def add_parameter_row():
        """Add a new row for parameter input."""
        row = len(parameter_entries) + 1
        parameter_name_entry = tk.Entry(parameter_frame, width=20)
        parameter_name_entry.grid(row=row, column=0, padx=5, pady=5)
        parameter_entries.append(parameter_name_entry)

    def save_parameters():
        """Save all parameter details to the database."""
        for parameter_name_entry in parameter_entries:
            parameter_name = parameter_name_entry.get().strip()

            if not parameter_name:
                messagebox.showerror("Error", "All fields are required for each parameter.")
                return

            con = connect_db()
            if con:
                cursor = con.cursor()
                try:
                    cursor.execute("""
                        INSERT INTO parametersDetails (orderId, parameterName)
                        VALUES (?, ?)
                    """, (order_details[0], parameter_name))
                    con.commit()
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to save parameter: {e}")
                finally:
                    con.close()

        messagebox.showinfo("Success", "All parameters saved successfully!")
        refresh_parameters()

    def delete_parameter():
        """Delete the selected parameter from the database."""
        selected_item = parameter_tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "No parameter selected.")
            return

        parameter_id = parameter_tree.item(selected_item, "values")[0]
        con = connect_db()
        if con:
            cursor = con.cursor()
            try:
                cursor.execute("DELETE FROM parametersDetails WHERE id = ?", (parameter_id,))
                con.commit()
                messagebox.showinfo("Success", "Parameter deleted successfully!")
                refresh_parameters()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete parameter: {e}")
            finally:
                con.close()

    def refresh_parameters():
        """Fetch and display all parameters for the selected order."""
        for row in parameter_tree.get_children():
            parameter_tree.delete(row)
        con = connect_db()
        if con:
            cursor = con.cursor()
            cursor.execute("SELECT id, parameterName FROM parametersDetails WHERE orderId = ?", (order_details[0],))
            for row in cursor.fetchall():
                parameter_tree.insert("", "end", values=row)
            con.close()

    # Add initial row for parameter input
    add_parameter_row()

    # Buttons to add more rows and save parameters
    tk.Button(view_order_window, text="Add Parameter", bg="#007BFF", fg="white", font=("Arial", 10), command=add_parameter_row).grid(row=len(labels) + 1, column=0, pady=10)
    tk.Button(view_order_window, text="Save Parameters", bg="#28A745", fg="white", font=("Arial", 10), command=save_parameters).grid(row=len(labels) + 1, column=1, pady=10)

    # Parameter table
    parameter_table_frame = tk.Frame(view_order_window, bg="white")
    parameter_table_frame.grid(row=len(labels) + 2, column=0, columnspan=2, pady=10, padx=10, sticky="nsew")

    parameter_columns = ("ID", "Parameter Name")
    parameter_tree = ttk.Treeview(parameter_table_frame, columns=parameter_columns, show="headings")
    for col in parameter_columns:
        parameter_tree.heading(col, text=col)
        parameter_tree.column(col, anchor="center", width=150)

    scroll_y = ttk.Scrollbar(parameter_table_frame, orient="vertical", command=parameter_tree.yview)
    parameter_tree.configure(yscrollcommand=scroll_y.set)

    parameter_tree.pack(side="left", fill="both", expand=True)
    scroll_y.pack(side="right", fill="y")

    tk.Button(view_order_window, text="Delete Parameter", bg="#DC3545", fg="white", font=("Arial", 10), command=delete_parameter).grid(row=len(labels) + 3, column=0, columnspan=2, pady=10)

    refresh_parameters()

# Order Input Form
order_form_frame = tk.Frame(main_frame, bg="white", padx=10, pady=10)
order_form_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=10)

tk.Label(order_form_frame, text="Order By:", bg="white", font=("Arial", 10)).grid(row=0, column=0, sticky="w", padx=5)
order_by_entry = tk.Entry(order_form_frame, width=15)
order_by_entry.grid(row=0, column=1, padx=5)

tk.Label(order_form_frame, text="Component Name:", bg="white", font=("Arial", 10)).grid(row=0, column=2, sticky="w", padx=5)
component_name_entry = tk.Entry(order_form_frame, width=15)
component_name_entry.grid(row=0, column=3, padx=5)

tk.Label(order_form_frame, text="Order Date:", bg="white", font=("Arial", 10)).grid(row=0, column=4, sticky="w", padx=5)
order_date_entry = tk.Entry(order_form_frame, width=15)
order_date_entry.grid(row=0, column=5, padx=5)

tk.Label(order_form_frame, text="Due Date:", bg="white", font=("Arial", 10)).grid(row=0, column=7, sticky="w", padx=5)
due_date_entry = tk.Entry(order_form_frame, width=15)
due_date_entry.grid(row=0, column=8, padx=5)

tk.Label(order_form_frame, text="Low Allowed:", bg="white", font=("Arial", 10)).grid(row=1, column=0, sticky="w", padx=5)
low_allowed_entry = tk.Entry(order_form_frame, width=15)
low_allowed_entry.grid(row=1, column=1, padx=5)

tk.Label(order_form_frame, text="Peak Allowed:", bg="white", font=("Arial", 10)).grid(row=1, column=2, sticky="w", padx=5)
peak_allowed_entry = tk.Entry(order_form_frame, width=15)
peak_allowed_entry.grid(row=1, column=3, padx=5)

tk.Label(order_form_frame, text="Quantity:", bg="white", font=("Arial", 10)).grid(row=1, column=4, sticky="w", padx=5)
quantity_entry = tk.Entry(order_form_frame, width=15)
quantity_entry.grid(row=1, column=5, padx=5)

tk.Button(order_form_frame, text="Submit", bg="#28A745", fg="white", font=("Arial", 10), command=submit_order).grid(row=1, column=6, columnspan=2, pady=10, padx=5)

# Orders Table
orders_table_frame = tk.Frame(main_frame, bg="white", padx=10, pady=10)
orders_table_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)

columns = ("Order ID", "Order By", "Component Name", "Order Date", "Due Date", "Low Allowed", "Peak Allowed", "Quantity")
orders_tree = ttk.Treeview(orders_table_frame, columns=columns, show="headings")
for col in columns:
    orders_tree.heading(col, text=col)
    orders_tree.column(col, anchor="center", width=100)

scroll_y = ttk.Scrollbar(orders_table_frame, orient="vertical", command=orders_tree.yview)
scroll_x = ttk.Scrollbar(orders_table_frame, orient="horizontal", command=orders_tree.xview)
orders_tree.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)

orders_tree.pack(side="left", fill="both", expand=True)
scroll_y.pack(side="right", fill="y")
scroll_x.pack(side="bottom", fill="x")

refresh_orders()  # Populate the table initially

# Add a "View" button to the orders table
view_button = tk.Button(orders_table_frame, text="View Order", bg="#007BFF", fg="white", font=("Arial", 10), command=view_order)
view_button.pack(side="top", pady=10)

main_frame.grid_rowconfigure(0, weight=0)  # Ensure the menubar row has no extra space
main_frame.grid_rowconfigure(1, weight=0)  # Add a row for the order form
main_frame.grid_rowconfigure(2, weight=1)  # Ensure the table container row takes remaining space

menubar.grid(row=0, column=0, sticky='ew', pady=0)  # Place the menubar in the first row
order_form_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=10)  # Place the order form in the second row
orders_table_frame.grid(row=2, column=0, sticky="nsew", padx=20, pady=10)  # Place the orders table in the third row

root.bind('<Configure>', on_resize)
root.mainloop()
