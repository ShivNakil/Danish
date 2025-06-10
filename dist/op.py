import tkinter as tk
from tkinter import ttk, messagebox
import sys
import sqlite3  # Add this import for database interaction
import os
from test import list_ports, connect_serial, send_command  # Import serial functions
import datetime  # <-- Add this line

# Update database path to handle PyInstaller's temporary directory
if getattr(sys, 'frozen', False):  # Check if running as a PyInstaller bundle
    BASE_DIR = sys._MEIPASS  # Temporary directory created by PyInstaller
else:
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
        self.selected_com_port = None  # Store selected COM port
        self.selected_baud_rate = None  # Store selected baud rate

        # === Top Bar with Username ===
        self.topbar = tk.Frame(self.root, height=50, bg="#0047AB")  # Updated color
        self.topbar.pack(side="top", fill="x")

        self.title_label = tk.Label(
            self.topbar, text=f"Welcome, {username}", font=("Arial", 16, "bold"),
            bg="#0047ab", fg="white"
        )
        self.title_label.pack(pady=10)

        # === Sidebar ===
        self.sidebar = tk.Frame(self.root, width=200, bg="#0047AB")

        # Communication Button in Sidebar
        self.com_baud_button = tk.Button(
            self.sidebar, text="Communication", font=("Arial", 10, "bold"),
            bg="#5597F3", fg="white", relief="flat", height=2, 
            command=self.open_com_baud_popup
        )
        self.com_baud_button.pack(fill="x", padx=10, pady=8)

        # Help and Support Button in Sidebar
        self.help_support_button = tk.Button(
            self.sidebar, text="Help and Support", font=("Arial", 10, "bold"),
            bg="#5597F3", fg="white", relief="flat", height=2, 
            command=self.open_help_support
        )
        self.help_support_button.pack(fill="x", padx=10, pady=8)

        # Log Out Button in Sidebar
        self.logout_button = tk.Button(
            self.sidebar, text="Log Out", font=("Arial", 10, "bold"),
            bg="#5597F3", fg="white", relief="flat", height=2, 
            command=self.logout_user
        )
        self.logout_button.pack(fill="x", padx=10, pady=8)

        # Arrow Button for Toggling Sidebar (Outer Edge)
        self.toggle_sidebar_button = tk.Button(
            self.root, text="☰", font=("Arial", 14, "bold"),
            bg="#5597F3", fg="white", relief="flat", borderwidth=0,
            activebackground="#5597F3", activeforeground="white",
            command=self.toggle_sidebar
        )
        self.toggle_sidebar_button.place(x=0, y=0, width=50, height=50)  # Fixed at top-left

        # === Main Area ===
        self.main_area = tk.Frame(self.root, bg="white")
        self.main_area.pack(side="right", fill="both", expand=True, padx=20, pady=20)

        # === Fields in a Single Line ===
        self.fields_frame = tk.Frame(self.main_area, bg="white")
        self.fields_frame.pack(fill="x", pady=10)

        # Component Name Selection
        tk.Label(self.fields_frame, text="Component Name:", font=("Arial", 12), bg="white").pack(side="left", padx=5)
        self.component_name_var = tk.StringVar(value="Select Component Name")
        self.component_name_dropdown = ttk.Combobox(self.fields_frame, textvariable=self.component_name_var, state="readonly", width=20)
        self.component_name_dropdown.pack(side="left", padx=5)
        self.component_name_dropdown.bind("<<ComboboxSelected>>", self.display_part_number)

        # Part Number Selection
        tk.Label(self.fields_frame, text="Part Number:", font=("Arial", 12), bg="white").pack(side="left", padx=5)
        self.part_number_var = tk.StringVar(value="Select Part Number")
        self.part_number_dropdown = ttk.Combobox(self.fields_frame, textvariable=self.part_number_var, state="readonly", width=20)
        self.part_number_dropdown.pack(side="left", padx=5)

        # Bind the event to populate parameters when a part number is selected
        self.part_number_dropdown.bind("<<ComboboxSelected>>", self.populate_parameters)

        # Parameter Selection (replace dropdown with checkboxes)
        tk.Label(self.fields_frame, text="Parameter:", font=("Arial", 12), bg="white").pack(side="left", padx=5)
        self.parameter_vars = {}  # Dictionary to hold parameter name and its IntVar
        self.parameter_checkboxes_frame = tk.Frame(self.fields_frame, bg="white")
        self.parameter_checkboxes_frame.pack(side="left", padx=5)

        # Read Values Button
        self.read_button = tk.Button(
            self.fields_frame, text="Read Values", font=("Arial", 12, "bold"),
            bg="#0047ab", fg="white", command=self.read_values
        )
        self.read_button.pack(side="left", padx=10)

        # Random Button
        self.random_button = tk.Button(
            self.fields_frame, text="Random", font=("Arial", 12, "bold"),
            bg="#6c757d", fg="white", command=self.generate_random_values
        )
        self.random_button.pack(side="left", padx=5)

        self.populate_components()  # Populate components on initialization

        # === Table Area ===
        self.table_frame = tk.Frame(self.main_area, bg="white")
        self.table_frame.pack(fill="both", expand=True, pady=10)

        # Table for newly added entries
        tk.Label(self.table_frame, text="New Entries", font=("Arial", 12, "bold"), bg="white").pack(anchor="w")
        columns_new = ["Part Number", "Component Serial Number", "Component Name", "Parameter Name", "Value", "Range"]  # Added "Range"

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
        columns_prev = ["Part Number", "Component Serial Number", "Component Name", "Parameter Name", "Value"]

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

    def logout_user(self):
        confirm = messagebox.askyesno("Logout", "Are you sure you want to log out?")
        if confirm:
            self.root.destroy()
            os.system("python d:\\Engineering\\Manish\\manish\\login.py")  # Open login.py after logout

    def open_com_baud_popup(self):
        """Open a popup window for COM Port and Baud Rate settings."""
        popup = tk.Toplevel(self.root)
        popup.title("COM Port and Baud Rate Settings")
        popup.geometry("400x300")
        popup.configure(bg="white")

        # COM Port Selection
        tk.Label(popup, text="COM Port:", font=("Arial", 12), bg="white").pack(pady=10)
        self.com_port_var = tk.StringVar(value="Select COM Port")
        self.com_port_dropdown = ttk.Combobox(popup, textvariable=self.com_port_var, state="readonly", width=30)
        self.com_port_dropdown.pack(pady=5)
        self.refresh_com_ports()

        # Baud Rate Setting
        tk.Label(popup, text="Baud Rate:", font=("Arial", 12), bg="white").pack(pady=10)
        self.baud_rate_var = tk.StringVar()
        self.baud_rate_entry = tk.Entry(popup, textvariable=self.baud_rate_var, width=30)
        self.baud_rate_entry.pack(pady=5)

        # Save Button
        tk.Button(
            popup, text="Save", font=("Arial", 12, "bold"),
            bg="#28a745", fg="white", command=lambda: self.save_com_baud_settings(popup)
        ).pack(pady=20)

    def save_com_baud_settings(self, popup):
        """Save the selected COM Port and Baud Rate settings."""
        selected_com_port = self.com_port_var.get()
        selected_baud_rate = self.baud_rate_var.get()

        if selected_com_port == "Select COM Port" or not selected_baud_rate:
            messagebox.showerror("Error", "Please select a valid COM Port and enter a Baud Rate.")
            return

        self.selected_com_port = selected_com_port
        self.selected_baud_rate = selected_baud_rate

        messagebox.showinfo("Success", f"Settings saved:\nCOM Port: {selected_com_port}\nBaud Rate: {selected_baud_rate}")
        popup.destroy()

    def refresh_com_ports(self):
        """Refresh the COM port dropdown values dynamically."""
        com_ports = [port.device for port in serial.tools.list_ports.comports()]
        self.com_port_dropdown["values"] = com_ports
        if com_ports:
            self.com_port_var.set(com_ports[0])  # Set the first COM port as default
        else:
            self.com_port_var.set("No COM Ports Available")

    def read_values(self):
        """Read values from the serial port and add a row to the new entries table for all selected parameters."""
        part_number = self.part_number_var.get()
        component = self.component_name_var.get()
        selected_parameters = [param for param, var in self.parameter_vars.items() if var.get() == 1]

        if part_number == "Select Part Number" or component == "Select Component Name" or not selected_parameters:
            messagebox.showerror("Error", "Please select valid Part Number, Component, and at least one Parameter.")
            return

        # Use saved COM port and baud rate
        if not self.selected_com_port or not self.selected_baud_rate:
            messagebox.showerror("Error", "Please set Communication and Baud Rate settings first.")
            return

        # Determine the starting componentSerialNumber
        if self.tree_prev.get_children() and self.latest_serial_number == 0:
            self.latest_serial_number = int(self.tree_prev.item(self.tree_prev.get_children()[0], "values")[1])

        self.latest_serial_number += 1

        # Open serial connection
        try:
            ser = connect_serial(self.selected_com_port, int(self.selected_baud_rate))
            if not ser:
                self.show_serial_error_popup(
                    "Failed to connect to the serial port.",
                    part_number, ", ".join(selected_parameters), self.selected_com_port, self.selected_baud_rate
                )
                return
        except Exception as e:
            self.show_serial_error_popup(
                f"Error opening serial port: {e}",
                part_number, ", ".join(selected_parameters), self.selected_com_port, self.selected_baud_rate
            )
            return

        param_names = []
        param_values = []
        param_ranges = []
        for parameter in selected_parameters:
            try:
                if parameter.lower() == "voltage":
                    response = send_command(ser, ":MEAS:VOLT?")
                    value = response
                elif parameter.lower() == "resistance":
                    response = send_command(ser, ":MEAS:RES?")
                    value = response
                else:
                    response = send_command(ser, f":MEAS:{parameter.upper()}?")
                    value = response
            except Exception as e:
                self.show_serial_error_popup(
                    f"Error reading from serial port: {e}",
                    part_number, parameter, self.selected_com_port, self.selected_baud_rate
                )
                ser.close()
                return

            # --- Range check logic ---
            min_val, max_val = None, None
            try:
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                cursor.execute("SELECT orderId FROM orders WHERE componentName = ? AND partNumber = ?", (component, part_number))
                order_id_row = cursor.fetchone()
                if order_id_row:
                    order_id = order_id_row[0]
                    # Use correct column names for your schema: low, high
                    cursor.execute("SELECT low, high FROM parametersDetails WHERE orderId = ? AND parameterName = ?", (order_id, parameter))
                    range_row = cursor.fetchone()
                    if range_row:
                        min_val, max_val = range_row
                conn.close()
            except Exception:
                pass

            # Format range for display
            if min_val is not None and max_val is not None:
                param_ranges.append(f"{min_val} - {max_val}")
            elif min_val is not None:
                param_ranges.append(f"{min_val} - ")
            elif max_val is not None:
                param_ranges.append(f" - {max_val}")
            else:
                param_ranges.append("")

            # Now do the range check
            try:
                measured_val = float(value)
                if min_val is not None and measured_val < float(min_val):
                    messagebox.showerror("Out of Range", f"Measured value {measured_val} for {parameter} is below minimum allowed {min_val}. Entry not added.")
                    ser.close()
                    return
                if max_val is not None and measured_val > float(max_val):
                    messagebox.showerror("Out of Range", f"Measured value {measured_val} for {parameter} is above maximum allowed {max_val}. Entry not added.")
                    ser.close()
                    return
            except Exception:
                messagebox.showerror("Value Error", f"Could not convert measured value '{value}' for {parameter} to float for range checking. Entry not added.")
                ser.close()
                return

            param_names.append(parameter)
            param_values.append(str(value))

        ser.close()  # Close serial connection

        if param_names and param_values:
            # Add a single row with comma-separated parameter names, values, and ranges
            self.tree_new.insert(
                "", 0,
                values=(
                    part_number,
                    self.latest_serial_number,
                    component,
                    ",".join(param_names),
                    ",".join(param_values),
                    ",".join(param_ranges)
                )
            )

    def show_serial_error_popup(self, error_message, part_number, parameter, com_port, baud_rate):
        """Show a popup with error details and selected values."""
        popup = tk.Toplevel(self.root)
        popup.title("Serial Error")
        popup.geometry("400x300")
        popup.configure(bg="white")

        tk.Label(popup, text="Serial Communication Error", font=("Arial", 14, "bold"), fg="red", bg="white").pack(pady=10)
        tk.Label(popup, text=error_message, font=("Arial", 11), fg="black", bg="white", wraplength=350, justify="left").pack(pady=5)

        details = (
            f"Part Number: {part_number}\n"
            f"Parameter: {parameter}\n"
            f"COM Port: {com_port}\n"
            f"Baud Rate: {baud_rate}"
        )
        tk.Label(popup, text=details, font=("Arial", 11), bg="white", justify="left", anchor="w").pack(pady=10)

        tk.Button(
            popup, text="Close", font=("Arial", 12, "bold"),
            bg="#0047ab", fg="white", command=popup.destroy
        ).pack(pady=10)

    def sort_table_by_column(self, column_name, descending=False):
        """Sort the table by the specified column in ascending or descending order."""
        column_index = self.tree["columns"].index(column_name)
        rows = [(self.tree.set(child, column_index), child) for child in self.tree.get_children()]
        rows.sort(key=lambda x: int(x[0]), reverse=descending)  # Sort numerically
        for index, (_, child) in enumerate(rows):
            self.tree.move(child, "", index)

    def populate_previous_entries(self):
        """Populate the previously fetched entries table."""
        part_number = self.part_number_var.get()
        component = self.component_name_var.get()  # Corrected variable name

        # For checkboxes, get selected parameters as a comma-separated string
        selected_parameters = [param for param, var in self.parameter_vars.items() if var.get() == 1]
        if selected_parameters:
            parameter = ",".join(selected_parameters)
        else:
            parameter = ""

        # Avoid showing error during dropdown population
        if part_number in ["Select Part Number", "No Part Numbers Available"] or \
           component in ["Select Component Name", "No Components Available"] or \
           not parameter:
            return  # Do nothing if invalid values are selected

        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()

            # Fetch previous entries for the selected part number, component, and parameter
            cursor.execute("""
                SELECT orderId, componentSerialNumber, componentName, parameterName, value
                FROM measuredValues
                WHERE partNumber = ? AND componentName = ? AND parameterName = ?
                ORDER BY componentSerialNumber DESC
            """, (part_number, component, parameter))
            rows = cursor.fetchall()
            conn.close()

            # Clear the previously fetched entries table and populate with previous entries
            self.tree_prev.delete(*self.tree_prev.get_children())
            for row in rows:
                self.tree_prev.insert("", "end", values=row)
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error fetching previous entries: {e}")

    def populate_components(self):
        """Populate the Component Name dropdown."""
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT componentName FROM orders")
            components = cursor.fetchall()
            conn.close()

            if components:
                self.component_name_dropdown["values"] = [component[0] for component in components]
                self.component_name_var.set("Select Component Name")
            else:
                self.component_name_dropdown["values"] = []
                self.component_name_var.set("No Components Available")
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error fetching components: {e}")

    def display_part_number(self, event=None):
        """Populate the Part Number dropdown for the selected Component Name."""
        component_name = self.component_name_var.get()
        if component_name == "Select Component Name" or component_name == "No Components Available":
            self.part_number_dropdown["values"] = []
            self.part_number_var.set("Select Part Number")
            return

        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT partNumber FROM orders WHERE componentName = ?", (component_name,))
            part_numbers = cursor.fetchall()
            conn.close()

            if part_numbers:
                self.part_number_dropdown["values"] = [part[0] for part in part_numbers]
                self.part_number_var.set("Select Part Number")
            else:
                self.part_number_dropdown["values"] = []
                self.part_number_var.set("No Part Numbers Available")
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error fetching part numbers: {e}")

    def populate_parameters(self, event=None):
        """Populate the Parameter checkboxes based on the selected Component Name and Part Number."""
        # Clear previous checkboxes
        for widget in self.parameter_checkboxes_frame.winfo_children():
            widget.destroy()
        self.parameter_vars.clear()

        component_name = self.component_name_var.get()
        part_number = self.part_number_var.get()

        if component_name in ["Select Component Name", "No Components Available"] or \
           part_number in ["Select Part Number", "No Part Numbers Available"]:
            return

        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()

            # Fetch the orderId based on the selected componentName and partNumber
            cursor.execute("SELECT orderId FROM orders WHERE componentName = ? AND partNumber = ?", (component_name, part_number))
            order_id = cursor.fetchone()

            if not order_id:
                conn.close()
                return

            # Fetch parameters from parametersDetails table using the orderId
            cursor.execute("SELECT parameterName FROM parametersDetails WHERE orderId = ?", (order_id[0],))
            parameters = [row[0] for row in cursor.fetchall()]
            conn.close()

            if parameters:
                for param in parameters:
                    var = tk.IntVar()
                    cb = tk.Checkbutton(self.parameter_checkboxes_frame, text=param, variable=var, bg="white")
                    cb.pack(side="left", padx=2)
                    self.parameter_vars[param] = var
            else:
                # No parameters available
                pass
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error fetching parameters: {e}")

        # After parameters are populated, refresh previous entries when any checkbox is selected
        # (Optional: you may want to trigger on checkbox click, or keep as manual after read)

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
                    partNumber TEXT NOT NULL,
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
                # Unpack only the first 5 columns (ignore the "Range" column)
                order, _, component, parameter_names, measured_values = values[:5]

                # Determine the next componentSerialNumber for the order
                next_serial_number = max_serial_numbers.get(order, 0) + 1
                max_serial_numbers[order] = next_serial_number

                # Placeholder logic for validity (replace with actual logic based on uploaded image)
                try:
                    is_valid = "Valid" if all(float(val) > 0.5 for val in measured_values.split(",")) else "Invalid"
                except Exception:
                    is_valid = "Invalid"

                # Insert the row into the database (parameterName and value as comma-separated)
                cursor.execute("""
                    INSERT INTO measuredValues (orderId, componentSerialNumber, componentName, partNumber, parameterName, operatorName, date, time, value, isValid)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    order,
                    next_serial_number,
                    component,
                    self.part_number_var.get(),  # Store the part number properly
                    parameter_names,
                    self.operator_name,
                    datetime.date.today().strftime("%Y-%m-%d"),
                    datetime.datetime.now().strftime("%H:%M:%S"),
                    measured_values,
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

    def toggle_sidebar(self):
        """Toggle the visibility of the sidebar."""
        if self.sidebar.winfo_ismapped():
            self.sidebar.pack_forget()
            # Do not move the toggle button, keep it at (0,0)
            # self.toggle_sidebar_button.config(text="→")  # Optionally change icon if you want
        else:
            self.sidebar.pack(side="left", fill="y")
            # self.toggle_sidebar_button.config(text="←")  # Optionally change icon if you want
            # Do not move the toggle button, keep it at (0,0)

    def open_help_support(self):
        """Open a popup window for Help and Support."""
        popup = tk.Toplevel(self.root)
        popup.title("Help and Support")
        popup.geometry("600x500")
        popup.configure(bg="white")

        tk.Label(
            popup, text="inThink Technologies",
            font=("Arial", 12), bg="white", wraplength=350, justify="center"
        ).pack(expand=True, pady=20)

        tk.Button(
            popup, text="Close", font=("Arial", 12, "bold"),
            bg="#0047ab", fg="white", command=popup.destroy
        ).pack(pady=10)

    def generate_random_values(self):
        """Generate random values for all selected parameters and add a row to the new entries table."""
        import random

        part_number = self.part_number_var.get()
        component = self.component_name_var.get()
        selected_parameters = [param for param, var in self.parameter_vars.items() if var.get() == 1]

        if part_number == "Select Part Number" or component == "Select Component Name" or not selected_parameters:
            messagebox.showerror("Error", "Please select valid Part Number, Component, and at least one Parameter.")
            return

        # Determine the starting componentSerialNumber
        if self.tree_prev.get_children() and self.latest_serial_number == 0:
            self.latest_serial_number = int(self.tree_prev.item(self.tree_prev.get_children()[0], "values")[1])

        self.latest_serial_number += 1

        param_names = []
        param_values = []
        param_ranges = []
        for parameter in selected_parameters:
            min_val, max_val = None, None
            # Use correct column names for your schema: low, high
            try:
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                cursor.execute("SELECT orderId FROM orders WHERE componentName = ? AND partNumber = ?", (component, part_number))
                order_id_row = cursor.fetchone()
                if order_id_row:
                    order_id = order_id_row[0]
                    cursor.execute("SELECT low, high FROM parametersDetails WHERE orderId = ? AND parameterName = ?", (order_id, parameter))
                    range_row = cursor.fetchone()
                    if range_row:
                        min_val, max_val = range_row
                conn.close()
            except Exception:
                pass

            # Format range for display
            if min_val is not None and max_val is not None:
                param_ranges.append(f"{min_val} - {max_val}")
            elif min_val is not None:
                param_ranges.append(f"{min_val} - ")
            elif max_val is not None:
                param_ranges.append(f" - {max_val}")
            else:
                param_ranges.append("")

            # Use default if both are None
            min_v =  2
            max_v =  6
            value = round(random.uniform(min_v, max_v), 2)
            # Range check for random value
            if min_val is not None and value < float(min_val):
                messagebox.showerror("Out of Range", f"Random value {value} for {parameter} is below minimum allowed {min_val}. Entry not added.")
                return
            if max_val is not None and value > float(max_val):
                messagebox.showerror("Out of Range", f"Random value {value} for {parameter} is above maximum allowed {max_val}. Entry not added.")
                return
            param_names.append(parameter)
            param_values.append(str(value))

        if param_names and param_values:
            self.tree_new.insert(
                "", 0,
                values=(
                    part_number,
                    self.latest_serial_number,
                    component,
                    ",".join(param_names),
                    ",".join(param_values),
                    ",".join(param_ranges)
                )
            )

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


























