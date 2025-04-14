import tkinter as tk
from tkinter import ttk, messagebox
try:
    import serial.tools.list_ports
except ModuleNotFoundError:
    messagebox.showerror("Module Error", "The 'pyserial' module is not installed. Please install it using 'pip install pyserial'.")
    exit()

class OperatorApp:
    def __init__(self, root, username):
        self.root = root
        self.root.title(f"Operator Screen - {username}")  # Display logged-in user's name
        self.root.geometry("800x500")
        self.root.configure(bg="white")
        self.root.minsize(600, 400)

        # === Top Bar with Username ===
        self.topbar = tk.Frame(self.root, height=50, bg="#0047ab")
        self.topbar.pack(side="top", fill="x")

        self.title_label = tk.Label(
            self.topbar, text=f"Welcome, {username}", font=("Arial", 16, "bold"),
            bg="#0047ab", fg="white"
        )
        self.title_label.pack(pady=10)

        # === Main Area ===
        self.main_area = tk.Frame(self.root, bg="white")
        self.main_area.pack(fill="both", expand=True, padx=20, pady=20)

        # === COM Port Selection ===
        self.com_port_var = tk.StringVar(value="Select COM Port")
        tk.Label(self.main_area, text="Select COM Port:", font=("Arial", 12), bg="white").grid(row=0, column=0, sticky="e", pady=5)
        self.com_port_dropdown = ttk.Combobox(self.main_area, textvariable=self.com_port_var, state="readonly", width=30)
        self.com_port_dropdown.grid(row=0, column=1, padx=10)
        self.refresh_com_ports()

        # === Baud Rate Setting ===
        self.baud_rate_var = tk.StringVar()
        tk.Label(self.main_area, text="Enter Baud Rate:", font=("Arial", 12), bg="white").grid(row=1, column=0, sticky="e", pady=5)
        self.baud_rate_entry = tk.Entry(self.main_area, textvariable=self.baud_rate_var, width=33)
        self.baud_rate_entry.grid(row=1, column=1, padx=10)

        # === Save Button ===
        self.save_button = tk.Button(
            self.main_area, text="Save Settings", font=("Arial", 12, "bold"),
            bg="#0047ab", fg="white", command=self.save_settings
        )
        self.save_button.grid(row=2, column=0, columnspan=2, pady=20)

    def refresh_com_ports(self):
        """Refresh the COM port dropdown values dynamically."""
        com_ports = [port.device for port in serial.tools.list_ports.comports()]
        self.com_port_dropdown["values"] = com_ports
        if com_ports:
            self.com_port_var.set(com_ports[0])  # Set the first COM port as default
        else:
            self.com_port_var.set("No COM Ports Available")

    def save_settings(self):
        """Save the selected COM port and baud rate."""
        com_port = self.com_port_var.get()
        baud_rate = self.baud_rate_var.get()
        if com_port == "No COM Ports Available" or not baud_rate.isdigit():
            messagebox.showerror("Error", "Please select a valid COM port and enter a numeric baud rate.")
        else:
            messagebox.showinfo("Settings Saved", f"COM Port: {com_port}\nBaud Rate: {baud_rate}")

if __name__ == "__main__":
    # Simulate fetching the logged-in user's name
    logged_in_user = "John Doe"  # Replace this with actual logic to fetch the username
    root = tk.Tk()
    app = OperatorApp(root, logged_in_user)
    root.mainloop()


























