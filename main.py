import tkinter as tk
from tkinter import messagebox
import sqlite3

# --- Database Setup ---
conn = sqlite3.connect("pos.db")
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        role TEXT
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        price REAL NOT NULL
    )
''')

# Default admin user එකක් add කරන්න
cursor.execute("SELECT * FROM users WHERE username = 'admin'")
if not cursor.fetchone():
    cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", ('admin', 'admin123', 'admin'))
    conn.commit()

# --- Login Function ---
def login():
    username = entry_username.get()
    password = entry_password.get()

    cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    result = cursor.fetchone()

    if result:
        messagebox.showinfo("Login සාර්ථකයි", f"ආයුබෝවන් {username} ({result[3]})")
        window.destroy()
        open_pos_window()
    else:
        messagebox.showerror("Login අසාර්ථකයි", "Username හෝ Password වැරදියි!")

# --- POS Dashboard ---
def open_pos_window():
    pos = tk.Tk()
    pos.title("POS පද්ධතිය")
    pos.geometry("400x400")

    def add_product():
        name = entry_name.get()
        price = entry_price.get()

        if name and price:
            try:
                cursor.execute("INSERT INTO products (name, price) VALUES (?, ?)", (name, float(price)))
                conn.commit()
                messagebox.showinfo("සාර්ථකයි", "භාණ්ඩය එකතු විය!")
                entry_name.delete(0, tk.END)
                entry_price.delete(0, tk.END)
            except:
                messagebox.showerror("දෝෂයක්", "මිලට අංකයක් ලබාදෙන්න!")
        else:
            messagebox.showwarning("අවවාදයයි", "සියළු පෝරම පුරවන්න!")

    tk.Label(pos, text="භාණ්ඩ නම").pack(pady=5)
    entry_name = tk.Entry(pos)
    entry_name.pack()

    tk.Label(pos, text="මිල").pack(pady=5)
    entry_price = tk.Entry(pos)
    entry_price.pack()

    tk.Button(pos, text="භාණ්ඩය එකතු කරන්න", command=add_product).pack(pady=10)

    pos.mainloop()

# --- Login UI ---
window = tk.Tk()
window.title("POS Login")
window.geometry("300x200")

tk.Label(window, text="Username").pack(pady=5)
entry_username = tk.Entry(window)
entry_username.pack()

tk.Label(window, text="Password").pack(pady=5)
entry_password = tk.Entry(window, show="*")
entry_password.pack()

tk.Button(window, text="Login", command=login).pack(pady=10)

window.mainloop()
