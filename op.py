import tkinter as tk
from tkinter import ttk, messagebox
import sys
import sqlite3  # Add this import for database interaction
import random  # Add this import for generating random values
import datetime  # Add this import for date and time handling
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "login.db")

try:
    import serial.tools.list_ports
except ModuleNotFoundError:
    messagebox.showerror("Module Error", "The 'pyserial' module is not installed. Please install it using 'pip install pyserial'.")
    exit()

class OperatorApp:
    def __init__(self, root, username, name):
        self.root = root
        self.root.title(f"Operator Dashboard - {username} {name}")
        self.root.state("zoomed")  # Maximize the window
        self.root.configure(bg="white")  # Set consistent background color

        self.operator_name = name  # Store operator name

        # === Top Bar with Username ===
        self.topbar = tk.Frame(self.root, height=50, bg="#0047AB")  # Updated color
        self.topbar.pack(side="top", fill="x")

        self.title_label = tk.Label(
            self.topbar, text=f"Welcome, {username}", font=("Arial", 16, "bold"),
            bg="#0047ab", fg="white"
        )
        self.title_label.pack(pady=10)

        # === Main Area ===
        self.main_area = tk.Frame(self.root, bg="white")
        self.main_area.pack(fill="both", expand=True, padx=20, pady=20)

        # === Fields in a Single Line ===
        self.fields_frame = tk.Frame(self.main_area, bg="white")
        self.fields_frame.pack(fill="x", pady=10)

        # COM Port Selection
        tk.Label(self.fields_frame, text="COM Port:", font=("Arial", 12), bg="white").pack(side="left", padx=5)
        self.com_port_var = tk.StringVar(value="Select COM Port")
        self.com_port_dropdown = ttk.Combobox(self.fields_frame, textvariable=self.com_port_var, state="readonly", width=20)
        self.com_port_dropdown.pack(side="left", padx=5)
        self.refresh_com_ports()

        # Baud Rate Setting
        tk.Label(self.fields_frame, text="Baud Rate:", font=("Arial", 12), bg="white").pack(side="left", padx=5)
        self.baud_rate_var = tk.StringVar()
        self.baud_rate_entry = tk.Entry(self.fields_frame, textvariable=self.baud_rate_var, width=15)
        self.baud_rate_entry.pack(side="left", padx=5)

        # Order Selection
        tk.Label(self.fields_frame, text="Order:", font=("Arial", 12), bg="white").pack(side="left", padx=5)
        self.order_var = tk.StringVar(value="Select Order")
        self.order_dropdown = ttk.Combobox(self.fields_frame, textvariable=self.order_var, state="readonly", width=20)
        self.order_dropdown.pack(side="left", padx=5)
        self.order_dropdown.bind("<<ComboboxSelected>>", self.populate_components)

        # Component Selection
        tk.Label(self.fields_frame, text="Component:", font=("Arial", 12), bg="white").pack(side="left", padx=5)
        self.component_var = tk.StringVar(value="Select Component")
        self.component_dropdown = ttk.Combobox(self.fields_frame, textvariable=self.component_var, state="readonly", width=20)
        self.component_dropdown.pack(side="left", padx=5)
        self.component_dropdown.bind("<<ComboboxSelected>>", self.populate_parameters)

        # Parameter Selection
        tk.Label(self.fields_frame, text="Parameter:", font=("Arial", 12), bg="white").pack(side="left", padx=5)
        self.parameter_var = tk.StringVar(value="Select Parameter")
        self.parameter_dropdown = ttk.Combobox(self.fields_frame, textvariable=self.parameter_var, state="readonly", width=20)
        self.parameter_dropdown.pack(side="left", padx=5)

        # Read Values Button
        self.read_button = tk.Button(
            self.fields_frame, text="Read Values", font=("Arial", 12, "bold"),
            bg="#0047ab", fg="white", command=self.read_values
        )
        self.read_button.pack(side="left", padx=10)

        self.populate_orders()  # Populate orders on initialization

        # === Table Area ===
        self.table_frame = tk.Frame(self.main_area, bg="white")
        self.table_frame.pack(fill="both", expand=True, pady=10)

        # Table for newly added entries
        tk.Label(self.table_frame, text="New Entries", font=("Arial", 12, "bold"), bg="white").pack(anchor="w")
        columns_new = ["Order ID", "Component Serial Number", "Component Name", "Parameter Name", "Value"]

        self.tree_new = ttk.Treeview(
            self.table_frame,
            columns=columns_new,
            show="headings",
            height=7,
            selectmode="browse"
        )

        for col in columns_new:
            self.tree_new.heading(col, text=col)
            self.tree_new.column(col, width=200, anchor="center")

        vsb_new = ttk.Scrollbar(self.table_frame, orient="vertical", command=self.tree_new.yview)
        self.tree_new.configure(yscrollcommand=vsb_new.set)

        self.tree_new.pack(side="top", fill="both", expand=True, pady=5)
        vsb_new.pack(side="right", fill="y")

        # Table for previously fetched entries
        tk.Label(self.table_frame, text="Previously Fetched Entries", font=("Arial", 12, "bold"), bg="white").pack(anchor="w")
        columns_prev = ["Order ID", "Component Serial Number", "Component Name", "Parameter Name", "Value"]

        self.tree_prev = ttk.Treeview(
            self.table_frame,
            columns=columns_prev,
            show="headings",
            height=7,
            selectmode="browse"
        )

        for col in columns_prev:
            self.tree_prev.heading(col, text=col)
            self.tree_prev.column(col, width=200, anchor="center")

        vsb_prev = ttk.Scrollbar(self.table_frame, orient="vertical", command=self.tree_prev.yview)
        self.tree_prev.configure(yscrollcommand=vsb_prev.set)

        self.tree_prev.pack(side="top", fill="both", expand=True, pady=5)
        vsb_prev.pack(side="right", fill="y")

        # Submit Button
        self.submit_button = tk.Button(
            self.main_area, text="Submit", font=("Arial", 12, "bold"),
            bg="#28a745", fg="white", command=self.submit_data
        )
        self.submit_button.pack(side="bottom", pady=10)

        self.latest_serial_number = 0  # Initialize the latest serial number

    def refresh_com_ports(self):
        """Refresh the COM port dropdown values dynamically."""
        com_ports = [port.device for port in serial.tools.list_ports.comports()]
        self.com_port_dropdown["values"] = com_ports
        if (com_ports):
            self.com_port_var.set(com_ports[0])  # Set the first COM port as default
        else:
            self.com_port_var.set("No COM Ports Available")

    def read_values(self):
        """Add a row to the new entries table with random values."""
        order = self.order_var.get()
        component = self.component_var.get()
        parameter = self.parameter_var.get()
        value = round(random.uniform(0, 1), 2)  # Generate a random value between 0 and 1

        if order == "Select Order" or component == "Select Component" or parameter == "Select Parameter":
            messagebox.showerror("Error", "Please select valid Order, Component, and Parameter.")
            return

        # Determine the starting componentSerialNumber
        if self.tree_prev.get_children() and self.latest_serial_number == 0:
            # Get the latest componentSerialNumber from the first row of the previously fetched entries
            self.latest_serial_number = int(self.tree_prev.item(self.tree_prev.get_children()[0], "values")[1])

        # Increment the latest serial number
        self.latest_serial_number += 1

        # Add a new row to the new entries table
        self.tree_new.insert("", 0, values=(order, self.latest_serial_number, component, parameter, value))

    def sort_table_by_column(self, column_name, descending=False):
        """Sort the table by the specified column in ascending or descending order."""
        column_index = self.tree["columns"].index(column_name)
        rows = [(self.tree.set(child, column_index), child) for child in self.tree.get_children()]
        rows.sort(key=lambda x: int(x[0]), reverse=descending)  # Sort numerically
        for index, (_, child) in enumerate(rows):
            self.tree.move(child, "", index)

    def populate_previous_entries(self):
        """Populate the previously fetched entries table."""
        order = self.order_var.get()
        component = self.component_var.get()
        parameter = self.parameter_var.get()

        # Avoid showing error during dropdown population
        if order in ["Select Order", "No Orders Available"] or \
           component in ["Select Component", "No Components Available"] or \
           parameter in ["Select Parameter", "No Parameters Available"]:
            return  # Do nothing if invalid values are selected

        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()

            # Fetch previous entries for the selected order, component, and parameter
            cursor.execute("""
                SELECT orderId, componentSerialNumber, componentName, parameterName, value
                FROM measuredValues
                WHERE orderId = ? AND componentName = ? AND parameterName = ?
                ORDER BY componentSerialNumber DESC
            """, (order, component, parameter))
            rows = cursor.fetchall()
            conn.close()

            # Clear the previously fetched entries table and populate with previous entries
            self.tree_prev.delete(*self.tree_prev.get_children())
            for row in rows:
                self.tree_prev.insert("", "end", values=row)
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error fetching previous entries: {e}")

    def populate_orders(self):
        """Populate the Order dropdown."""
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT orderId FROM orders")
            orders = cursor.fetchall()
            conn.close()

            if orders:
                self.order_dropdown["values"] = [order[0] for order in orders]
                self.order_var.set("Select Order")
            else:
                self.order_dropdown["values"] = []
                self.order_var.set("No Orders Available")
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error fetching orders: {e}")

    def populate_components(self, event=None):
        """Populate the Component dropdown based on the selected Order."""
        order = self.order_var.get()
        if order == "Select Order" or order == "No Orders Available":
            self.component_dropdown["values"] = []
            self.component_var.set("Select Component")
            return

        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT componentName FROM orders WHERE orderId = ?", (order,))
            components = [row[0] for row in cursor.fetchall()]
            conn.close()

            if components:
                self.component_dropdown["values"] = components
                self.component_var.set("Select Component")
            else:
                self.component_dropdown["values"] = []
                self.component_var.set("No Components Available")
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error fetching components: {e}")
        self.populate_previous_entries()  # Populate previous entries after selection

    def populate_parameters(self, event=None):
        """Populate the Parameter dropdown based on the selected Component."""
        order = self.order_var.get()
        if order == "Select Order" or order == "No Orders Available":
            self.parameter_dropdown["values"] = []
            self.parameter_var.set("Select Parameter")
            return

        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT parameterName FROM parametersDetails WHERE orderId = ?", (order,))
            parameters = [row[0] for row in cursor.fetchall()]
            conn.close()

            if parameters:
                self.parameter_dropdown["values"] = parameters
                self.parameter_var.set("Select Parameter")
            else:
                self.parameter_dropdown["values"] = []
                self.parameter_var.set("No Parameters Available")
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error fetching parameters: {e}")
        # Bind to call populate_previous_entries only after a parameter is selected
        self.parameter_dropdown.bind("<<ComboboxSelected>>", lambda e: self.populate_previous_entries())

    def submit_data(self):
        """Submit only newly added rows to the database."""
        if not self.tree_new.get_children():
            messagebox.showerror("Error", "No new data to submit.")
            return

        if not messagebox.askyesno("Confirmation", "Are you sure you want to submit the new data?"):
            return

        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()

            # Create the table if it doesn't exist
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS measuredValues (
                    orderId TEXT NOT NULL,
                    componentSerialNumber INTEGER NOT NULL,
                    componentName TEXT NOT NULL,
                    parameterName TEXT NOT NULL,
                    operatorName TEXT NOT NULL,
                    date TEXT NOT NULL,
                    time TEXT NOT NULL,
                    value REAL NOT NULL,
                    isValid TEXT NOT NULL,
                    PRIMARY KEY (orderId, componentSerialNumber)
                )
            """)

            # Fetch the maximum componentSerialNumber for each orderId
            cursor.execute("""
                SELECT orderId, MAX(componentSerialNumber) 
                FROM measuredValues 
                GROUP BY orderId
            """)
            max_serial_numbers = {row[0]: row[1] for row in cursor.fetchall()}

            # Insert only rows from the new entries table
            for row in self.tree_new.get_children():
                values = self.tree_new.item(row, "values")
                order, _, component, parameter, measured_value = values

                # Determine the next componentSerialNumber for the order
                next_serial_number = max_serial_numbers.get(order, 0) + 1
                max_serial_numbers[order] = next_serial_number

                # Placeholder logic for validity (replace with actual logic based on uploaded image)
                is_valid = "Valid" if float(measured_value) > 0.5 else "Invalid"

                # Insert the row into the database
                cursor.execute("""
                    INSERT INTO measuredValues (orderId, componentSerialNumber, componentName, parameterName, operatorName, date, time, value, isValid)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    order,
                    next_serial_number,
                    component,
                    parameter,
                    self.operator_name,
                    datetime.date.today().strftime("%Y-%m-%d"),
                    datetime.datetime.now().strftime("%H:%M:%S"),
                    measured_value,
                    is_valid
                ))

            conn.commit()
            conn.close()

            messagebox.showinfo("Success", "New data submitted successfully.")
            self.tree_new.delete(*self.tree_new.get_children())  # Clear the new entries table after submission

            # Call populate_previous_entries to refresh the previously fetched entries table
            self.populate_previous_entries()

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error submitting data: {e}")

if __name__ == "__main__":
    # Fetch username and name from command-line arguments
    logged_in_user = "Shiv"
    logged_in_name = "Nakil"

    if len(sys.argv) < 3:
        # messagebox.showerror("Error", "Invalid arguments passed to the application.")
        # exit()
        pass
    else:
        logged_in_user = sys.argv[1]
        logged_in_name = sys.argv[2]
    
    root = tk.Tk()
    app = OperatorApp(root, logged_in_user, logged_in_name)
    root.mainloop()


























