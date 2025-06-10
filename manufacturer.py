import tkinter as tk
from tkinter import ttk, messagebox
from ttkbootstrap import Style
import serial.tools.list_ports  # Import for fetching COM ports
import serial  # Import pyserial for interaction with COM ports
import os  # Import os for running external scripts
import sqlite3  # Import SQLite for database operations
from tkinter import simpledialog, Toplevel  # Import for date selection dialog and custom date picker dialog
import sys  # Ensure sys is imported
import pandas as pd  # Add this import at the top

# Update database path to handle PyInstaller's temporary directory
if getattr(sys, 'frozen', False):  # Check if running as a PyInstaller bundle
    BASE_DIR = sys._MEIPASS  # Temporary directory created by PyInstaller
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DB_PATH = os.path.join(BASE_DIR, "login.db")

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
root.title("Manufacturer Dashboard")
root.state("zoomed")  # Maximize the window
root.configure(bg="white")  # Set consistent background color
style = Style("cosmo")

# Configure grid for responsive layout
root.grid_rowconfigure(0, weight=0)  # Menubar row (fixed height)
root.grid_rowconfigure(1, weight=1)  # Main content row (sidebar + main_frame)
root.grid_columnconfigure(1, weight=1)

# Menubar with blue background
menubar = tk.Frame(root, bg='#0047AB', height=80)  # Updated color
menubar.grid(row=0, column=0, columnspan=2, sticky='ew', pady=0)
menubar.grid_propagate(False)
main_frame = tk.Frame(root)
main_frame.grid(row=1, column=1, sticky='nsew')  # Main frame aligned next to the sidebar
main_frame.grid_rowconfigure(0, weight=0)  # Add a row for the order form
main_frame.grid_rowconfigure(1, weight=1)  # Ensure the table container row takes remaining space
main_frame.grid_columnconfigure(0, weight=1)

# Sidebar with blue background, now below menubar
sidebar = tk.Frame(root, bg='#0047AB', width=250)
sidebar.grid_propagate(False)

# Settings section with darker blue background
settings_frame = tk.Frame(sidebar, bg='black', padx=10, pady=5)  # Set to black for consistency
settings_frame.pack_forget()

# Report Generation Section with even darker blue
ttk.Button(settings_frame, text="Baud Rate", bootstyle='secondary', padding=12).pack(fill='x', padx=5, pady=4)
report_frame = tk.Frame(settings_frame, bg='black', padx=5, pady=2)  # Set to black for consistency
report_frame.pack(fill='x')

# Form fields with consistent styling
labels = ["Start Date", "End Date", "Username"]
for lbl in labels:
    frame = tk.Frame(report_frame, bg='black')  # Set to black
    frame.pack(fill='x', pady=4)
    tk.Label(frame, text=lbl, bg='black', fg='white', width=10, anchor='w').pack(side='left')  # Set to black
    ttk.Entry(frame).pack(fill='x', expand=True, padx=5)

ttk.Button(report_frame, text="Submit", bootstyle='success', padding=12).pack(fill='x', padx=5, pady=6)

# Fix sidebar toggle functionality
sidebar_visible = False  # Start with sidebar hidden

def toggle_sidebar():
    global sidebar_visible
    if sidebar_visible:
        sidebar.grid_forget()
        sidebar_visible = False
    else:
        # Place sidebar in row 1, column 0 (below menubar)
        sidebar.grid(row=1, column=0, sticky='ns')
        sidebar_visible = True

# Add Burger Menu Button to toggle sidebar in the menubar at the left
burger_btn = tk.Button(
    menubar, text="☰", font=("Arial", 14, "bold"),
    bg="#5597F3", fg="white", relief="flat", borderwidth=0,
    activebackground="#5597F3", activeforeground="white",
    command=toggle_sidebar
)
burger_btn.pack(side='left', padx=(5, 15), pady=10)

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
    add_user_window.geometry("900x500")
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
    if (com_ports):
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

def open_com_port_popup():
    """Open a popup window for setting baud rate and COM port."""
    popup = Toplevel(root)
    popup.title("COM Port Settings")
    popup.geometry("400x300")
    popup.config(bg="white")

    tk.Label(popup, text="Baud Rate:", bg="white", font=("Arial", 10)).pack(pady=10)
    baud_rate_var = tk.StringVar()
    baud_rate_entry = tk.Entry(popup, textvariable=baud_rate_var, width=20)
    baud_rate_entry.pack(pady=5)

    tk.Label(popup, text="COM Port:", bg="white", font=("Arial", 10)).pack(pady=10)
    com_port_var = tk.StringVar(value="Select COM Port")
    com_port_dropdown = ttk.Combobox(popup, textvariable=com_port_var, state="readonly", width=18)
    com_port_dropdown.pack(pady=5)

    def refresh_com_ports():
        """Refresh the COM port dropdown values dynamically."""
        com_ports = [port.device for port in serial.tools.list_ports.comports()]
        com_port_dropdown["values"] = com_ports
        if com_ports:
            com_port_var.set(com_ports[0])  # Set the first COM port as default
        else:
            com_port_var.set("No COM Ports Available")

    refresh_com_ports()

    def connect_to_com_port():
        """Connect to the selected COM port and display a message."""
        selected_port = com_port_var.get()
        if selected_port == "No COM Ports Available" or not selected_port:
            messagebox.showerror("Error", "No valid COM port selected.")
            return
        try:
            with serial.Serial(selected_port, baudrate=int(baud_rate_var.get()), timeout=1) as ser:
                messagebox.showinfo("Success", f"Connected to {selected_port} at {ser.baudrate} baud.")
        except serial.SerialException as e:
            messagebox.showerror("Error", f"Failed to connect to {selected_port}: {e}")
        except ValueError:
            messagebox.showerror("Error", "Invalid Baud Rate. Please enter a valid number.")

    tk.Button(popup, text="Connect", bg="#28A745", fg="white", font=("Arial", 10), command=connect_to_com_port).pack(pady=10)
    tk.Button(popup, text="Refresh Ports", bg="#007BFF", fg="white", font=("Arial", 10), command=refresh_com_ports).pack(pady=5)

# Add a button to open the popup in the sidebar
tk.Button(
    sidebar,
    text="Communication",
    bg="#5597F3",
    fg="white",
    font=("Arial", 10, "bold"),
    relief="flat",
    borderwidth=0,
    highlightthickness=0,
    activebackground="#5597F3",
    activeforeground="white",
    height=2,
    command=open_com_port_popup
).pack(fill="x", padx=10, pady=(80, 8))

for text in ["User Logout", "Add User"]:
    if text == "User Logout":
        command = logout_user
    elif text == "Add User":
        command = add_user
    else:
        command = dummy_action

    tk.Button(
        sidebar,
        text=text,
        bg="#5597F3",
        fg="white",
        font=("Arial", 10, "bold"),
        relief="flat",
        borderwidth=0,
        activebackground="#5597F3",
        activeforeground="white",
        height=2,
        command=command
    ).pack(fill="x", padx=10, pady=8)

def open_main_database():
    """Open a window displaying all records from measuredValues with Excel-like headers."""
    db_window = tk.Toplevel(root)
    db_window.title("Main Database")
    db_window.state("zoomed")  # Maximize the window
    db_window.config(bg="white")

    excel_columns = ["A", "B", "C", "D", "E", "F", "G"]
    data_columns = ["Sr.No.", "Date", "Time", "Operator", "Part No.", "Parameter Name", "Value"]
    col_width = 140

    # Use a container frame for both header and treeview
    container = tk.Frame(db_window, bg="white")
    container.pack(fill="both", expand=True)  # removed padx/pady

    # Header row
    header_frame = tk.Frame(container, bg="white")
    header_frame.grid(row=0, column=0, sticky="nsew")
    for idx, col in enumerate(excel_columns):
        lbl = tk.Label(
            header_frame, text=col, bg="white", fg="black",
            font=("Arial", 10, "bold"),
            borderwidth=1, relief="solid", anchor="center",  # border for cell
            highlightbackground="#cccccc", highlightcolor="#cccccc", highlightthickness=1
        )
        lbl.grid(row=0, column=idx, sticky="nsew", ipadx=1, ipady=4)
        header_frame.grid_columnconfigure(idx, weight=1)  # removed minsize

    style = ttk.Style()
    style.configure("Treeview.Heading", font=("Arial", 10, "bold"))
    style.configure("Excel.Treeview", rowheight=24, font=("Arial", 10))
    style.map("Excel.Treeview", background=[("selected", "#CCE5FF")])
    style.layout("Excel.Treeview", [
        ('Treeview.field', {'sticky': 'nswe', 'children': [
            ('Treeview.padding', {'sticky': 'nswe', 'children': [
                ('Treeview.treearea', {'sticky': 'nswe'})
            ]})
        ]})
    ])
    style.configure("Excel.Treeview", bordercolor="#cccccc", borderwidth=1)
    style.configure("Treeview", bordercolor="#cccccc", borderwidth=1)

    tree = ttk.Treeview(container, columns=data_columns, show="headings", style="Excel.Treeview")
    for idx, col in enumerate(data_columns):
        tree.heading(col, text=col)
        tree.column(col, anchor="center", stretch=True)  # stretch True
    tree.grid(row=1, column=0, sticky="nsew")
    container.grid_rowconfigure(1, weight=1)
    container.grid_columnconfigure(0, weight=1)

    tree.tag_configure('evenrow', background='#F7F7F7')
    tree.tag_configure('oddrow', background='#FFFFFF')

    # Fetch and display all records from measuredValues table
    con = connect_db()
    if con:
        cursor = con.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS measuredValues (
                orderId TEXT NOT NULL,
                componentSerialNumber INTEGER NOT NULL,
                componentName TEXT NOT NULL,
                partNumber TEXT NOT NULL,
                parameterName TEXT NOT NULL,
                operatorName TEXT NOT NULL,
                date TEXT NOT NULL,
                time TEXT NOT NULL,
                value REAL NOT NULL,
                isValid TEXT NOT NULL,
                PRIMARY KEY (orderId, componentSerialNumber, parameterName)
            )
        """)
        cursor.execute("""
            SELECT date, time, operatorName, partNumber, parameterName, value
            FROM measuredValues
            ORDER BY date, time, operatorName, partNumber, parameterName
        """)
        rows = cursor.fetchall()
        for idx, row in enumerate(rows, start=1):
            date, time_, operator, part_no, param_name, value = row
            tag = 'evenrow' if idx % 2 == 0 else 'oddrow'
            tree.insert("", "end", values=(idx, date, time_, operator, part_no, param_name, value), tags=(tag,))
        con.close()

    # Add Save and Print buttons below the table
    def save_to_excel():
        data = []
        for row_id in tree.get_children():
            data.append(tree.item(row_id)['values'])
        df = pd.DataFrame(data, columns=data_columns)
        from tkinter import filedialog
        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*")]
        )
        if file_path:
            df.to_excel(file_path, index=False)
            messagebox.showinfo("Exported", f"Data exported to {file_path}")

    def print_table():
        import tempfile
        import os
        data = []
        for row_id in tree.get_children():
            data.append(tree.item(row_id)['values'])
        df = pd.DataFrame(data, columns=data_columns)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp:
            df.to_excel(tmp.name, index=False)
            tmp_path = tmp.name
        # Send the file to the default printer
        if sys.platform == "win32":
            # Windows: use the 'print' verb
            os.startfile(tmp_path, "print")
        else:
            # macOS/Linux: try lpr
            os.system(f"lpr '{tmp_path}'")

    btn_frame = tk.Frame(container, bg="white")
    btn_frame.grid(row=2, column=0, sticky="e", pady=8, padx=8)
    # save_btn = tk.Button(btn_frame, text="Save as Excel", bg="#007BFF", fg="white", font=("Arial", 10, "bold"), command=save_to_excel)
    # save_btn.pack(side="right", padx=(0, 16))  # Increased gap between buttons
    # print_btn = tk.Button(btn_frame, text="Print", bg="#28A745", fg="white", font=("Arial", 10, "bold"), command=print_table)
    # print_btn.pack(side="right")

    print_btn = tk.Button(
                btn_frame, text="Print", bg="#0047ab", fg="white", font=("Arial", 11),
                command=print_table
            )
    print_btn.pack(side="left", padx=10)

    save_btn = tk.Button(
                btn_frame, text="Save as Excel", bg="#28A745", fg="white", font=("Arial", 11),
                command=save_to_excel
            )
    save_btn.pack(side="left", padx=10)

def open_generate_report_popup():
    """Open a popup to select filters and display filtered measuredValues."""
    popup = tk.Toplevel(root)
    popup.title("Generate Report")
    popup.geometry("400x350")
    popup.config(bg="white")

    # --- Filter fields ---
    tk.Label(popup, text="Start Date (YYYY-MM-DD):", bg="white").pack(pady=(15, 2))
    start_date_var = tk.StringVar()
    tk.Entry(popup, textvariable=start_date_var).pack()

    tk.Label(popup, text="End Date (YYYY-MM-DD):", bg="white").pack(pady=(15, 2))
    end_date_var = tk.StringVar()
    tk.Entry(popup, textvariable=end_date_var).pack()

    # Fetch operator names and part numbers for dropdowns
    con = connect_db()
    operator_names = []
    part_numbers = []
    if con:
        cursor = con.cursor()
        cursor.execute("SELECT DISTINCT operatorName FROM measuredValues")
        operator_names = [row[0] for row in cursor.fetchall()]
        cursor.execute("SELECT DISTINCT partNumber FROM measuredValues")
        part_numbers = [row[0] for row in cursor.fetchall()]
        con.close()

    tk.Label(popup, text="Operator Name:", bg="white").pack(pady=(15, 2))
    operator_var = tk.StringVar()
    operator_dropdown = ttk.Combobox(popup, textvariable=operator_var, values=[""] + operator_names, state="readonly")
    operator_dropdown.pack()

    tk.Label(popup, text="Part Number:", bg="white").pack(pady=(15, 2))
    partno_var = tk.StringVar()
    partno_dropdown = ttk.Combobox(popup, textvariable=partno_var, values=[""] + part_numbers, state="readonly")
    partno_dropdown.pack()

    def show_report():
        # Build SQL query based on selected filters
        query = """
            SELECT date, time, operatorName, partNumber, parameterName, value
            FROM measuredValues
            WHERE 1=1
        """
        params = []
        if start_date_var.get():
            query += " AND date >= ?"
            params.append(start_date_var.get())
        if end_date_var.get():
            query += " AND date <= ?"
            params.append(end_date_var.get())
        if operator_var.get():
            query += " AND operatorName = ?"
            params.append(operator_var.get())
        if partno_var.get():
            query += " AND partNumber = ?"
            params.append(partno_var.get())
        query += " ORDER BY date, time, operatorName, partNumber, parameterName"

        # Display results in a new window
        result_win = tk.Toplevel(root)
        result_win.title("Report Results")
        result_win.state("zoomed")  # Maximize the window
        result_win.config(bg="white")

        excel_columns = ["A", "B", "C", "D", "E", "F", "G"]
        data_columns = ["Sr.No.", "Date", "Time", "Operator", "Part No.", "Parameter Name", "Value"]
        col_width = 140

        # Use a container frame for both header and treeview
        container = tk.Frame(result_win, bg="white")
        container.pack(fill="both", expand=True)  # removed padx/pady

        # Header row
        header_frame = tk.Frame(container, bg="white")
        header_frame.grid(row=0, column=0, sticky="nsew")
        for idx, col in enumerate(excel_columns):
            lbl = tk.Label(
                header_frame, text=col, bg="white", fg="black",
                font=("Arial", 10, "bold"),
                borderwidth=1, relief="solid", anchor="center",  # border for cell
                highlightbackground="#cccccc", highlightcolor="#cccccc", highlightthickness=1
            )
            lbl.grid(row=0, column=idx, sticky="nsew", ipadx=1, ipady=4)
            header_frame.grid_columnconfigure(idx, weight=1)  # removed minsize

        style = ttk.Style()
        style.configure("Treeview.Heading", font=("Arial", 10, "bold"))
        style.configure("Excel.Treeview", rowheight=24, font=("Arial", 10))
        style.map("Excel.Treeview", background=[("selected", "#CCE5FF")])
        style.layout("Excel.Treeview", [
            ('Treeview.field', {'sticky': 'nswe', 'children': [
                ('Treeview.padding', {'sticky': 'nswe', 'children': [
                    ('Treeview.treearea', {'sticky': 'nswe'})
                ]})
            ]})
        ])
        style.configure("Excel.Treeview", bordercolor="#cccccc", borderwidth=1)
        style.configure("Treeview", bordercolor="#cccccc", borderwidth=1)

        tree = ttk.Treeview(container, columns=data_columns, show="headings", style="Excel.Treeview")
        for idx, col in enumerate(data_columns):
            tree.heading(col, text=col)
            tree.column(col, anchor="center", stretch=True)  # stretch True
        tree.grid(row=1, column=0, sticky="nsew")
        container.grid_rowconfigure(1, weight=1)
        container.grid_columnconfigure(0, weight=1)

        tree.tag_configure('evenrow', background='#F7F7F7')
        tree.tag_configure('oddrow', background='#FFFFFF')

        con = connect_db()
        if con:
            cursor = con.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            for idx, row in enumerate(rows, start=1):
                date, time_, operator, part_no, param_name, value = row
                tag = 'evenrow' if idx % 2 == 0 else 'oddrow'
                tree.insert("", "end", values=(idx, date, time_, operator, part_no, param_name, value), tags=(tag,))
            con.close()

        # Add Save and Print buttons below the table
        def save_to_excel():
            data = []
            for row_id in tree.get_children():
                data.append(tree.item(row_id)['values'])
            df = pd.DataFrame(data, columns=data_columns)
            from tkinter import filedialog
            file_path = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*")]
            )
            if file_path:
                df.to_excel(file_path, index=False)
                messagebox.showinfo("Exported", f"Data exported to {file_path}")

        def print_table():
            import tempfile
            import os
            data = []
            for row_id in tree.get_children():
                data.append(tree.item(row_id)['values'])
            df = pd.DataFrame(data, columns=data_columns)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp:
                df.to_excel(tmp.name, index=False)
                tmp_path = tmp.name
            # Send the file to the default printer
            if sys.platform == "win32":
                # Windows: use the 'print' verb
                os.startfile(tmp_path, "print")
            else:
                # macOS/Linux: try lpr
                os.system(f"lpr '{tmp_path}'")

        btn_frame = tk.Frame(container, bg="white")
        btn_frame.grid(row=2, column=0, sticky="e", pady=8, padx=8)
        # save_btn = tk.Button(btn_frame, text="Save as Excel", bg="#007BFF", fg="white", font=("Arial", 10, "bold"), command=save_to_excel)
        # save_btn.pack(side="right", padx=(0, 16))  # Increased gap between buttons
        # print_btn = tk.Button(btn_frame, text="Print", bg="#28A745", fg="white", font=("Arial", 10, "bold"), command=print_table)
        # print_btn.pack(side="right")

        print_btn = tk.Button(
                btn_frame, text="Print", bg="#0047ab", fg="white", font=("Arial", 11),
                command=print_table
            )
        print_btn.pack(side="left", padx=10)

        save_btn = tk.Button(
                btn_frame, text="Save as Excel", bg="#28A745", fg="white", font=("Arial", 11),
                command=save_to_excel
            )
        save_btn.pack(side="left", padx=10)

        popup.destroy()

    tk.Button(popup, text="Show Report", bg="#28A745", fg="white", font=("Arial", 11), command=show_report).pack(pady=25)
     

# Right-side buttons
# ttk.Button(menubar, text="User Database", bootstyle='primary', padding=(15, 10)).pack(side='right', padx=10, pady=10)
ttk.Button(menubar, text="Main Database", bootstyle='secondary', padding=(15, 10), command=open_main_database).pack(side='right', padx=10, pady=10)
ttk.Button(menubar, text="Generate Report", bootstyle='success', padding=(15, 10), command=open_generate_report_popup).pack(side='right', padx=10, pady=10)

def create_orders_table():
    """Create the orders table in the database if it doesn't exist."""
    con = connect_db()
    if con:
        cursor = con.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                orderId INTEGER PRIMARY KEY AUTOINCREMENT,
                componentName TEXT NOT NULL,
                partNumber TEXT NOT NULL
            )
        """)  # Added partNumber column
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

def submit_order_and_save_parameters():
    """Submit a new order and save associated parameters."""
    component_name = component_name_entry.get().strip()
    part_number = part_number_entry.get().strip()  # Get part number input

    if not component_name or not part_number:
        messagebox.showerror("Error", "Component Name and Part Number are required.")
        return

    con = connect_db()
    if con:
        cursor = con.cursor()
        cursor.execute("""
            INSERT INTO orders (componentName, partNumber)
            VALUES (?, ?)
        """, (component_name, part_number))  # Save part number
        con.commit()

        # Fetch the order ID of the newly inserted component
        cursor.execute("SELECT orderId FROM orders WHERE componentName = ? AND partNumber = ?", (component_name, part_number))
        order = cursor.fetchone()
        if not order:
            messagebox.showerror("Error", "Failed to retrieve the order ID.")
            con.close()
            return

        order_id = order[0]

        # Save parameters associated with the component
        for parameter_name_entry in parameter_entries:
            parameter_name = parameter_name_entry[0].get().strip()

            if not parameter_name:
                messagebox.showerror("Error", "Parameter Name is required.")
                con.close()
                return

            try:
                cursor.execute("""
                    INSERT INTO parametersDetails (orderId, parameterName)
                    VALUES (?, ?)
                """, (order_id, parameter_name))
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save parameter: {e}")
                con.close()
                return

        con.commit()
        con.close()
        messagebox.showinfo("Success", "Component, part number, and parameters saved successfully!")
        refresh_orders()
        clear_order_form()

def clear_order_form():
    """Clear the order input form."""
    component_name_entry.delete(0, tk.END)
    part_number_entry.delete(0, tk.END)  # Clear part number field
    for parameter_name_entry in parameter_entries:
        parameter_name_entry[0].delete(0, tk.END)

# Update references to "Order ID" in the refresh_orders function
def refresh_orders():
    """Fetch and display all orders in the table."""
    for row in orders_tree.get_children():
        orders_tree.delete(row)
    con = connect_db()
    if con:
        cursor = con.cursor()
        cursor.execute("SELECT orderId, componentName, partNumber FROM orders")
        orders = cursor.fetchall()

        for idx, order in enumerate(orders, start=1):
            serial_number, component_name, part_number = order
            # Fetch parameters for the order and format them with high and low values
            cursor.execute("""
                SELECT parameterName, low, high
                FROM parametersDetails
                WHERE orderId = ?
            """, (serial_number,))
            parameters = [
                f"{param[0]} ({param[1]}, {param[2]})" for param in cursor.fetchall()
            ]
            parameters_list = ", ".join(parameters)

            # Insert the row with parameters into the table, with alternating row tags
            tag = 'evenrow' if idx % 2 == 0 else 'oddrow'
            orders_tree.insert("", "end", values=(serial_number, component_name, part_number, parameters_list), tags=(tag,))
        con.close()

def add_parameter_row():
    """Add a new row for parameter input."""
    row = len(parameter_entries) + 1
    parameter_name_entry = tk.Entry(parameter_frame, width=15)

    parameter_name_entry.grid(row=row, column=0, padx=5, pady=5)

    parameter_entries.append((parameter_name_entry,))  # Adjusted to store only parameter_name_entry

def remove_parameter_row():
    """Remove the last row of parameter input."""
    if parameter_entries:
        parameter_name_entry = parameter_entries.pop()[0]  # Adjusted to handle only parameter_name_entry
        parameter_name_entry.destroy()
    else:
        messagebox.showinfo("Info", "No parameter fields to remove.")

# Order Input Form
order_form_frame = tk.Frame(main_frame, bg="white", padx=10, pady=10)
order_form_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=10)

tk.Label(order_form_frame, text="Component Name:", bg="white", font=("Arial", 10)).grid(row=0, column=0, sticky="w", padx=5)
component_name_entry = tk.Entry(order_form_frame, width=15)
component_name_entry.grid(row=0, column=1, padx=5)

# Add Part Number field
tk.Label(order_form_frame, text="Part Number:", bg="white", font=("Arial", 10)).grid(row=1, column=0, sticky="w", padx=5)
part_number_entry = tk.Entry(order_form_frame, width=15)
part_number_entry.grid(row=1, column=1, padx=5)

# Adjust Submit button position
tk.Button(order_form_frame, text="Submit", bg="#28A745", fg="white", font=("Arial", 10), command=submit_order_and_save_parameters).grid(row=2, column=2, pady=10, padx=5)

# Add Submit Button to save data into the database
submit_button = tk.Button(order_form_frame, text="Submit Data", bg="#28A745", fg="white", font=("Arial", 10), command=submit_order_and_save_parameters)
submit_button.grid(row=3, column=1, pady=10, padx=5)

# Parameter Input Section
parameter_frame = tk.Frame(order_form_frame, bg="white", padx=10, pady=10)
parameter_frame.grid(row=2, column=0, columnspan=3, sticky="ew", pady=10)

tk.Label(parameter_frame, text="Parameter Name", bg="white", font=("Arial", 10)).grid(row=0, column=0, padx=5, pady=5)

parameter_entries = []
add_parameter_row()  # Add the first row for parameter input

# Add "Add Parameter" and "Remove Parameter" buttons
tk.Button(parameter_frame, text="Add Parameter", bg="#007BFF", fg="white", font=("Arial", 10), command=add_parameter_row).grid(row=0, column=3, padx=5, pady=5)
tk.Button(parameter_frame, text="Remove Parameter", bg="#DC3545", fg="white", font=("Arial", 10), command=remove_parameter_row).grid(row=0, column=4, padx=5, pady=5)

# Orders Table
orders_table_frame = tk.Frame(main_frame, bg="white", padx=10, pady=10)
orders_table_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)

# Update the orders table column headers
columns = ("Serial Number", "Component Name", "Part Number", "Parameters")
orders_tree = ttk.Treeview(orders_table_frame, columns=columns, show="headings")
for col in columns:
    orders_tree.heading(col, text=col)
    orders_tree.column(col, anchor="center", width=150)

# Add striped row tags/colors (same as main database)
orders_tree.tag_configure('evenrow', background="#FFFFFF")
orders_tree.tag_configure('oddrow', background="#CFCFCF")

scroll_y = ttk.Scrollbar(orders_table_frame, orient="vertical", command=orders_tree.yview)
scroll_x = ttk.Scrollbar(orders_table_frame, orient="horizontal", command=orders_tree.xview)
orders_tree.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)

orders_tree.pack(side="left", fill="both", expand=True)
scroll_y.pack(side="right", fill="y")
scroll_x.pack(side="bottom", fill="x")

refresh_orders()  # Populate the table initially

# Update references to "Order ID" in the populate_fields function
def populate_fields(event):
    """Populate the fields with the selected row's values."""
    selected_item = orders_tree.selection()
    if not selected_item:
        return

    order_details = orders_tree.item(selected_item, "values")
    if not order_details:
        return

    # Clear existing fields
    clear_order_form()

    # Remove all parameter input fields
    while parameter_entries:
        remove_parameter_row()

    # Populate the Component Name field
    component_name_entry.insert(0, order_details[1])  # Assuming column 1 is Component Name
    part_number_entry.insert(0, order_details[2])  # Assuming column 2 is Part Number

    # Fetch and populate parameters for the selected order
    con = connect_db()
    if con:
        cursor = con.cursor()
        cursor.execute("""
            SELECT parameterName, low, high
            FROM parametersDetails
            WHERE orderId = ?
        """, (order_details[0],))  # Assuming column 0 is Serial Number
        parameters = cursor.fetchall()
        con.close()

        for parameter_name, low, high in parameters:
            add_parameter_row()
            parameter_entries[-1][0].insert(0, parameter_name)  # Parameter Name

# Bind the populate_fields function to the treeview selection
orders_tree.bind("<<TreeviewSelect>>", populate_fields)

main_frame.grid_rowconfigure(0, weight=0)  # Ensure the menubar row has no extra space
main_frame.grid_rowconfigure(1, weight=0)  # Add a row for the order form
main_frame.grid_rowconfigure(2, weight=1)  # Ensure the table container row takes remaining space

menubar.grid(row=0, column=0, sticky='ew', pady=0)  # Place the menubar in the first row
order_form_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=10)  # Place the order form in the second row
orders_table_frame.grid(row=2, column=0, sticky="nsew", padx=20, pady=10)  # Place the orders table in the third row

root.bind('<Configure>', on_resize)

# --- Place these definitions and button creation BEFORE root.mainloop() ---

def create_user_database_table():
    """Create the user_database table if it doesn't exist."""
    con = connect_db()
    if con:
        cursor = con.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_database (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                column_name TEXT NOT NULL
            )
        """)
        con.commit()
        con.close()

create_user_database_table()

def open_user_database_window():
    """Open a window to select columns for the user database."""
    win = tk.Toplevel(root)
    win.title("User Database Column Selection")
    win.geometry("500x600")
    win.config(bg="white")

    # Fetch measuredValues columns
    con = connect_db()
    columns = []
    parameter_names = set()
    if con:
        cursor = con.cursor()
        cursor.execute("PRAGMA table_info(measuredValues)")
        columns = [row[1] for row in cursor.fetchall() if row[1] != "parameterName"]
        # Fetch all parameterName values
        cursor.execute("SELECT DISTINCT parameterName FROM measuredValues")
        for row in cursor.fetchall():
            # Split comma-separated parameter names
            for pname in row[0].split(","):
                pname = pname.strip()
                if pname:
                    parameter_names.add(pname)
        con.close()

    # Frame for checkboxes
    frame = tk.Frame(win, bg="white")
    frame.pack(fill="both", expand=True, padx=20, pady=20)

    tk.Label(frame, text="Select columns to include:", bg="white", font=("Arial", 12, "bold")).pack(anchor="w", pady=(0,10))

    # Dict to hold checkbox variables
    checkbox_vars = {}

    # Add checkboxes for measuredValues columns (excluding parameterName)
    for col in columns:
        var = tk.BooleanVar()
        cb = tk.Checkbutton(frame, text=col, variable=var, bg="white", anchor="w")
        cb.pack(fill="x", anchor="w")
        checkbox_vars[col] = var

    # Separator
    tk.Label(frame, text="Parameter Names:", bg="white", font=("Arial", 11, "bold")).pack(anchor="w", pady=(15,5))

    # Add checkboxes for each unique parameter name
    for pname in sorted(parameter_names):
        var = tk.BooleanVar()
        cb = tk.Checkbutton(frame, text=pname, variable=var, bg="white", anchor="w")
        cb.pack(fill="x", anchor="w")
        checkbox_vars[pname] = var

    def save_selected_columns():
        selected = [col for col, var in checkbox_vars.items() if var.get()]
        if not selected:
            messagebox.showerror("Error", "Please select at least one column.")
            return
        con = connect_db()
        if con:
            cursor = con.cursor()
            cursor.execute("DELETE FROM user_database")  # Clear previous selections
            for col in selected:
                cursor.execute("INSERT INTO user_database (column_name) VALUES (?)", (col,))
            con.commit()
            con.close()
        messagebox.showinfo("Success", "Selected columns saved to user_database.")
        win.destroy()

    tk.Button(win, text="Save", bg="#28A745", fg="white", font=("Arial", 11), command=save_selected_columns).pack(pady=20)


# Replace the old User Database button creation with this (before root.mainloop()):
ttk.Button(menubar, text="User Database", bootstyle='primary', padding=(15, 10), command=open_user_database_window).pack(side='right', padx=10, pady=10)

root.mainloop()
