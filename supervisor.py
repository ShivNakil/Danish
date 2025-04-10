import tkinter as tk
from tkinter import ttk, messagebox
import subprocess

class HamburgerMenuApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Excel-like Table with Burger Menu")
        self.root.geometry("1200x700")
        self.root.configure(bg="white")
        self.root.minsize(800, 600)

        self.menu_visible = False
        self.menu_width = 250

        # === Top bar ===
        self.topbar = tk.Frame(self.root, height=50, bg="#0047ab")
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
        self.menu_frame = tk.Frame(self.main_area, width=0, bg="#003d99")
        self.menu_frame.pack(side="left", fill="y")
        self.menu_frame.pack_propagate(False)
        self.setup_menu_content()

        # === Table Area ===
        self.table_frame = tk.Frame(self.main_area, bg="white")
        self.table_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        self.create_table()

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

        create_rounded_btn(self.menu_inner, "Create User", self.create_user).pack(pady=10, fill='x')
        create_rounded_btn(self.menu_inner, "Report Generation", self.generate_report).pack(pady=10, fill='x')
        create_rounded_btn(self.menu_inner, "User Logout", self.logout).pack(pady=10, fill='x')

        settings_frame = tk.LabelFrame(
            self.menu_inner, text="Settings", bg="#003d99", fg="white",
            font=("Arial", 11, "bold"), bd=1, padx=10, pady=10,
            relief="flat", highlightbackground="#007bff", highlightthickness=1
        )
        settings_frame.pack(pady=20, fill='both')

        baud_btn = tk.Button(
            settings_frame, text="Baud Rate", font=("Arial", 11),
            bg="#0047ab", fg="white", relief="flat", bd=0,
            activebackground="#3366cc", padx=8, pady=6, highlightthickness=0
        )
        baud_btn.pack(fill='x', pady=5)

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
        columns = ["Date", "Time", "Component Name", "Peak Value", "Low Value"]

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

        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")

        self.table_frame.grid_rowconfigure(0, weight=1)
        self.table_frame.grid_columnconfigure(0, weight=1)

        self.tree.bind("<Double-1>", self.on_double_click)

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
            messagebox.showinfo("Logout", "User logged out")
            self.root.destroy()
            subprocess.Popen(["python", "d:\\Engineering\\manish\\Manish\\login.py"])  # Relaunch login screen

if __name__ == "__main__":
    root = tk.Tk()
    app = HamburgerMenuApp(root)
    root.mainloop()


























