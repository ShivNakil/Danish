import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import sqlite3  # Add this import for database interaction
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "login.db")

class HamburgerMenuApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Excel-like Table with Burger Menu")
        self.root.state("zoomed")  # Maximize the window
        self.root.configure(bg="white")  # Set consistent background color
        self.root.minsize(800, 600)

        self.menu_visible = False
        self.menu_width = 250

        # === Top bar ===
        self.topbar = tk.Frame(self.root, height=50, bg="#0047AB")  # Updated color
        self.topbar.pack(side="top", fill="x")

        self.menu_button = tk.Button(
            self.topbar, text="☰", font=("Arial", 18),
            bg="#0047ab", fg="white", bd=0, command=self.toggle_menu,
            activebackground="#0066cc", highlightthickness=0
        )
        self.menu_button.pack(side="left", padx=10)

        # === Main Area (holds menu + content) ===
        self.main_area = tk.Frame(self.root, bg="white")
        self.main_area.pack(fill="both", expand=True)

        # === Side Menu (initially hidden) ===
        self.menu_frame = tk.Frame(self.main_area, width=0, bg="#0047AB")  # Updated color
        self.menu_frame.pack(side="left", fill="y")
        self.menu_frame.pack_propagate(False)
        self.setup_menu_content()

        # === Table Area ===
        self.table_frame = tk.Frame(self.main_area, bg="white")
        self.table_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        self.create_table()
        self.populate_orders()  # Populate orders on page load
        self.populate_table()  # Populate table on page load

    def setup_menu_content(self):
        self.menu_inner = tk.Frame(self.menu_frame, bg="#003d99")
        self.menu_inner.pack(padx=10, pady=20, fill='both', expand=True)

        def create_rounded_btn(parent, text, cmd=None):
            btn = tk.Button(
                parent, text=text, font=("Arial", 12), command=cmd,
                bg="#007bff", fg="white", activebackground="#3399ff",
                relief="flat", bd=0, padx=10, pady=8, highlightthickness=0
            )
            btn.bind("<Enter>", lambda e: btn.config(bg="#3399ff"))
            btn.bind("<Leave>", lambda e: btn.config(bg="#007bff"))
            return btn

        # Removed "Create User" button
        create_rounded_btn(self.menu_inner, "Report Generation", self.generate_report).pack(pady=10, fill='x')
        create_rounded_btn(self.menu_inner, "User Logout", self.logout).pack(pady=10, fill='x')

        settings_frame = tk.LabelFrame(
            self.menu_inner, text="Settings", bg="#003d99", fg="white",
            font=("Arial", 11, "bold"), bd=1, padx=10, pady=10,
            relief="flat", highlightbackground="#007bff", highlightthickness=1
        )
        settings_frame.pack(pady=20, fill='both')

        # Baud Rate Field
        tk.Label(settings_frame, text="Baud Rate:", bg="#003d99", fg="white", font=("Arial", 10)).pack(anchor="w", pady=5)
        self.baud_rate_var = tk.StringVar()
        self.baud_rate_entry = tk.Entry(settings_frame, textvariable=self.baud_rate_var, width=20)
        self.baud_rate_entry.pack(fill="x", pady=5)

        # COM Port Dropdown
        tk.Label(settings_frame, text="COM Port:", bg="#003d99", fg="white", font=("Arial", 10)).pack(anchor="w", pady=5)
        self.com_port_var = tk.StringVar(value="Select COM Port")
        self.com_port_dropdown = ttk.Combobox(settings_frame, textvariable=self.com_port_var, state="readonly", width=18)
        self.com_port_dropdown.pack(fill="x", pady=5)
        self.refresh_com_ports()

        # Save Button
        tk.Button(
            settings_frame, text="Save Settings", font=("Arial", 11),
            bg="#0047ab", fg="white", relief="flat", bd=0,
            activebackground="#3366cc", padx=8, pady=6, highlightthickness=0,
            command=self.save_settings
        ).pack(fill='x', pady=10)

    def refresh_com_ports(self):
        """Refresh the COM port dropdown values dynamically."""
        try:
            import serial.tools.list_ports
            com_ports = [port.device for port in serial.tools.list_ports.comports()]
            self.com_port_dropdown["values"] = com_ports
            if com_ports:
                self.com_port_var.set(com_ports[0])  # Set the first COM port as default
            else:
                self.com_port_var.set("No COM Ports Available")
        except ModuleNotFoundError:
            self.com_port_var.set("pyserial not installed")

    def save_settings(self):
        baud_rate = self.baud_rate_var.get()
        com_port = self.com_port_var.get()
        if not baud_rate or com_port == "Select COM Port" or com_port == "No COM Ports Available":
            messagebox.showerror("Error", "Please enter a valid Baud Rate and select a COM Port.")
        else:
            messagebox.showinfo("Settings Saved", f"Baud Rate: {baud_rate}\nCOM Port: {com_port}")

    def toggle_menu(self):
        if self.menu_visible:
            # Close menu
            self.menu_frame.config(width=0)
            self.menu_visible = False
        else:
            # Open menu
            self.menu_frame.config(width=self.menu_width)
            self.menu_visible = True
        
        # Force immediate update of the layout
        self.menu_frame.update_idletasks()
        self.main_area.update_idletasks()
        self.root.update_idletasks()

    def create_table(self):
        # Add dropdown and input fields above the table
        control_frame = tk.Frame(self.table_frame, bg="white")
        control_frame.pack(fill="x", pady=10)

        # Order Dropdown
        tk.Label(control_frame, text="Order:", bg="white", font=("Arial", 10)).pack(side="left", padx=5)
        self.order_var = tk.StringVar(value="Select Order")
        self.order_dropdown = ttk.Combobox(control_frame, textvariable=self.order_var, state="readonly", width=20)
        self.order_dropdown.pack(side="left", padx=5)
        self.order_dropdown.bind("<<ComboboxSelected>>", self.populate_components)

        # Component Dropdown
        tk.Label(control_frame, text="Component:", bg="white", font=("Arial", 10)).pack(side="left", padx=5)
        self.component_var = tk.StringVar(value="Select Component")
        self.component_dropdown = ttk.Combobox(control_frame, textvariable=self.component_var, state="readonly", width=20)
        self.component_dropdown.pack(side="left", padx=5)
        self.component_dropdown.bind("<<ComboboxSelected>>", self.populate_parameters)

        # Parameter Dropdown
        tk.Label(control_frame, text="Parameter:", bg="white", font=("Arial", 10)).pack(side="left", padx=5)
        self.parameter_var = tk.StringVar(value="Select Parameter")
        self.parameter_dropdown = ttk.Combobox(control_frame, textvariable=self.parameter_var, state="readonly", width=20)
        self.parameter_dropdown.pack(side="left", padx=5)

        # Low Value Input
        tk.Label(control_frame, text="Low Value:", bg="white", font=("Arial", 10)).pack(side="left", padx=5)
        self.low_value_var = tk.StringVar()
        self.low_value_entry = tk.Entry(control_frame, textvariable=self.low_value_var, width=15)
        self.low_value_entry.pack(side="left", padx=5)

        # High Value Input
        tk.Label(control_frame, text="High Value:", bg="white", font=("Arial", 10)).pack(side="left", padx=5)
        self.high_value_var = tk.StringVar()
        self.high_value_entry = tk.Entry(control_frame, textvariable=self.high_value_var, width=15)
        self.high_value_entry.pack(side="left", padx=5)

        # Save Button
        tk.Button(
            control_frame, text="Save", bg="#0047ab", fg="white", font=("Arial", 10),
            command=self.save_parameter_values
        ).pack(side="left", padx=10)

        # Table columns
        columns = ["Order ID", "Component Name", "Parameter", "Low Value", "High Value"]

        style = ttk.Style()
        style.configure("Treeview", 
            background="white",
            foreground="black",
            rowheight=25,
            fieldbackground="white"
        )
        style.map("Treeview", background=[("selected", "#007bff")])

        self.tree = ttk.Treeview(
            self.table_frame,
            columns=columns,
            show="headings",
            height=30,
            selectmode="browse"
        )

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150, anchor="center")

        # Fill empty rows
        for _ in range(50):
            self.tree.insert("", "end", values=[""] * len(columns))

        # Scrollbars
        vsb = ttk.Scrollbar(self.table_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(self.table_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        # Pack the table and scrollbars
        self.tree.pack(side="top", fill="both", expand=True)
        vsb.pack(side="right", fill="y")
        hsb.pack(side="bottom", fill="x")

        self.tree.bind("<<TreeviewSelect>>", self.on_row_select)  # Bind row selection event

        # Add an "Update" button below the table
        update_button = tk.Button(
            self.table_frame, text="Update Selected Row", bg="#0047ab", fg="white", font=("Arial", 10),
            command=self.update_selected_row
        )
        update_button.pack(side="bottom", pady=10)

    def populate_orders(self):
        """Populate the Order dropdown on page load."""
        try:
            conn = sqlite3.connect(DB_PATH)  # Ensure this path is correct
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
            conn = sqlite3.connect(DB_PATH)  # Ensure this path is correct
            cursor = conn.cursor()
            
            # Fetch components for the selected order
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

    def populate_parameters(self, event=None):
        """Populate the Parameter dropdown based on the selected Order."""
        order = self.order_var.get()
        if order == "Select Order" or order == "No Orders Available":
            self.parameter_dropdown["values"] = []
            self.parameter_var.set("Select Parameter")
            return

        try:
            conn = sqlite3.connect(DB_PATH)  # Ensure this path is correct
            cursor = conn.cursor()
            # Fetch parameters for the selected order
            print((order,))
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

    def save_parameter_values(self):
        """Save the selected parameter's low and high values to the database."""
        parameter = self.parameter_var.get()
        low_value = self.low_value_var.get()
        high_value = self.high_value_var.get()
        order_id = self.order_var.get()

        if parameter == "Select Parameter" or not low_value or not high_value or order_id == "Select Order":
            messagebox.showerror("Error", "Please select a valid Order, Parameter, and enter valid values.")
            return

        try:
            conn = sqlite3.connect(DB_PATH)  # Ensure this path is correct
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE parametersDetails
                SET low = ?, high = ?
                WHERE parameterName = ? AND orderId = ?
                """,
                (low_value, high_value, parameter, order_id)
            )
            conn.commit()
            conn.close()

            messagebox.showinfo("Values Saved", f"Order ID: {order_id}\nParameter: {parameter}\nLow Value: {low_value}\nHigh Value: {high_value}")
            self.populate_table()  # Refresh the table
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error saving parameter values: {e}")

    def on_double_click(self, event):
        item_id = self.tree.identify_row(event.y)
        column = self.tree.identify_column(event.x)

        if not item_id or not column:
            return

        col_index = int(column.replace('#', '')) - 1
        x, y, width, height = self.tree.bbox(item_id, column)
        value = self.tree.item(item_id, "values")[col_index]

        entry = tk.Entry(self.tree, width=15)
        entry.insert(0, value)
        entry.place(x=x, y=y, width=width, height=height)
        entry.focus()

        def save_edit(event=None):
            new_value = entry.get()
            values = list(self.tree.item(item_id, "values"))
            values[col_index] = new_value
            self.tree.item(item_id, values=values)
            entry.destroy()

        entry.bind("<Return>", save_edit)
        entry.bind("<FocusOut>", save_edit)

    def create_user(self):
        messagebox.showinfo("Create User", "Create User functionality would go here")

    def generate_report(self):
        messagebox.showinfo("Report Generation", "Report generation would be implemented here")

    def logout(self):
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            self.root.destroy()
            subprocess.Popen(["python", os.path.join(BASE_DIR, "login.py")])

    def populate_table(self):
        """Fetch and display data in the main frame table."""
        try:
            conn = sqlite3.connect(DB_PATH)  # Ensure this path is correct
            cursor = conn.cursor()
            # Join orders and parametersDetails tables to fetch required data
            query = """
                SELECT o.orderId, o.componentName, p.parameterName, p.low, p.high
                FROM orders o
                JOIN parametersDetails p ON o.orderId = p.orderId
            """
            cursor.execute(query)
            rows = cursor.fetchall()
            conn.close()

            # Clear existing rows in the table
            for item in self.tree.get_children():
                self.tree.delete(item)

            # Insert fetched rows into the table
            for row in rows:
                self.tree.insert("", "end", values=row)
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error fetching table data: {e}")

    def on_row_select(self, event):
        """Handle row selection and populate dropdowns and input fields."""
        selected_item = self.tree.selection()
        if not selected_item:
            return

        # Get selected row values
        values = self.tree.item(selected_item[0], "values")
        if len(values) < 5:
            return

        # Populate dropdowns and input fields
        self.order_var.set(values[0])
        self.component_var.set(values[1])
        self.parameter_var.set(values[2])
        self.low_value_var.set(values[3])
        self.high_value_var.set(values[4])

    def update_selected_row(self):
        """Update the selected row's values in the database."""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "No row selected.")
            return

        # Get updated values from dropdowns and input fields
        order_id = self.order_var.get()
        component_name = self.component_var.get()
        parameter_name = self.parameter_var.get()
        low_value = self.low_value_var.get()
        high_value = self.high_value_var.get()

        if not all([order_id, component_name, parameter_name, low_value, high_value]):
            messagebox.showerror("Error", "Please fill all fields.")
            return

        try:
            conn = sqlite3.connect(DB_PATH)  # Ensure this path is correct
            cursor = conn.cursor()
            # Update the database
            cursor.execute(
                """
                UPDATE parametersDetails
                SET low = ?, high = ?
                WHERE orderId = ? AND componentName = ? AND parameterName = ?
                """,
                (low_value, high_value, order_id, component_name, parameter_name)
            )
            conn.commit()
            conn.close()

            # Update the table row
            self.tree.item(selected_item[0], values=(order_id, component_name, parameter_name, low_value, high_value))
            messagebox.showinfo("Success", "Row updated successfully.")
            self.populate_table()  # Refresh the table
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error updating row: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = HamburgerMenuApp(root)
    root.mainloop()


























