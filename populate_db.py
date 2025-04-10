import sqlite3

# Connect to the database
conn = sqlite3.connect("d:\\Engineering\\Manish\\manish\\login.db")
cursor = conn.cursor()

# Create the users table if it doesn't exist
cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        employee_type TEXT NOT NULL
    )
""")

# Insert initial user data
users = [
    ("Admin User", "admin", "admin123", "admin"),
    ("Supervisor User", "supervisor", "supervisor123", "supervisor"),
    ("Manufacturer User", "manufacturer", "manufacturer123", "manufacturer"),
    ("Operator User", "operator", "operator123", "operator"),
]

cursor.executemany("INSERT OR IGNORE INTO users (name, username, password, employee_type) VALUES (?, ?, ?, ?)", users)
conn.commit()
conn.close()

print("Database populated successfully.")
