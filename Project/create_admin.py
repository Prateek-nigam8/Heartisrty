import bcrypt
from db import get_db_connection

def create_admin_user(username="admin", email="admin@heartistry.com", password="admin123"):
    """Create an admin user in the database"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Check if admin user already exists
    cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
    existing_admin = cursor.fetchone()
    
    if existing_admin:
        print(f"Admin user '{username}' already exists.")
        return False
    
    # Hash password
    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    
    # Insert admin user
    cursor.execute(
        "INSERT INTO users (username, email, password, is_admin) VALUES (%s, %s, %s, %s)",
        (username, email, hashed_password.decode(), 1)
    )
    conn.commit()
    
    cursor.close()
    conn.close()
    
    print(f"Admin user '{username}' created successfully!")
    print(f"Email: {email}")
    print(f"Password: {password}")
    print("Please change these credentials after first login.")
    
    return True

if __name__ == "__main__":
    create_admin_user()