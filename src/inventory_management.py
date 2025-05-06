import customtkinter as ctk
from tkinter import messagebox, ttk
import sqlite3
from datetime import datetime

def open_inventory_management(username, role):
    ctk.set_appearance_mode("dark")
    app = ctk.CTk()
    app.title(f"SuperPOS 2030 - Inventory Management ({role})")
    app.geometry("1000x600")

    # --- Main frames ---
    top_frame = ctk.CTkFrame(app)
    top_frame.pack(fill="x", padx=10, pady=10)

    main_frame = ctk.CTkFrame(app)
    main_frame.pack(fill="both", expand=True, padx=10, pady=10)

    # --- Header content ---
    ctk.CTkLabel(top_frame, text="🏪 Inventory Management System", 
                font=ctk.CTkFont(size=24, weight="bold")).pack(side="left", padx=20)
    
    user_info = ctk.CTkFrame(top_frame, fg_color="transparent")
    user_info.pack(side="right", padx=20)
    
    ctk.CTkLabel(user_info, text=f"👤 User: {username}", 
                font=ctk.CTkFont(size=14)).pack(side="top")
    ctk.CTkLabel(user_info, text=f"Role: {role}", 
                font=ctk.CTkFont(size=12)).pack(side="top")
    
    # --- Tabs ---
    tabview = ctk.CTkTabview(main_frame)
    tabview.pack(fill="both", expand=True)
    
    tab_products = tabview.add("Products")
    tab_sales = tabview.add("Sales History")
    tab_users = tabview.add("User Management")
    
    # --- Products Tab ---
    products_frame = ctk.CTkFrame(tab_products)
    products_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)
    
    # Table for products
    columns = ('id', 'name', 'price', 'quantity')
    product_tree = ttk.Treeview(products_frame, columns=columns, show='headings')
    
    # Define headings
    for col in columns:
        product_tree.heading(col, text=col.title())
        product_tree.column(col, width=100)
    
    product_tree.pack(fill="both", expand=True, pady=10)
    
    # Product controls
    product_controls = ctk.CTkFrame(tab_products)
    product_controls.pack(side="right", fill="y", padx=10, pady=10)
    
    ctk.CTkLabel(product_controls, text="Product Management", 
                font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)
    
    # Product form
    name_var = ctk.StringVar()
    price_var = ctk.StringVar()
    qty_var = ctk.StringVar()
    
    ctk.CTkLabel(product_controls, text="Product Name").pack(anchor="w", pady=(10, 0))
    name_entry = ctk.CTkEntry(product_controls, textvariable=name_var, width=200)
    name_entry.pack(pady=(0, 10))
    
    ctk.CTkLabel(product_controls, text="Price").pack(anchor="w", pady=(5, 0))
    price_entry = ctk.CTkEntry(product_controls, textvariable=price_var, width=200)
    price_entry.pack(pady=(0, 10))
    
    ctk.CTkLabel(product_controls, text="Quantity").pack(anchor="w", pady=(5, 0))
    qty_entry = ctk.CTkEntry(product_controls, textvariable=qty_var, width=200)
    qty_entry.pack(pady=(0, 10))
    
    selected_id = None
    
    # --- Load Products ---
    def load_products():
        # Clear existing data
        for item in product_tree.get_children():
            product_tree.delete(item)
        
        # Get data from database
        conn = sqlite3.connect("database/pos.db")
        c = conn.cursor()
        c.execute("SELECT * FROM products")
        rows = c.fetchall()
        conn.close()
        
        # Insert into treeview
        for row in rows:
            product_tree.insert('', 'end', values=row)
    
    # --- Add Product ---
    def add_product():
        try:
            name = name_var.get()
            price = float(price_var.get())
            qty = int(qty_var.get())
            
            if not name:
                messagebox.showerror("Error", "Product name cannot be empty")
                return
            
            conn = sqlite3.connect("database/pos.db")
            c = conn.cursor()
            c.execute("INSERT INTO products (name, price, quantity) VALUES (?, ?, ?)", 
                     (name, price, qty))
            conn.commit()
            conn.close()
            
            load_products()
            clear_form()
            messagebox.showinfo("Success", f"Product '{name}' added successfully")
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid numbers for price and quantity")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add product: {str(e)}")
    
    # --- Update Product ---
    def update_product():
        if not selected_id:
            messagebox.showwarning("No Selection", "Please select a product to update")
            return
        
        try:
            name = name_var.get()
            price = float(price_var.get())
            qty = int(qty_var.get())
            
            conn = sqlite3.connect("database/pos.db")
            c = conn.cursor()
            c.execute("UPDATE products SET name=?, price=?, quantity=? WHERE id=?", 
                     (name, price, qty, selected_id))
            conn.commit()
            conn.close()
            
            load_products()
            clear_form()
            messagebox.showinfo("Success", "Product updated successfully")
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid numbers for price and quantity")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update product: {str(e)}")
    
    # --- Delete Product ---
    def delete_product():
        if not selected_id:
            messagebox.showwarning("No Selection", "Please select a product to delete")
            return
        
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this product?"):
            try:
                conn = sqlite3.connect("database/pos.db")
                c = conn.cursor()
                c.execute("DELETE FROM products WHERE id=?", (selected_id,))
                conn.commit()
                conn.close()
                
                load_products()
                clear_form()
                messagebox.showinfo("Success", "Product deleted successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete product: {str(e)}")
    
    # --- Clear Form ---
    def clear_form():
        global selected_id
        selected_id = None
        name_var.set("")
        price_var.set("")
        qty_var.set("")
    
    # --- Select Product ---
    def on_product_select(event):
        global selected_id
        
        selected = product_tree.focus()
        if not selected:
            return
            
        values = product_tree.item(selected, 'values')
        if values:
            selected_id = values[0]
            name_var.set(values[1])
            price_var.set(values[2])
            qty_var.set(values[3])
    
    # Bind selection event
    product_tree.bind('<<TreeviewSelect>>', on_product_select)
    
    # Add buttons
    button_frame = ctk.CTkFrame(product_controls, fg_color="transparent")
    button_frame.pack(pady=20)
    
    ctk.CTkButton(button_frame, text="Add", command=add_product, width=80).pack(side="left", padx=5)
    ctk.CTkButton(button_frame, text="Update", command=update_product, width=80).pack(side="left", padx=5)
    ctk.CTkButton(button_frame, text="Delete", command=delete_product, fg_color="red", width=80).pack(side="left", padx=5)
    
    ctk.CTkButton(product_controls, text="Clear Form", command=clear_form, width=180).pack(pady=10)
    ctk.CTkButton(product_controls, text="Refresh", command=load_products, width=180).pack(pady=10)
    
    # --- Sales History Tab ---
    sales_frame = ctk.CTkFrame(tab_sales)
    sales_frame.pack(fill="both", expand=True, padx=10, pady=10)
    
    # Table for sales
    sales_columns = ('id', 'product_id', 'quantity', 'total', 'date')
    sales_tree = ttk.Treeview(sales_frame, columns=sales_columns, show='headings')
    
    # Define headings
    for col in sales_columns:
        sales_tree.heading(col, text=col.title())
        sales_tree.column(col, width=100)
    
    sales_tree.pack(fill="both", expand=True, pady=10)
    
    # --- Load Sales ---
    def load_sales():
        # Clear existing data
        for item in sales_tree.get_children():
            sales_tree.delete(item)
        
        # Get data from database
        conn = sqlite3.connect("database/pos.db")
        c = conn.cursor()
        c.execute("SELECT s.id, s.product_id, p.name, s.quantity, s.total, s.date FROM sales s JOIN products p ON s.product_id = p.id ORDER BY s.date DESC")
        rows = c.fetchall()
        conn.close()
        
        # Insert into treeview
        for row in rows:
            sales_tree.insert('', 'end', values=(row[0], row[1], row[2], row[3], row[4], row[5]))
    
    ctk.CTkButton(sales_frame, text="Refresh Sales Data", command=load_sales).pack(pady=10)
    
    # --- User Management Tab ---
    if role.lower() == "admin":  # Only admin can manage users
        users_frame = ctk.CTkFrame(tab_users)
        users_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        
        # Table for users
        users_columns = ('id', 'username', 'role')
        users_tree = ttk.Treeview(users_frame, columns=users_columns, show='headings')
        
        # Define headings
        for col in users_columns:
            users_tree.heading(col, text=col.title())
            users_tree.column(col, width=100)
        
        users_tree.pack(fill="both", expand=True, pady=10)
        
        # User controls
        user_controls = ctk.CTkFrame(tab_users)
        user_controls.pack(side="right", fill="y", padx=10, pady=10)
        
        ctk.CTkLabel(user_controls, text="User Management", 
                    font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)
        
        # User form
        user_name_var = ctk.StringVar()
        user_pass_var = ctk.StringVar()
        user_role_var = ctk.StringVar()
        
        ctk.CTkLabel(user_controls, text="Username").pack(anchor="w", pady=(10, 0))
        user_name_entry = ctk.CTkEntry(user_controls, textvariable=user_name_var, width=200)
        user_name_entry.pack(pady=(0, 10))
        
        ctk.CTkLabel(user_controls, text="Password").pack(anchor="w", pady=(5, 0))
        user_pass_entry = ctk.CTkEntry(user_controls, textvariable=user_pass_var, width=200, show="*")
        user_pass_entry.pack(pady=(0, 10))
        
        ctk.CTkLabel(user_controls, text="Role").pack(anchor="w", pady=(5, 0))
        role_combo = ctk.CTkComboBox(user_controls, values=["admin", "manager", "inventory", "cashier"], 
                                    variable=user_role_var, width=200)
        role_combo.pack(pady=(0, 10))
        
        user_selected_id = None
        
        # --- Load Users ---
        def load_users():
            # Clear existing data
            for item in users_tree.get_children():
                users_tree.delete(item)
            
            # Get data from database
            conn = sqlite3.connect("database/pos.db")
            c = conn.cursor()
            c.execute("SELECT id, username, role FROM users")
            rows = c.fetchall()
            conn.close()
            
            # Insert into treeview
            for row in rows:
                users_tree.insert('', 'end', values=row)
        
        # --- Add User ---
        def add_user():
            try:
                username = user_name_var.get()
                password = user_pass_var.get()
                role = user_role_var.get()
                
                if not username or not password or not role:
                    messagebox.showerror("Error", "All fields are required")
                    return
                
                conn = sqlite3.connect("database/pos.db")
                c = conn.cursor()
                c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", 
                         (username, password, role))
                conn.commit()
                conn.close()
                
                load_users()
                clear_user_form()
                messagebox.showinfo("Success", f"User '{username}' added successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add user: {str(e)}")
        
        # --- Update User ---
        def update_user():
            if not user_selected_id:
                messagebox.showwarning("No Selection", "Please select a user to update")
                return
            
            try:
                username = user_name_var.get()
                password = user_pass_var.get()
                role = user_role_var.get()
                
                if not username or not role:
                    messagebox.showerror("Error", "Username and role are required")
                    return
                
                conn = sqlite3.connect("database/pos.db")
                c = conn.cursor()
                
                # Update with or without password change
                if password:
                    c.execute("UPDATE users SET username=?, password=?, role=? WHERE id=?", 
                             (username, password, role, user_selected_id))
                else:
                    c.execute("UPDATE users SET username=?, role=? WHERE id=?", 
                             (username, role, user_selected_id))
                
                conn.commit()
                conn.close()
                
                load_users()
                clear_user_form()
                messagebox.showinfo("Success", "User updated successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update user: {str(e)}")
        
        # --- Delete User ---
        def delete_user():
            if not user_selected_id:
                messagebox.showwarning("No Selection", "Please select a user to delete")
                return
            
            if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this user?"):
                try:
                    conn = sqlite3.connect("database/pos.db")
                    c = conn.cursor()
                    c.execute("DELETE FROM users WHERE id=?", (user_selected_id,))
                    conn.commit()
                    conn.close()
                    
                    load_users()
                    clear_user_form()
                    messagebox.showinfo("Success", "User deleted successfully")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to delete user: {str(e)}")
        
        # --- Clear User Form ---
        def clear_user_form():
            global user_selected_id
            user_selected_id = None
            user_name_var.set("")
            user_pass_var.set("")
            user_role_var.set("cashier")  # Default role
        
        # --- Select User ---
        def on_user_select(event):
            global user_selected_id
            
            selected = users_tree.focus()
            if not selected:
                return
                
            values = users_tree.item(selected, 'values')
            if values:
                user_selected_id = values[0]
                user_name_var.set(values[1])
                user_pass_var.set("")  # Clear password for security
                user_role_var.set(values[2])
        
        # Bind selection event
        users_tree.bind('<<TreeviewSelect>>', on_user_select)
        
        # Add buttons
        user_button_frame = ctk.CTkFrame(user_controls, fg_color="transparent")
        user_button_frame.pack(pady=20)
        
        ctk.CTkButton(user_button_frame, text="Add", command=add_user, width=80).pack(side="left", padx=5)
        ctk.CTkButton(user_button_frame, text="Update", command=update_user, width=80).pack(side="left", padx=5)
        ctk.CTkButton(user_button_frame, text="Delete", command=delete_user, fg_color="red", width=80).pack(side="left", padx=5)
        
        ctk.CTkButton(user_controls, text="Clear Form", command=clear_user_form, width=180).pack(pady=10)
        ctk.CTkButton(user_controls, text="Refresh", command=load_users, width=180).pack(pady=10)
        
        # Initialize users table
        load_users()
    else:
        # For non-admin users, display access denied message
        ctk.CTkLabel(tab_users, text="Access Denied", 
                   font=ctk.CTkFont(size=24, weight="bold")).pack(pady=20)
        ctk.CTkLabel(tab_users, text="You need administrator privileges to manage users.",
                   font=ctk.CTkFont(size=16)).pack(pady=10)
    
    # --- Footer with action buttons ---
    footer = ctk.CTkFrame(app)
    footer.pack(fill="x", padx=10, pady=10)
    
    ctk.CTkButton(footer, text="Switch to POS", command=lambda: [app.destroy(), 
                                                             open_pos(username, role)]).pack(side="left", padx=10)
    ctk.CTkButton(footer, text="Logout", fg_color="red", 
                command=app.destroy).pack(side="right", padx=10)
    
    # Initialize product list
    load_products()
    load_sales()
    
    app.mainloop()

# Helper function to open POS/Dashboard
def open_pos(username, role):
    from src.dashboard import open_dashboard
    open_dashboard(username, role)