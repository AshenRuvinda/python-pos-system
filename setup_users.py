import sqlite3
import os

def setup_database():
    """
    Creates the database directory if it doesn't exist and sets up the required tables
    with admin, manager, and 2 cashier users along with sample products.
    """
    # Create database directory if it doesn't exist
    if not os.path.exists("database"):
        os.makedirs("database")
    
    # Connect to the database (creates it if it doesn't exist)
    conn = sqlite3.connect("database/pos.db")
    cursor = conn.cursor()
    
    # Create users table if it doesn't exist
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL
    )
    ''')
    
    # Create products table if it doesn't exist
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        category TEXT,
        price REAL NOT NULL DEFAULT 0,
        quantity INTEGER NOT NULL DEFAULT 0
    )
    ''')
    
    # Clear existing users (to ensure we have exactly what's requested)
    cursor.execute("DELETE FROM users")
    
    # Add requested users: admin, manager, and 2 cashiers
    requested_users = [
        ("admin", "admin123", "admin"),
        ("manager", "manager123", "manager"),
        ("cashier1", "cash123", "cashier"),
        ("cashier2", "cash456", "cashier")
    ]
    
    cursor.executemany(
        "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
        requested_users
    )
    print(f"Added {len(requested_users)} users as requested")
    
    # Check if products already exist
    cursor.execute("SELECT COUNT(*) FROM products")
    product_count = cursor.fetchone()[0]
    
    # Add sample products if none exist
    if product_count == 0:
        sample_products = [
            ("Smartphone XYZ", "Electronics", 499.99, 25),
            ("Laptop Pro", "Electronics", 1299.99, 10),
            ("Coffee Maker", "Appliances", 79.99, 15),
            ("Desk Chair", "Furniture", 149.99, 8),
            ("Headphones", "Electronics", 59.99, 30),
            ("Blender", "Appliances", 39.99, 12),
            ("Notebook", "Stationery", 4.99, 100),
            ("Water Bottle", "Kitchen", 12.99, 50),
            ("Backpack", "Accessories", 34.99, 20),
            ("Desk Lamp", "Furniture", 24.99, 18)
        ]
        
        cursor.executemany(
            "INSERT INTO products (name, category, price, quantity) VALUES (?, ?, ?, ?)",
            sample_products
        )
        print(f"Added {len(sample_products)} sample products")
    else:
        print(f"Database already has {product_count} products")
    
    # Commit changes and close connection
    conn.commit()
    conn.close()
    
    print("Database setup complete!")
    print("\nUser Accounts:")
    print("--------------------")
    print("Admin User:")
    print("  Username: admin")
    print("  Password: admin123")
    print("\nManager User:")
    print("  Username: manager")
    print("  Password: manager123")
    print("\nCashier Users:")
    print("  Username: cashier1")
    print("  Password: cash123")
    print("  Username: cashier2")
    print("  Password: cash456")
    print("--------------------")
    
if __name__ == "__main__":
    setup_database()