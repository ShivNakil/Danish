import tkinter as tk
from tkinter import ttk
from ttkbootstrap import Style

def toggle_settings():
    if settings_frame.winfo_ismapped():
        settings_frame.pack_forget()
    else:
        settings_frame.pack(fill='x', padx=10, pady=5)

def toggle_menu(event=None):
    if burger_menu.menu.winfo_ismapped():
        burger_menu.menu.unpost()
    else:
        burger_menu.menu.post(burger_menu.winfo_rootx(), burger_menu.winfo_rooty() + burger_menu.winfo_height())

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
sidebar = tk.Frame(root, bg='#0047ab', width=250)
sidebar.grid(row=0, column=0, sticky='ns')
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
main_frame.grid(row=0, column=1, sticky='nsew')
main_frame.grid_rowconfigure(1, weight=1)
main_frame.grid_columnconfigure(0, weight=1)

# Menubar with blue background
menubar = tk.Frame(main_frame, bg='#0047ab', height=80)
menubar.grid(row=0, column=0, sticky='ew')
menubar.grid_propagate(False)

# Burger Menu with blue styling
burger_menu = tk.Menubutton(
    menubar, 
    text="☰", 
    bg='#0047ab', 
    fg='white', 
    activebackground='#003366',
    relief='flat', 
    width=3,
    font=('Arial', 16)
)

# Menu with blue styling
burger_menu.menu = tk.Menu(
    burger_menu, 
    tearoff=0,
    bg='#0047ab',
    fg='white',
    activebackground='#003366',
    activeforeground='white',
    bd=0
)

burger_menu.menu.add_command(label="User Logout")
burger_menu.menu.add_command(label="Settings", command=toggle_settings)
burger_menu.menu.add_command(label="Help")
burger_menu["menu"] = burger_menu.menu
burger_menu.pack(side='left', padx=20, pady=10)
burger_menu.bind("<Button-1>", toggle_menu)

# Right-side buttons
ttk.Button(menubar, text="User Database", bootstyle='primary', padding=(15, 10)).pack(side='right', padx=10, pady=10)
ttk.Button(menubar, text="User Request", bootstyle='primary', padding=(15, 10)).pack(side='right', padx=10, pady=10)

# Table with scrollbars
table_container = tk.Frame(main_frame)
table_container.grid(row=1, column=0, sticky='nsew', padx=20, pady=20)

canvas = tk.Canvas(table_container)
scroll_y = ttk.Scrollbar(table_container, orient="vertical", command=canvas.yview)
scroll_x = ttk.Scrollbar(table_container, orient="horizontal", command=canvas.xview)
scrollable_frame = tk.Frame(canvas)

scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)

canvas.pack(side="left", fill="both", expand=True)
scroll_y.pack(side="right", fill="y")
scroll_x.pack(side="bottom", fill="x")

# Table cells
rows, cols = 15, 8
cells = {}
for r in range(rows):
    for c in range(cols):
        cell = tk.Entry(scrollable_frame, width=18, justify='center', relief='ridge', borderwidth=1, font=('Arial', 10))
        cell.grid(row=r, column=c, sticky='nsew', padx=2, pady=2)
        cells[(r, c)] = cell

for c in range(cols):
    scrollable_frame.grid_columnconfigure(c, weight=1, uniform="cols")
for r in range(rows):
    scrollable_frame.grid_rowconfigure(r, weight=1, uniform="rows")

root.bind('<Configure>', on_resize)
root.mainloop() 

 














