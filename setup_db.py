import sqlite3

def init_db():
    conn = sqlite3.connect("disaster_alert.db")
    cursor = conn.cursor()
    
    # 1. Setup Recipients (Users)
    cursor.execute("DROP TABLE IF EXISTS users")
    cursor.execute("CREATE TABLE users (region TEXT, phone TEXT)")
    
    # +917428349990 is valid, 9191 is invalid
    users = [
        ("Delhi", "+917428349990"), # Valid
        ("Delhi", "9191"),          # Invalid (Failure Test)
        ("Mumbai", "+917428349990"), # Valid
        ("Kolkata", "9191"),         # Invalid (Failure Test)
        ("Chennai", "+917428349990"), # Valid
        ("Bangalore", "9191")        # Invalid (Failure Test)
    ]
    cursor.executemany("INSERT INTO users (region, phone) VALUES (?, ?)", users)
    
    # 2. Setup Admins (For Login Success/Failure metrics)
    cursor.execute("DROP TABLE IF EXISTS admins")
    cursor.execute("CREATE TABLE admins (username TEXT PRIMARY KEY, password TEXT)")
    cursor.execute("INSERT INTO admins (username, password) VALUES (?, ?)", ("admin", "password123"))
    
    conn.commit()
    conn.close()
    print("[INIT] Database initialized with diverse test data.")

if __name__ == "__main__":
    init_db()