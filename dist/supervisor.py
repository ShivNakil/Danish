import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import sqlite3  # Add this import for database interaction
import os
import sys  # Ensure sys is imported

# Update database path to handle PyInstaller's temporary directory
if getattr(sys, 'frozen', False):  # Check if running as a PyInstaller bundle
    BASE_DIR = sys._MEIPASS  # Temporary directory created by PyInstaller
else:
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

        create_rounded_btn(self.menu_inner, "Report Generation", self.generate_report).pack(pady=10, fill='x')
        # Add User Database button below Report Generation
        create_rounded_btn(self.menu_inner, "User Database", self.open_user_database).pack(pady=10, fill='x')
        create_rounded_btn(self.menu_inner, "User Logout", self.logout).pack(pady=10, fill='x')
        create_rounded_btn(self.menu_inner, "Communication", self.open_com_port_popup).pack(pady=10, fill='x')

    # Add a stub for the User Database button action
    def open_user_database(self):
        # Open a window showing only the columns listed in user_database
        self.open_user_database_window()

    def open_user_database_window(self):
        """Open a window displaying only the columns listed in user_database."""
        win = tk.Toplevel(self.root)
        win.title("User Database")
        win.geometry("1100x500")
        win.config(bg="white")

        # Fetch selected columns from user_database table
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT column_name FROM user_database")
            columns = [row[0] for row in cursor.fetchall()]
            conn.close()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error fetching user database columns: {e}")
            win.destroy()
            return

        if not columns:
            tk.Label(win, text="No columns selected in user_database.", bg="white", fg="red", font=("Arial", 12)).pack(pady=20)
            return

        # Treeview for data
        tree = ttk.Treeview(win, columns=columns, show="headings")
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, anchor="center", width=140)
        tree.pack(fill="both", expand=True, padx=10, pady=10)

        # Fetch and display data from measuredValues table for selected columns
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            # Always fetch all columns needed for processing
            cursor.execute("PRAGMA table_info(measuredValues)")
            all_mv_cols = [row[1] for row in cursor.fetchall()]
            fetch_cols = set(columns) & set(all_mv_cols)
            fetch_cols.update(["parameterName", "value"])
            fetch_cols = list(fetch_cols)
            col_str = ", ".join([f'"{col}"' for col in fetch_cols])
            cursor.execute(f"SELECT {col_str} FROM measuredValues")
            rows = cursor.fetchall()
            desc = [d[0] for d in cursor.description]
            conn.close()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error fetching measuredValues data: {e}")
            win.destroy()
            return

        # Helper to extract voltage/resistance from parameterName/value
        def extract_param_value(param_name, value, target):
            # param_name, value: both may be comma separated
            if not param_name or not value:
                return "n/a"
            names = [n.strip().lower() for n in str(param_name).split(",")]
            vals = [v.strip() for v in str(value).split(",")]
            result = []
            for n, v in zip(names, vals):
                if target in n:
                    result.append(v if v else "n/a")
            return ", ".join(result) if result else "n/a"

        for row in rows:
            row_dict = dict(zip(desc, row))
            display_row = []
            for col in columns:
                if col.lower() in ("voltage", "resistance"):
                    val = extract_param_value(
                        row_dict.get("parameterName", ""), row_dict.get("value", ""), col.lower()
                    )
                    display_row.append(val)
                else:
                    v = row_dict.get(col, None)
                    display_row.append(v if v not in (None, "",) else "n/a")
            tree.insert("", "end", values=display_row)

    def open_com_port_popup(self):
        """Open a popup window for Baud Rate and COM Port settings."""
        popup = tk.Toplevel(self.root)
        popup.title("Communication")
        popup.geometry("300x200")
        popup.configure(bg="white")

        tk.Label(popup, text="Baud Rate:", bg="white", font=("Arial", 10)).pack(anchor="w", pady=5, padx=10)
        baud_rate_var = tk.StringVar()
        baud_rate_entry = tk.Entry(popup, textvariable=baud_rate_var, width=20)
        baud_rate_entry.pack(fill="x", padx=10, pady=5)

        tk.Label(popup, text="COM Port:", bg="white", font=("Arial", 10)).pack(anchor="w", pady=5, padx=10)
        com_port_var = tk.StringVar(value="Select COM Port")
        com_port_dropdown = ttk.Combobox(popup, textvariable=com_port_var, state="readonly", width=18)
        com_port_dropdown.pack(fill="x", padx=10, pady=5)

        # Populate COM ports
        try:
            import serial.tools.list_ports
            com_ports = [port.device for port in serial.tools.list_ports.comports()]
            com_port_dropdown["values"] = com_ports
            if com_ports:
                com_port_var.set(com_ports[0])  # Set the first COM port as default
            else:
                com_port_var.set("No COM Ports Available")
        except ModuleNotFoundError:
            com_port_var.set("pyserial not installed")

        def save_settings():
            baud_rate = baud_rate_var.get()
            com_port = com_port_var.get()
            if not baud_rate or com_port == "Select COM Port" or com_port == "No COM Ports Available":
                messagebox.showerror("Error", "Please enter a valid Baud Rate and select a COM Port.")
            else:
                messagebox.showinfo("Settings Saved", f"Baud Rate: {baud_rate}\nCOM Port: {com_port}")
                popup.destroy()

        tk.Button(
            popup, text="Save Settings", font=("Arial", 11),
            bg="#0047ab", fg="white", relief="flat", bd=0,
            activebackground="#3366cc", padx=8, pady=6, highlightthickness=0,
            command=save_settings
        ).pack(fill='x', pady=10, padx=10)

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

        # Component Dropdown
        tk.Label(control_frame, text="Component:", bg="white", font=("Arial", 10)).pack(side="left", padx=5)
        self.component_var = tk.StringVar(value="Select Component")
        self.component_dropdown = ttk.Combobox(control_frame, textvariable=self.component_var, state="readonly", width=20)
        self.component_dropdown.pack(side="left", padx=5)
        self.component_dropdown.bind("<<ComboboxSelected>>", self.populate_part_numbers)

        # Part Number Dropdown
        tk.Label(control_frame, text="Part Number:", bg="white", font=("Arial", 10)).pack(side="left", padx=5)
        self.part_number_var = tk.StringVar(value="Select Part Number")
        self.part_number_dropdown = ttk.Combobox(control_frame, textvariable=self.part_number_var, state="readonly", width=20)
        self.part_number_dropdown.pack(side="left", padx=5)
        self.part_number_dropdown.bind("<<ComboboxSelected>>", self.populate_parameters)

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
        """Populate the Component dropdown on page load."""
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT componentName FROM orders")
            components = cursor.fetchall()
            conn.close()

            if components:
                self.component_dropdown["values"] = [component[0] for component in components]
                self.component_var.set("Select Component")
            else:
                self.component_dropdown["values"] = []
                self.component_var.set("No Components Available")
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error fetching components: {e}")

    def populate_part_numbers(self, event=None):
        """Populate the Part Number dropdown based on the selected Component."""
        component = self.component_var.get()
        if component == "Select Component" or component == "No Components Available":
            self.part_number_dropdown["values"] = []
            self.part_number_var.set("Select Part Number")
            return

        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT partNumber FROM orders WHERE componentName = ?", (component,))
            part_numbers = [row[0] for row in cursor.fetchall()]
            conn.close()

            if part_numbers:
                self.part_number_dropdown["values"] = part_numbers
                self.part_number_var.set("Select Part Number")
            else:
                self.part_number_dropdown["values"] = []
                self.part_number_var.set("No Part Numbers Available")
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error fetching part numbers: {e}")

    def populate_parameters(self, event=None):
        """Populate the Parameter dropdown based on the selected Component and Part Number."""
        component = self.component_var.get()
        part_number = self.part_number_var.get()
        if component == "Select Component" or part_number == "Select Part Number":
            self.parameter_dropdown["values"] = []
            self.parameter_var.set("Select Parameter")
            return

        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            # Fetch orderId for the selected component and part number
            cursor.execute(
                "SELECT orderId FROM orders WHERE componentName = ? AND partNumber = ?",
                (component, part_number)
            )
            result = cursor.fetchone()
            if not result:
                self.parameter_dropdown["values"] = []
                self.parameter_var.set("No Parameters Available")
                conn.close()
                return

            order_id = result[0]

            # Fetch parameters for the selected orderId
            cursor.execute(
                "SELECT parameterName FROM parametersDetails WHERE orderId = ?",
                (order_id,)
            )
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
        component = self.component_var.get()
        part_number = self.part_number_var.get()
        parameter = self.parameter_var.get()
        low_value = self.low_value_var.get()
        high_value = self.high_value_var.get()

        if component == "Select Component" or part_number == "Select Part Number" or parameter == "Select Parameter" or not low_value or not high_value:
            messagebox.showerror("Error", "Please select valid Component, Part Number, Parameter, and enter valid values.")
            return

        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            # Fetch orderId for the selected component and part number
            cursor.execute(
                "SELECT orderId FROM orders WHERE componentName = ? AND partNumber = ?",
                (component, part_number)
            )
            result = cursor.fetchone()
            if not result:
                messagebox.showerror("Error", "Invalid Component or Part Number selection.")
                conn.close()
                return

            order_id = result[0]

            # Update the parametersDetails table
            cursor.execute(
                """
                UPDATE parametersDetails
                SET low = ?, high = ?
                WHERE orderId = ? AND parameterName = ?
                """,
                (low_value, high_value, order_id, parameter)
            )
            conn.commit()
            conn.close()

            messagebox.showinfo("Values Saved", f"Component: {component}\nPart Number: {part_number}\nParameter: {parameter}\nLow Value: {low_value}\nHigh Value: {high_value}")
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
        """Open a popup to select filters and display filtered measuredValues with restricted columns."""
        popup = tk.Toplevel(self.root)
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
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT operatorName FROM measuredValues")
            operator_names = [row[0] for row in cursor.fetchall()]
            cursor.execute("SELECT DISTINCT partNumber FROM measuredValues")
            part_numbers = [row[0] for row in cursor.fetchall()]
            conn.close()
        except Exception:
            operator_names = []
            part_numbers = []

        tk.Label(popup, text="Operator Name:", bg="white").pack(pady=(15, 2))
        operator_var = tk.StringVar()
        operator_dropdown = ttk.Combobox(popup, textvariable=operator_var, values=[""] + operator_names, state="readonly")
        operator_dropdown.pack()

        tk.Label(popup, text="Part Number:", bg="white").pack(pady=(15, 2))
        partno_var = tk.StringVar()
        partno_dropdown = ttk.Combobox(popup, textvariable=partno_var, values=[""] + part_numbers, state="readonly")
        partno_dropdown.pack()

        def show_report():
            # Fetch restricted columns from user_database
            try:
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                cursor.execute("SELECT column_name FROM user_database")
                columns = [row[0] for row in cursor.fetchall()]
                conn.close()
            except Exception:
                columns = []

            if not columns:
                messagebox.showerror("Error", "No columns selected in user_database.")
                popup.destroy()
                return

            # Build SQL query based on selected filters
            query = "SELECT * FROM measuredValues WHERE 1=1"
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
            result_win = tk.Toplevel(self.root)
            result_win.title("Report Results")
            result_win.geometry("1100x500")
            result_win.config(bg="white")

            # Treeview for data
            tree = ttk.Treeview(result_win, columns=columns, show="headings")
            for col in columns:
                tree.heading(col, text=col)
                tree.column(col, anchor="center", width=140)
            tree.pack(fill="both", expand=True, padx=10, pady=10)

            # Fetch and display filtered data
            try:
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                cursor.execute("PRAGMA table_info(measuredValues)")
                all_mv_cols = [row[1] for row in cursor.fetchall()]
                fetch_cols = set(columns) & set(all_mv_cols)
                fetch_cols.update(["parameterName", "value"])
                fetch_cols = list(fetch_cols)
                col_str = ", ".join([f'"{col}"' for col in fetch_cols])
                cursor.execute(query.replace("SELECT *", f"SELECT {col_str}"), params)
                rows = cursor.fetchall()
                desc = [d[0] for d in cursor.description]
                conn.close()
            except Exception:
                rows = []
                desc = []

            # Helper to extract voltage/resistance from parameterName/value
            def extract_param_value(param_name, value, target):
                if not param_name or not value:
                    return "n/a"
                names = [n.strip().lower() for n in str(param_name).split(",")]
                vals = [v.strip() for v in str(value).split(",")]
                result = []
                for n, v in zip(names, vals):
                    if target in n:
                        result.append(v if v else "n/a")
                return ", ".join(result) if result else "n/a"

            for row in rows:
                row_dict = dict(zip(desc, row))
                display_row = []
                for col in columns:
                    if col.lower() in ("voltage", "resistance"):
                        val = extract_param_value(
                            row_dict.get("parameterName", ""), row_dict.get("value", ""), col.lower()
                        )
                        display_row.append(val)
                    else:
                        v = row_dict.get(col, None)
                        display_row.append(v if v not in (None, "",) else "n/a")
                tree.insert("", "end", values=display_row)

            # --- Print Button ---
            def print_report():
                import tempfile
                import platform
                import subprocess
                try:
                    import openpyxl
                except ImportError:
                    messagebox.showerror("Missing Library", "openpyxl is required for printing as Excel.\nInstall it with: pip install openpyxl")
                    return

                # Create Excel file in temp
                wb = openpyxl.Workbook()
                ws = wb.active
                ws.append(columns)
                for item in tree.get_children():
                    vals = tree.item(item, "values")
                    ws.append(list(vals))
                with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as f:
                    temp_path = f.name
                    wb.save(temp_path)

                # Open system print dialog for the Excel file
                if platform.system() == "Windows":
                    # This will open the default associated app's print dialog (usually Excel)
                    os.startfile(temp_path, "print")
                elif platform.system() == "Darwin":
                    subprocess.run(["open", temp_path])
                else:
                    subprocess.run(["xdg-open", temp_path])

            # --- Save as Excel Button ---
            def save_as_excel():
                try:
                    import openpyxl
                    from tkinter import filedialog
                    wb = openpyxl.Workbook()
                    ws = wb.active
                    ws.append(columns)
                    for item in tree.get_children():
                        vals = tree.item(item, "values")
                        ws.append(list(vals))
                    file_path = filedialog.asksaveasfilename(
                        defaultextension=".xlsx",
                        filetypes=[("Excel files", "*.xlsx"), ("All files", "*")]
                    )
                    if file_path:
                        wb.save(file_path)
                        messagebox.showinfo("Saved", f"Report saved as {file_path}")
                except ImportError:
                    messagebox.showerror("Missing Library", "openpyxl is required to save as Excel.\nInstall it with: pip install openpyxl")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to save Excel file:\n{e}")

            # Button frame for Print and Save as Excel
            btn_frame = tk.Frame(result_win, bg="white")
            btn_frame.pack(side="bottom", pady=10)

            print_btn = tk.Button(
                btn_frame, text="Print", bg="#0047ab", fg="white", font=("Arial", 11),
                command=print_report
            )
            print_btn.pack(side="left", padx=10)

            save_excel_btn = tk.Button(
                btn_frame, text="Save as Excel", bg="#28A745", fg="white", font=("Arial", 11),
                command=save_as_excel
            )
            save_excel_btn.pack(side="left", padx=10)

            popup.destroy()

        tk.Button(popup, text="Show Report", bg="#28A745", fg="white", font=("Arial", 11), command=show_report).pack(pady=25)

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


























