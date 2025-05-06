import customtkinter as ctk
from tkinter import messagebox
import sqlite3
import os
from PIL import Image

# Import your dashboard modules
# You'll need to create the inventory_management module
from src.dashboard import open_dashboard
from src.inventory_management import open_inventory_management  # This will need to be created


def login_window():
    ctk.set_appearance_mode("dark")  # 'System', 'Dark', 'Light'
    ctk.set_default_color_theme("blue")

    app = ctk.CTk()
    app.geometry("500x450")
    app.title("🛒 SuperPOS 2030 - Login")
    
    # Create a frame for the logo and title
    header_frame = ctk.CTkFrame(app, corner_radius=0)
    header_frame.pack(fill="x", pady=10)
    
    # Add logo image (create an assets folder and place the image there)
    try:
        # Check if the assets directory exists
        if not os.path.exists("assets"):
            os.makedirs("assets")
            
        # Path to the logo image
        image_path = os.path.join("assets", "superpos_logo.png")
        
        # If the image doesn't exist, we'll handle that in the except block
        logo_image = ctk.CTkImage(light_image=Image.open(image_path),
                                 dark_image=Image.open(image_path),
                                 size=(100, 100))
        logo_label = ctk.CTkLabel(header_frame, image=logo_image, text="")
        logo_label.pack(pady=10)
    except:
        # If the image is not found, display a text placeholder
        logo_label = ctk.CTkLabel(header_frame, text="🛒", font=ctk.CTkFont(size=60))
        logo_label.pack(pady=10)
        print("Note: Create an 'assets' folder and add 'superpos_logo.png' for a logo image")

    # Title label
    ctk.CTkLabel(header_frame, text="SuperPOS 2030", 
                font=ctk.CTkFont(size=24, weight="bold")).pack()
    ctk.CTkLabel(header_frame, text="Point of Sale System", 
                font=ctk.CTkFont(size=16)).pack(pady=5)

    # Login form frame
    login_frame = ctk.CTkFrame(app)
    login_frame.pack(pady=20, padx=40, fill="both", expand=True)

    ctk.CTkLabel(login_frame, text="🔐 User Login", 
                font=ctk.CTkFont(size=20, weight="bold")).pack(pady=20)

    # Username field
    username_frame = ctk.CTkFrame(login_frame, fg_color="transparent")
    username_frame.pack(fill="x", pady=5)
    ctk.CTkLabel(username_frame, text="Username:", width=100, anchor="w").pack(side="left", padx=5)
    username_entry = ctk.CTkEntry(username_frame, placeholder_text="Enter username")
    username_entry.pack(side="left", fill="x", expand=True, padx=5)

    # Password field
    password_frame = ctk.CTkFrame(login_frame, fg_color="transparent")
    password_frame.pack(fill="x", pady=5)
    ctk.CTkLabel(password_frame, text="Password:", width=100, anchor="w").pack(side="left", padx=5)
    password_entry = ctk.CTkEntry(password_frame, placeholder_text="Enter password", show="*")
    password_entry.pack(side="left", fill="x", expand=True, padx=5)

    def perform_login():
        username = username_entry.get()
        password = password_entry.get()

        if not username or not password:
            messagebox.showerror("Login Error", "Username and password cannot be empty.")
            return

        try:
            conn = sqlite3.connect("database/pos.db")
            c = conn.cursor()
            c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
            user = c.fetchone()
            conn.close()

            if user:
                user_id, username, password, role = user
                messagebox.showinfo("Login Success", f"Welcome {username}!")
                app.destroy()
                
                # Direct to appropriate window based on role
                if role.lower() in ['admin', 'inventory', 'manager']:
                    open_inventory_management(username, role)
                elif role.lower() == 'cashier':  # Explicitly handle cashier role
                    open_dashboard(username, role)
                else:  # Fallback for any other roles
                    open_dashboard(username, role)
            else:
                messagebox.showerror("Login Failed", "Invalid username or password.")
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to connect to database: {str(e)}")

    # Login button
    login_btn = ctk.CTkButton(login_frame, text="Login", command=perform_login)
    login_btn.pack(pady=20)

    # Add a status label at the bottom
    status_label = ctk.CTkLabel(app, text="© 2030 SuperPOS - All rights reserved", font=("Arial", 10))
    status_label.pack(side="bottom", pady=5)

    app.mainloop()


if __name__ == "__main__":
    login_window()