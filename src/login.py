import customtkinter as ctk
from tkinter import messagebox
import sqlite3
from src.dashboard import open_dashboard



def login_window():
    ctk.set_appearance_mode("dark")  # 'System', 'Dark', 'Light'
    ctk.set_default_color_theme("blue")

    app = ctk.CTk()
    app.geometry("400x300")
    app.title("🛒 SuperPOS 2030 - Login")

    def perform_login():
        username = username_entry.get()
        password = password_entry.get()

        conn = sqlite3.connect("database/pos.db")
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = c.fetchone()
        conn.close()

        if user:
            messagebox.showinfo("Login Success", f"Welcome {username}!")
            app.destroy()
            open_dashboard(username, user[3])  # pass role
        else:
            messagebox.showerror("Login Failed", "Invalid credentials.")

    ctk.CTkLabel(app, text="🔐 SuperPOS Login", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=20)

    username_entry = ctk.CTkEntry(app, placeholder_text="Username")
    username_entry.pack(pady=10)

    password_entry = ctk.CTkEntry(app, placeholder_text="Password", show="*")
    password_entry.pack(pady=10)

    login_btn = ctk.CTkButton(app, text="Login", command=perform_login)
    login_btn.pack(pady=20)

    app.mainloop()
