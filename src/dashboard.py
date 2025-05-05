import customtkinter as ctk
from tkinter import messagebox
import sqlite3
from datetime import datetime

cart = []  # Global cart list

def open_dashboard(username, role):
    ctk.set_appearance_mode("dark")
    app = ctk.CTk()
    app.title(f"SuperPOS 2030 - Dashboard ({role})")
    app.geometry("900x600")

    # --- Database fetch ---
    def load_products():
        conn = sqlite3.connect("database/pos.db")
        c = conn.cursor()
        c.execute("SELECT * FROM products")
        rows = c.fetchall()
        conn.close()

        for widget in product_frame.winfo_children():
            widget.destroy()

        for row in rows:
            product_id, name, price, qty = row
            row_text = f"{name} - Rs. {price} ({qty} available)"
            btn = ctk.CTkButton(product_frame, text=row_text,
                                command=lambda r=row: add_to_cart(r))
            btn.pack(pady=3, fill='x')

    # --- Add to Cart ---
    def add_to_cart(product):
        if product[3] <= 0:
            messagebox.showerror("Out of Stock", "This product is unavailable.")
            return
        cart.append(product)
        update_cart()

    # --- Update Cart UI ---
    def update_cart():
        total = 0
        for widget in cart_frame.winfo_children():
            widget.destroy()

        for item in cart:
            ctk.CTkLabel(cart_frame, text=f"{item[1]} - Rs. {item[2]}").pack()
            total += item[2]

        total_label.configure(text=f"Total: Rs. {total}")

    # --- Checkout ---
    def checkout():
        if not cart:
            messagebox.showwarning("Empty", "Cart is empty!")
            return

        conn = sqlite3.connect("database/pos.db")
        c = conn.cursor()
        total = sum([item[2] for item in cart])

        for item in cart:
            c.execute("INSERT INTO sales (product_id, quantity, total, date) VALUES (?, ?, ?, ?)",
                      (item[0], 1, item[2], datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            c.execute("UPDATE products SET quantity = quantity - 1 WHERE id = ?", (item[0],))

        conn.commit()
        conn.close()
        cart.clear()
        update_cart()
        load_products()
        messagebox.showinfo("Success", f"Checkout complete!\nRs. {total} collected.")

    # --- Layout ---
    left_panel = ctk.CTkFrame(app, width=300)
    left_panel.pack(side="left", fill="y", padx=10, pady=10)

    center_panel = ctk.CTkFrame(app)
    center_panel.pack(side="left", fill="both", expand=True, padx=10, pady=10)

    right_panel = ctk.CTkFrame(app, width=250)
    right_panel.pack(side="right", fill="y", padx=10, pady=10)

    # --- Left (Products) ---
    ctk.CTkLabel(left_panel, text="🛍️ Available Products", font=ctk.CTkFont(size=16)).pack(pady=5)
    product_frame = ctk.CTkScrollableFrame(left_panel, width=280, height=500)
    product_frame.pack()

    # --- Center (Cart) ---
    ctk.CTkLabel(center_panel, text="🧾 Shopping Cart", font=ctk.CTkFont(size=16)).pack(pady=5)
    cart_frame = ctk.CTkScrollableFrame(center_panel, width=400, height=400)
    cart_frame.pack(pady=10)

    total_label = ctk.CTkLabel(center_panel, text="Total: Rs. 0.00", font=ctk.CTkFont(size=18, weight="bold"))
    total_label.pack(pady=10)

    ctk.CTkButton(center_panel, text="✅ Checkout", command=checkout).pack(pady=10)
    ctk.CTkButton(center_panel, text="🧹 Clear Cart", command=lambda: [cart.clear(), update_cart()]).pack()

    # --- Right (User Info) ---
    ctk.CTkLabel(right_panel, text=f"👤 Logged in as: {username}", font=ctk.CTkFont(size=14)).pack(pady=20)
    ctk.CTkLabel(right_panel, text="Role: " + role).pack(pady=5)
    ctk.CTkButton(right_panel, text="🔄 Refresh Products", command=load_products).pack(pady=10)
    ctk.CTkButton(right_panel, text="🚪 Logout", fg_color="red", command=app.destroy).pack(pady=40)

    # --- Admin Controls ---
    if role == "admin":
        ctk.CTkLabel(right_panel, text="🛠️ Admin Panel", font=ctk.CTkFont(size=15)).pack(pady=5)

        name_entry = ctk.CTkEntry(right_panel, placeholder_text="Product Name")
        name_entry.pack(pady=5)

        price_entry = ctk.CTkEntry(right_panel, placeholder_text="Price")
        price_entry.pack(pady=5)

        qty_entry = ctk.CTkEntry(right_panel, placeholder_text="Quantity")
        qty_entry.pack(pady=5)

        def add_product():
            name = name_entry.get()
            try:
                price = float(price_entry.get())
                qty = int(qty_entry.get())
            except:
                messagebox.showerror("Invalid", "Enter valid price & quantity.")
                return

            conn = sqlite3.connect("database/pos.db")
            c = conn.cursor()
            c.execute("INSERT INTO products (name, price, quantity) VALUES (?, ?, ?)", (name, price, qty))
            conn.commit()
            conn.close()
            load_products()
            messagebox.showinfo("Added", f"{name} added.")
            name_entry.delete(0, "end")
            price_entry.delete(0, "end")
            qty_entry.delete(0, "end")

        ctk.CTkButton(right_panel, text="➕ Add Product", command=add_product).pack(pady=10)

    load_products()
    app.mainloop()
