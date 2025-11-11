import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'catstore.db')

def init_db():
    """Initialize the database and create tables if they don't exist."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Create users table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            mobile TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            reset_token TEXT,
            reset_token_expiry TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

    # Create contacts table
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT,
            message TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def add_user(full_name, email, mobile, password):
    """Add a new user to the database."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        password_hash = generate_password_hash(password)
        c.execute('''
            INSERT INTO users (full_name, email, mobile, password_hash)
            VALUES (?, ?, ?, ?)
        ''', (full_name, email, mobile, password_hash))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def get_user_by_email(email):
    """Retrieve user by email."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE email = ?', (email,))
    user = c.fetchone()
    conn.close()
    return user

def verify_password(stored_password_hash, provided_password):
    """Verify a stored password hash against a provided password."""
    return check_password_hash(stored_password_hash, provided_password)

def set_reset_token(email, token, expiry):
    """Set password reset token and expiry for a user."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        UPDATE users 
        SET reset_token = ?, reset_token_expiry = ? 
        WHERE email = ?
    ''', (token, expiry, email))
    conn.commit()
    conn.close()

def verify_reset_token(token):
    """Verify a password reset token and return user email if valid."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        SELECT email FROM users 
        WHERE reset_token = ? AND reset_token_expiry > datetime('now')
    ''', (token,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else None

def update_password(email, new_password):
    """Update user's password."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    password_hash = generate_password_hash(new_password)
    c.execute('''
        UPDATE users 
        SET password_hash = ?, reset_token = NULL, reset_token_expiry = NULL 
        WHERE email = ?
    ''', (password_hash, email))
    conn.commit()
    conn.close()

def get_all_users():
    """Retrieve all registered users."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT id, full_name, email, mobile, created_at FROM users ORDER BY created_at DESC')
    users = c.fetchall()
    conn.close()
    return users

def add_contact(full_name, email, phone, message):
    """Store a contact form submission."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        c.execute('''
            INSERT INTO contacts (full_name, email, phone, message)
            VALUES (?, ?, ?, ?)
        ''', (full_name, email, phone, message))
        conn.commit()
        return True
    except Exception:
        return False
    finally:
        conn.close()

def get_all_contacts():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT id, full_name, email, phone, message, created_at FROM contacts ORDER BY created_at DESC')
    rows = c.fetchall()
    conn.close()
    return rows