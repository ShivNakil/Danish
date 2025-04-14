import tkinter as tk
from tkinter import ttk, messagebox
import subprocess

class OperatorScreen(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Operator Panel")
        self.geometry("1000x600")
        self.configure(bg='white')
        
        # Top Navigation Bar
        self.navbar = tk.Frame(self, bg='#0066FF', height=50)
        self.navbar.pack(fill=tk.X)
        
        # Burger Menu Button
        self.burger_menu = tk.Button(self.navbar, text="☰", font=("Arial", 16), bg="#0066FF", fg="white", bd=0, command=self.toggle_menu)
        self.burger_menu.pack(side=tk.LEFT, padx=10)
        
        tk.Label(self.navbar, text="Operator Panel", fg="white", bg="#0066FF", font=("Arial", 14, "bold")).pack(side=tk.LEFT, padx=10)
        
        self.report_button = tk.Button(self.navbar, text="Generate Report", command=self.generate_report, bg="#0047AB", fg="white")
        self.report_button.pack(side=tk.RIGHT, padx=10)
        
        tk.Button(self.navbar, text="Logout", command=self.logout, bg="#0047AB", fg="white").pack(side=tk.RIGHT, padx=10)
        
        # Burger Menu Frame (Hidden initially)
        self.menu_frame = tk.Frame(self, bg="#0047AB", width=200, height=550)
        self.menu_frame.place(x=-200, y=50)
        self.menu_frame.pack_propagate(False)
        
        tk.Label(self.menu_frame, text="COM Port:", fg="white", bg="#0047AB").pack(pady=5)
        self.com_port = ttk.Combobox(self.menu_frame, values=["COM1", "COM2", "COM3", "COM4"])
        self.com_port.pack(pady=5)
        
        tk.Label(self.menu_frame, text="Baud Rate:", fg="white", bg="#0047AB").pack(pady=5)
        self.baud_rate = ttk.Combobox(self.menu_frame, values=["9600", "115200", "250000"])
        self.baud_rate.pack(pady=5)
        
        # Main content frame - will contain the table and scrollbars
        self.main_frame = tk.Frame(self, bg='white')
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create a container frame for the treeview and scrollbars
        self.tree_container = tk.Frame(self.main_frame, bd=2, relief="solid")
        self.tree_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Define columns
        columns = ("Date & Time", "Operator Name", "Component", "Peak Value", "Low Value", "Measured Value")
        
        # Create horizontal scrollbar
        self.h_scroll = ttk.Scrollbar(self.tree_container, orient="horizontal")
        self.h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Create vertical scrollbar
        self.v_scroll = ttk.Scrollbar(self.tree_container)
        self.v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Create the Treeview with both scrollbars
        self.tree = ttk.Treeview(
            self.tree_container,
            columns=columns,
            show="headings",
            style="Custom.Treeview",
            yscrollcommand=self.v_scroll.set,
            xscrollcommand=self.h_scroll.set,
            selectmode='extended'
        )
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        # Configure the scrollbars
        self.v_scroll.config(command=self.tree.yview)
        self.h_scroll.config(command=self.tree.xview)
        
        # Custom styling for table appearance
        style = ttk.Style()
        style.theme_use("default")  # Ensure headers always appear

        style.configure("Treeview",
                      background="white",
                      foreground="black",
                      rowheight=25,
                      fieldbackground="white",
                      font=('Arial', 10),
                      borderwidth=1,
                      relief="solid")
        
        style.configure("Treeview.Heading",
                      background="#0066FF",
                      foreground="white",
                      padding=5,
                      font=('Arial', 10, 'bold'),
                      relief="solid",
                      borderwidth=1)

        style.configure("Custom.Treeview.Heading",
                        background="#0066FF",
                        foreground="white",
                        font=("Arial", 10, "bold"),
                        relief="ridge",
                        borderwidth=1)

        style.map("Treeview.Heading",
                  background=[("active", "#0047AB")])
        
        # Configure column headings and columns
        for col in columns:
            self.tree.heading(col, text=col, anchor='center')
            self.tree.column(col, anchor='center', stretch=True)

        # Insert sample data
        for i in range(5):
            self.tree.insert("", tk.END, 
                           values=(
                               f"2025-04-03 12:{i:02d}:00", 
                               f"Operator {i%3 + 1}", 
                               f"Battery {chr(65 + (i % 26))}", 
                               f"{3.5 + (i%10)*0.1:.1f}V", 
                               f"{2.5 + (i%5)*0.2:.1f}V", 
                               f"{3.0 + (i%8)*0.15:.2f}V"
                           ))
        
        # Track menu state
        self.menu_open = False
        self.menu_frame.lift()
        
    def toggle_menu(self):
        if self.menu_open:
            self.animate_menu(-200)
        else:
            self.animate_menu(0)
        self.menu_open = not self.menu_open
        
    def animate_menu(self, target_x):
        current_x = self.menu_frame.winfo_x()
        step = 10 if target_x > current_x else -10
        
        def move():
            nonlocal current_x
            current_x += step
            self.menu_frame.place(x=current_x, y=50)
            
            if (step > 0 and current_x < target_x) or (step < 0 and current_x > target_x):
                self.after(10, move)
            else:
                self.menu_frame.place(x=target_x, y=50)
        
        move()
        
    def logout(self):
        messagebox.showinfo("Logout", "Logging out...")
        self.destroy()
        subprocess.Popen(["python", "d:\\Engineering\\manish\\Manish\\login.py"])  # Relaunch login screen
        
    def generate_report(self):
        messagebox.showinfo("Report", "Generating operator-specific report...")
        
if __name__ == "__main__":
    app = OperatorScreen()
    app.mainloop()