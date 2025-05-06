import customtkinter as ctk
from tkinter import messagebox
import sqlite3
from datetime import datetime
from fpdf import FPDF
import os
import platform
from PIL import Image, ImageTk

def open_dashboard(username, role):
    cart = []  # each item is [id, name, price, qty_selected]

    ctk.set_appearance_mode("light")
    app = ctk.CTk()
    app.title(f"LANKA SUPER STORE - POS System")
    app.geometry("1100x770")
    app.configure(fg_color="#CCCCCC")  # Light gray background matching the design

    # Set grid layout for the entire app
    app.grid_rowconfigure(0, weight=1)
    app.grid_columnconfigure(1, weight=1)

    def load_products(search_term=None):
        conn = sqlite3.connect("database/pos.db")
        c = conn.cursor()
        
        if search_term:
            c.execute("SELECT * FROM products WHERE name LIKE ?", (f'%{search_term}%',))
        else:
            c.execute("SELECT * FROM products")
            
        rows = c.fetchall()
        conn.close()

        # Clear existing products
        for widget in product_frame.winfo_children():
            widget.destroy()

        # Create grid of product buttons
        row_idx = 0
        col_idx = 0
        for row in rows:
            product_id, name, price, qty = row
            
            # Create product button
            btn = ctk.CTkButton(
                product_frame,
                text=name,  # Using actual product name from database
                font=("Arial", 14, "bold"),
                width=150,
                height=100,
                fg_color="#DDDDDD",  # Light gray color for product buttons
                text_color="#333333",  # Dark gray text
                hover_color="#BBBBBB",
                corner_radius=10,
                border_width=0,
                anchor="center"
            )
            btn.grid(row=row_idx, column=col_idx, padx=10, pady=10, sticky="nsew")
            btn.configure(command=lambda r=row: open_quantity_popup(r))
            
            # Update grid position
            col_idx += 1
            if col_idx >= 3:  # 3 columns as shown in image
                col_idx = 0
                row_idx += 1

    def search_products():
        search_term = search_entry.get()
        load_products(search_term)

    def open_quantity_popup(product):
        popup = ctk.CTkToplevel(app)
        popup.geometry("300x200")
        popup.title("Select Quantity")
        popup.grab_set()

        product_id, name, price, available_qty = product
        ctk.CTkLabel(popup, text=name, font=("Arial", 16, "bold")).pack(pady=10)
        ctk.CTkLabel(popup, text=f"Available: {available_qty}").pack(pady=5)
        
        qty_frame = ctk.CTkFrame(popup)
        qty_frame.pack(pady=10)
        
        qty_var = ctk.IntVar(value=1)
        
        def decrease_qty():
            if qty_var.get() > 1:
                qty_var.set(qty_var.get() - 1)
                
        def increase_qty():
            if qty_var.get() < available_qty:
                qty_var.set(qty_var.get() + 1)
                
        minus_btn = ctk.CTkButton(qty_frame, text="-", width=40, command=decrease_qty)
        minus_btn.pack(side="left", padx=5)
        
        qty_label = ctk.CTkLabel(qty_frame, textvariable=qty_var, width=40)
        qty_label.pack(side="left", padx=10)
        
        plus_btn = ctk.CTkButton(qty_frame, text="+", width=40, command=increase_qty)
        plus_btn.pack(side="left", padx=5)

        def confirm():
            qty = qty_var.get()
            if qty <= 0 or qty > available_qty:
                messagebox.showerror("Invalid", "Enter a valid quantity")
                return
                
            # Check if product already in cart
            for i, item in enumerate(cart):
                if item[0] == product_id:
                    cart[i][3] += qty
                    update_cart()
                    popup.destroy()
                    return
                    
            cart.append([product_id, name, price, qty])
            update_cart()
            popup.destroy()

        ctk.CTkButton(popup, text="Add to Cart", command=confirm, fg_color="#00AA00").pack(pady=10)

    def update_cart():
        total = 0
        
        # Clear cart display
        for widget in cart_table.winfo_children():
            widget.destroy()
            
        # Add header row
        headers = ["No", "Name", "Qty", "Unit Price", "Amount"]
        for col, header in enumerate(headers):
            lbl = ctk.CTkLabel(cart_table, text=header, font=("Arial", 12, "bold"), text_color="#333333")
            lbl.grid(row=0, column=col, padx=5, pady=5, sticky="w")
        
        # Add cart items
        for index, item in enumerate(cart):
            product_id, name, price, qty = item
            subtotal = price * qty
            
            # Item number
            ctk.CTkLabel(cart_table, text=f"{index+1:02d}.", text_color="#333333").grid(row=index+1, column=0, padx=5, pady=5, sticky="w")
            
            # Name
            ctk.CTkLabel(cart_table, text=name, text_color="#333333").grid(row=index+1, column=1, padx=5, pady=5, sticky="w")
            
            # Quantity
            ctk.CTkLabel(cart_table, text=str(qty), text_color="#333333").grid(row=index+1, column=2, padx=5, pady=5, sticky="w")
            
            # Unit price
            ctk.CTkLabel(cart_table, text=f"{price:.2f}", text_color="#333333").grid(row=index+1, column=3, padx=5, pady=5, sticky="w")
            
            # Amount
            ctk.CTkLabel(cart_table, text=f"{subtotal:.2f}", text_color="#333333").grid(row=index+1, column=4, padx=5, pady=5, sticky="w")
            
            # Delete button (red X)
            delete_btn = ctk.CTkButton(
                cart_table, 
                text="✖", 
                width=25, 
                height=25, 
                fg_color="#FF3333", 
                hover_color="#CC0000", 
                corner_radius=12,
                command=lambda idx=index: remove_item(idx)
            )
            delete_btn.grid(row=index+1, column=5, padx=5, pady=5)
            
            total += subtotal
        
        # Update total items and total amount
        total_items_label.configure(text=f"{len(cart):02d}")
        net_total_label.configure(text=f"{total:.2f}")
        
        # Reset cash and balance if cart is empty
        if len(cart) == 0:
            cash_label.configure(text="0.00")
            balance_amt_label.configure(text="0.00")

    def remove_item(index):
        del cart[index]
        update_cart()

    def generate_receipt(cart_items, total, cash, balance):
        receipt = FPDF()
        receipt.add_page()
        receipt.set_font("Arial", "B", size=16)
        receipt.cell(200, 10, txt="LANKA SUPER STORE", ln=True, align='C')
        receipt.set_font("Arial", size=12)
        receipt.cell(200, 5, txt="Your Shopping Partner", ln=True, align='C')
        receipt.cell(200, 5, txt="---------------------------------", ln=True, align='C')
        receipt.cell(200, 10, txt=f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True, align='C')
        receipt.cell(200, 5, txt=f"Cashier: {username}", ln=True, align='C')
        receipt.ln(10)

        # Table header
        receipt.set_font("Arial", "B", size=12)
        receipt.cell(10, 10, "No", 1)
        receipt.cell(80, 10, "Item", 1)
        receipt.cell(20, 10, "Qty", 1)
        receipt.cell(40, 10, "Unit Price", 1)
        receipt.cell(40, 10, "Amount", 1)
        receipt.ln()

        # Table content
        receipt.set_font("Arial", size=12)
        for i, item in enumerate(cart_items):
            product_id, name, price, qty = item
            total_price = price * qty
            receipt.cell(10, 10, f"{i+1}", 1)
            receipt.cell(80, 10, name, 1)
            receipt.cell(20, 10, str(qty), 1)
            receipt.cell(40, 10, f"{price:.2f}", 1)
            receipt.cell(40, 10, f"{total_price:.2f}", 1)
            receipt.ln()

        # Summary
        receipt.ln(5)
        receipt.set_font("Arial", "B", size=12)
        receipt.cell(150, 10, "NET TOTAL:", 0, 0, 'R')
        receipt.cell(40, 10, f"{total:.2f}", 0, 1, 'R')
        
        receipt.cell(150, 10, "CASH:", 0, 0, 'R')
        receipt.cell(40, 10, f"{cash:.2f}", 0, 1, 'R')
        
        receipt.cell(150, 10, "BALANCE:", 0, 0, 'R')
        receipt.cell(40, 10, f"{balance:.2f}", 0, 1, 'R')
        
        receipt.ln(10)
        receipt.set_font("Arial", size=10)
        receipt.cell(200, 10, txt="Thank you for shopping with Lanka Super Store!", ln=True, align='C')

        filepath = "receipt.pdf"
        receipt.output(filepath)

        if platform.system() == "Windows":
            os.startfile(filepath)
        elif platform.system() == "Darwin":
            os.system(f"open {filepath}")
        else:
            os.system(f"xdg-open {filepath}")

    def clear_cart():
        cart.clear()
        update_cart()

    def checkout():
        if not cart:
            messagebox.showwarning("Empty", "Cart is empty!")
            return

        total = sum([item[2]*item[3] for item in cart])

        checkout_window = ctk.CTkToplevel(app)
        checkout_window.title("Checkout")
        checkout_window.geometry("400x300")
        checkout_window.grab_set()

        # Checkout form
        frame = ctk.CTkFrame(checkout_window)
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(frame, text="CHECKOUT", font=("Arial", 18, "bold")).pack(pady=10)
        
        # Total
        total_frame = ctk.CTkFrame(frame)
        total_frame.pack(fill="x", pady=5)
        ctk.CTkLabel(total_frame, text="NET TOTAL:", font=("Arial", 14, "bold")).pack(side="left", padx=10)
        ctk.CTkLabel(total_frame, text=f"{total:.2f}", font=("Arial", 14)).pack(side="right", padx=10)
        
        # Cash input
        cash_frame = ctk.CTkFrame(frame)
        cash_frame.pack(fill="x", pady=5)
        ctk.CTkLabel(cash_frame, text="CASH:", font=("Arial", 14, "bold")).pack(side="left", padx=10)
        cash_entry = ctk.CTkEntry(cash_frame, font=("Arial", 14))
        cash_entry.pack(side="right", padx=10)
        cash_entry.insert(0, f"{total:.2f}")
        
        # Balance
        balance_frame = ctk.CTkFrame(frame)
        balance_frame.pack(fill="x", pady=5)
        ctk.CTkLabel(balance_frame, text="BALANCE:", font=("Arial", 14, "bold")).pack(side="left", padx=10)
        balance_label = ctk.CTkLabel(balance_frame, text="0.00", font=("Arial", 14))
        balance_label.pack(side="right", padx=10)
        
        def update_balance(*args):
            try:
                cash = float(cash_entry.get())
                balance = cash - total
                balance_label.configure(text=f"{balance:.2f}")
            except:
                balance_label.configure(text="Invalid")
                
        cash_entry.bind("<KeyRelease>", update_balance)
        update_balance()

        def confirm_checkout():
            try:
                cash = float(cash_entry.get())
                if cash < total:
                    messagebox.showerror("Error", "Insufficient cash")
                    return
                    
                conn = sqlite3.connect("database/pos.db")
                c = conn.cursor()
                for item in cart:
                    product_id, name, price, qty = item
                    c.execute("INSERT INTO sales (product_id, quantity, total, date) VALUES (?, ?, ?, ?)",
                              (product_id, qty, price * qty, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                    c.execute("UPDATE products SET quantity = quantity - ? WHERE id = ?", (qty, product_id))
                conn.commit()
                conn.close()

                balance = cash - total
                generate_receipt(cart.copy(), total, cash, balance)
                
                # Update the summary panel
                cash_label.configure(text=f"{cash:.2f}")
                balance_amt_label.configure(text=f"{balance:.2f}")
                
                cart.clear()
                update_cart()
                load_products()
                checkout_window.destroy()
                messagebox.showinfo("Success", f"Checkout complete! Change: Rs. {balance:.2f}")
            except:
                messagebox.showerror("Error", "Invalid cash input")

        # Buttons
        btn_frame = ctk.CTkFrame(frame)
        btn_frame.pack(fill="x", pady=20)
        
        cancel_btn = ctk.CTkButton(btn_frame, text="Cancel", command=checkout_window.destroy, fg_color="#FF3333", hover_color="#CC0000")
        cancel_btn.pack(side="left", padx=10, fill="x", expand=True)
        
        confirm_btn = ctk.CTkButton(btn_frame, text="Checkout", command=confirm_checkout, fg_color="#00AA00", hover_color="#008800")
        confirm_btn.pack(side="right", padx=10, fill="x", expand=True)

    # Main layout with darker gray background matching the design
    app.configure(fg_color="#CCCCCC")

    # Main container frame
    main_container = ctk.CTkFrame(app, fg_color="#CCCCCC", corner_radius=0)
    main_container.pack(fill="both", expand=True, padx=10, pady=10)

    # Header with store logo and name (left side)
    header_frame = ctk.CTkFrame(main_container, height=80, fg_color="#CCCCCC", corner_radius=0)
    header_frame.pack(fill="x", pady=0)
    
    # Logo and store name side by side
    logo_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
    logo_frame.pack(side="left", padx=20)
    
    # Try to load store logo as a circular image
    try:
        logo_img = Image.open("assets/logo.png")  # Update with your logo path
        logo_img = logo_img.resize((50, 50))
        logo_photo = ImageTk.PhotoImage(logo_img)
        logo_label = ctk.CTkLabel(logo_frame, text="", image=logo_photo)
        logo_label.image = logo_photo
        logo_label.pack(side="left", padx=(0, 10))
    except:
        # If logo loading fails, create a placeholder
        logo_placeholder = ctk.CTkFrame(logo_frame, width=50, height=50, corner_radius=25, fg_color="#888888")
        logo_placeholder.pack(side="left", padx=(0, 10))
    
    # Store name with shopping cart icon
    name_frame = ctk.CTkFrame(logo_frame, fg_color="transparent")
    name_frame.pack(side="left")
    
    store_name_frame = ctk.CTkFrame(name_frame, fg_color="transparent")
    store_name_frame.pack(anchor="w")
    
    l_label = ctk.CTkLabel(store_name_frame, text="L", font=("Arial", 28, "bold"))
    l_label.pack(side="left", padx=0)
    
    anka_label = ctk.CTkLabel(store_name_frame, text="ANKA", font=("Arial", 24, "bold"))
    anka_label.pack(side="left", padx=0)
    
    # Shopping cart icon
    cart_icon_frame = ctk.CTkFrame(store_name_frame, fg_color="transparent")
    cart_icon_frame.pack(side="left", padx=5)
    
    try:
        cart_icon = Image.open("assets/cart_icon.png")  # Update with your icon path
        cart_icon = cart_icon.resize((30, 30))
        cart_photo = ImageTk.PhotoImage(cart_icon)
        cart_icon_label = ctk.CTkLabel(cart_icon_frame, text="", image=cart_photo)
        cart_icon_label.image = cart_photo
        cart_icon_label.pack()
    except:
        # If cart icon loading fails, use text
        cart_icon_label = ctk.CTkLabel(cart_icon_frame, text="🛒", font=("Arial", 24))
        cart_icon_label.pack()
    
    super_store_label = ctk.CTkLabel(name_frame, text="Super\nStore", font=("Arial", 14))
    super_store_label.pack(anchor="w")
    
    # Main content area
    content_frame = ctk.CTkFrame(main_container, fg_color="#CCCCCC")
    content_frame.pack(fill="both", expand=True, padx=0, pady=5)
    
    # Left panel - Products
    left_panel = ctk.CTkFrame(content_frame, width=400, fg_color="#CCCCCC")
    left_panel.pack(side="left", fill="both", expand=True, padx=5, pady=5)
    
    # Search box with rounded corners
    search_frame = ctk.CTkFrame(left_panel, height=40, fg_color="#DDDDDD", corner_radius=20)
    search_frame.pack(fill="x", pady=10, padx=10)
    
    search_entry = ctk.CTkEntry(search_frame, placeholder_text="Search here", border_width=0, 
                               fg_color="transparent", height=30, text_color="#666666")
    search_entry.pack(side="left", fill="both", expand=True, padx=10, pady=5)
    
    search_btn = ctk.CTkButton(search_frame, text="🔍", width=30, fg_color="transparent", 
                              hover_color="#BBBBBB", corner_radius=20, command=search_products)
    search_btn.pack(side="right", padx=5, pady=5)
    
    search_entry.bind("<Return>", lambda event: search_products())
    
    # Products grid in a scrollable frame
    product_frame = ctk.CTkScrollableFrame(left_panel, fg_color="#CCCCCC")
    product_frame.pack(fill="both", expand=True, pady=5)
    
    # Configure grid for product buttons
    for i in range(3):  # 3 columns
        product_frame.grid_columnconfigure(i, weight=1)
    
    # Right panel - Cart and checkout
    right_panel = ctk.CTkFrame(content_frame, width=450, fg_color="#DDDDDD", corner_radius=10)
    right_panel.pack(side="right", fill="both", expand=False, padx=5, pady=5)
    
    # Cart header
    cart_header = ctk.CTkFrame(right_panel, height=50, fg_color="transparent")
    cart_header.pack(fill="x", padx=20, pady=10)
    
    # Cart icon and text
    cart_label_frame = ctk.CTkFrame(cart_header, fg_color="transparent")
    cart_label_frame.pack(side="left")
    
    try:
        small_cart_icon = Image.open("assets/cart_icon.png")  # Update with your icon path
        small_cart_icon = small_cart_icon.resize((25, 25))
        small_cart_photo = ImageTk.PhotoImage(small_cart_icon)
        small_cart_label = ctk.CTkLabel(cart_label_frame, text="", image=small_cart_photo)
        small_cart_label.image = small_cart_photo
        small_cart_label.pack(side="left", padx=(0, 5))
    except:
        # If icon loading fails, use text
        small_cart_label = ctk.CTkLabel(cart_label_frame, text="🛒", font=("Arial", 18))
        small_cart_label.pack(side="left", padx=(0, 5))
    
    ctk.CTkLabel(cart_label_frame, text="CART", font=("Arial", 18, "bold")).pack(side="left")
    
    # Cart items table
    cart_table = ctk.CTkScrollableFrame(right_panel, fg_color="#EEEEEE", corner_radius=5)
    cart_table.pack(fill="both", expand=True, padx=20, pady=10)
    
    # Configure cart table columns
    for i in range(6):  # 6 columns (No, Name, Qty, Unit Price, Amount, Delete)
        cart_table.grid_columnconfigure(i, weight=1 if i == 1 else 0)
    
    # User info panel with green circular icon
    user_panel = ctk.CTkFrame(right_panel, fg_color="#EEEEEE", corner_radius=8)
    user_panel.pack(fill="x", padx=20, pady=(0, 10))
    
    # User icon (green circle with profile)
    user_icon_frame = ctk.CTkFrame(user_panel, width=30, height=30, corner_radius=15, fg_color="#00AA00")
    user_icon_frame.pack(side="left", padx=10, pady=10)
    
    # Try to load a user icon, or use a placeholder
    try:
        user_icon = Image.open("assets/user_icon.png")  # Update with your icon path
        user_icon = user_icon.resize((20, 20))
        user_photo = ImageTk.PhotoImage(user_icon)
        user_icon_label = ctk.CTkLabel(user_icon_frame, text="", image=user_photo)
        user_icon_label.image = user_photo
        user_icon_label.pack()
    except:
        # If user icon loading fails, use text placeholder
        user_icon_label = ctk.CTkLabel(user_icon_frame, text="👤", font=("Arial", 14), text_color="#FFFFFF")
        user_icon_label.pack()
    
    # Username and role
    ctk.CTkLabel(user_panel, text=f"{username}({role})", font=("Arial", 12)).pack(side="left", padx=5, pady=10)
    
    # Summary panel
    summary_panel = ctk.CTkFrame(right_panel, fg_color="#FFFFFF", corner_radius=8)
    summary_panel.pack(fill="x", padx=20, pady=5)
    
    # NET TOTAL
    total_row = ctk.CTkFrame(summary_panel, fg_color="transparent")
    total_row.pack(fill="x", padx=10, pady=5)
    ctk.CTkLabel(total_row, text="NET TOTAL", font=("Arial", 14, "bold"), text_color="#333333").pack(side="left")
    net_total_label = ctk.CTkLabel(total_row, text="0.00", font=("Arial", 14), text_color="#333333")
    net_total_label.pack(side="right")
    
    # CASH row
    cash_row = ctk.CTkFrame(summary_panel, fg_color="transparent")
    cash_row.pack(fill="x", padx=10, pady=2)
    ctk.CTkLabel(cash_row, text="CASH", font=("Arial", 12), text_color="#333333").pack(side="left")
    cash_label = ctk.CTkLabel(cash_row, text="0.00", font=("Arial", 12), text_color="#333333")
    cash_label.pack(side="right")
    
    # BALANCE row
    balance_row = ctk.CTkFrame(summary_panel, fg_color="transparent")
    balance_row.pack(fill="x", padx=10, pady=2)
    ctk.CTkLabel(balance_row, text="BALANCE", font=("Arial", 12), text_color="#333333").pack(side="left")
    balance_amt_label = ctk.CTkLabel(balance_row, text="0.00", font=("Arial", 12), text_color="#333333")
    balance_amt_label.pack(side="right")
    
    # Total items row
    items_row = ctk.CTkFrame(summary_panel, fg_color="transparent")
    items_row.pack(fill="x", padx=10, pady=5)
    ctk.CTkLabel(items_row, text="TOTAL ITEMS", font=("Arial", 12), text_color="#333333").pack(side="left")
    total_items_label = ctk.CTkLabel(items_row, text="00", font=("Arial", 12), text_color="#333333")
    total_items_label.pack(side="right")
    
    # Action buttons
    buttons_frame = ctk.CTkFrame(right_panel, fg_color="transparent")
    buttons_frame.pack(fill="x", padx=20, pady=10)
    
    # Clear Cart button (red)
    clear_btn = ctk.CTkButton(buttons_frame, text="Clear Cart", fg_color="#FF0000", hover_color="#CC0000",
                             command=clear_cart, height=40, corner_radius=5)
    clear_btn.pack(side="left", padx=5, fill="x", expand=True)
    
    # Checkout button (green)
    checkout_btn = ctk.CTkButton(buttons_frame, text="Checkout", fg_color="#00AA00", hover_color="#008800",
                                command=checkout, height=40, corner_radius=5)
    checkout_btn.pack(side="right", padx=5, fill="x", expand=True)
    
    # Logout button - round red button
    logout_btn = ctk.CTkButton(right_panel, text="Logout", fg_color="#FF0000", hover_color="#CC0000",
                              command=app.destroy, width=100, height=35, corner_radius=17)
    logout_btn.pack(side="right", padx=20, pady=10)

    # Admin Panel (if applicable)
    if role.lower() == "admin":
        admin_panel = ctk.CTkFrame(left_panel, fg_color="#EEEEEE", corner_radius=8)
        admin_panel.pack(fill="x", pady=10, padx=10)
        
        ctk.CTkLabel(admin_panel, text="🛠️ Admin Panel", font=("Arial", 14, "bold")).pack(pady=5)
        
        name_entry = ctk.CTkEntry(admin_panel, placeholder_text="Product Name")
        price_entry = ctk.CTkEntry(admin_panel, placeholder_text="Price")
        qty_entry = ctk.CTkEntry(admin_panel, placeholder_text="Quantity")
        name_entry.pack(padx=10, pady=5, fill="x")
        price_entry.pack(padx=10, pady=5, fill="x")
        qty_entry.pack(padx=10, pady=5, fill="x")

        def add_product():
            try:
                name = name_entry.get()
                price = float(price_entry.get())
                qty = int(qty_entry.get())
                
                if not name:
                    messagebox.showerror("Invalid", "Product name cannot be empty")
                    return
                
                conn = sqlite3.connect("database/pos.db")
                c = conn.cursor()
                c.execute("INSERT INTO products (name, price, quantity) VALUES (?, ?, ?)", (name, price, qty))
                conn.commit()
                conn.close()
                load_products()
                name_entry.delete(0, "end")
                price_entry.delete(0, "end")
                qty_entry.delete(0, "end")
                messagebox.showinfo("Added", f"{name} added successfully.")
            except ValueError:
                messagebox.showerror("Invalid", "Enter valid price and quantity values")
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred: {str(e)}")

        ctk.CTkButton(admin_panel, text="Add Product", command=add_product, fg_color="#00AA00").pack(padx=10, pady=10, fill="x")

    # Initial load
    load_products()
    update_cart()
    app.mainloop()