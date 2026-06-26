"""
Authentication Module - IMPROVED with Logging
Debug version to help identify issues
"""

import sqlite3
import hashlib
from typing import Tuple
import os

# Enable logging
DEBUG = True

def log(message):
    """Log debug messages"""
    if DEBUG:
        print(f"🔐 AUTH: {message}")

def make_hashes(password: str) -> str:
    """Hash password using SHA-256"""
    hashed = hashlib.sha256(str.encode(password)).hexdigest()
    log(f"Hashed password: {password[:3]}... → {hashed[:10]}...")
    return hashed

def create_usertable():
    """Create user database table"""
    try:
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS userstable(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                email TEXT UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()
        log("User table created/verified ✅")
    except Exception as e:
        log(f"Error creating table: {str(e)}")

def add_user(username: str, password: str, email: str = None) -> Tuple[bool, str]:
    """Add a new user to the database"""
    log(f"Attempting to add user: {username}")
    
    if not username or not password:
        log("❌ Missing username or password")
        return False, "❌ Username and password are required!"
    
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    
    try:
        log(f"Inserting user {username} with email {email}")
        log(f"Password being stored: {password[:10]}... (length: {len(password)})")
        
        c.execute(
            'INSERT INTO userstable(username, password, email) VALUES (?,?,?)',
            (username, password, email)
        )
        conn.commit()
        conn.close()
        
        log(f"✅ User {username} added successfully")
        return True, f"✅ Account created successfully!"
    
    except sqlite3.IntegrityError as e:
        conn.close()
        log(f"❌ IntegrityError: {str(e)}")
        if 'username' in str(e):
            return False, f"❌ Username '{username}' already exists!"
        elif 'email' in str(e):
            return False, f"❌ Email already registered!"
        else:
            return False, f"❌ {str(e)}"
    
    except Exception as e:
        conn.close()
        log(f"❌ Exception: {str(e)}")
        return False, f"❌ Error: {str(e)}"

def login_user(username: str, password: str) -> Tuple[bool, str]:
    """Login user by verifying username and password"""
    log(f"Login attempt for user: {username}")
    
    if not username or not password:
        log("❌ Missing username or password")
        return False, "❌ Please enter both username and password!"
    
    try:
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        
        # Hash the password they entered
        hashed_pwd = make_hashes(password)
        log(f"Looking for user: {username}")
        log(f"Entered password hash: {hashed_pwd[:10]}...")
        
        # Query database
        c.execute(
            'SELECT username, password FROM userstable WHERE username = ?',
            (username,)
        )
        data = c.fetchone()
        conn.close()
        
        if not data:
            log(f"❌ User {username} not found")
            return False, "❌ Username not found!"
        
        stored_username, stored_hash = data
        log(f"Found user: {stored_username}")
        log(f"Stored password hash: {stored_hash[:10]}...")
        log(f"Hashes match: {hashed_pwd == stored_hash}")
        
        if hashed_pwd == stored_hash:
            log(f"✅ Login successful for {username}")
            return True, f"✅ Welcome back, {username}!"
        else:
            log(f"❌ Password mismatch for {username}")
            log(f"  Entered: {hashed_pwd}")
            log(f"  Stored:  {stored_hash}")
            return False, "❌ Username or password is incorrect!"
    
    except Exception as e:
        log(f"❌ Login exception: {str(e)}")
        return False, f"❌ Login error: {str(e)}"

def user_exists(username: str) -> bool:
    """Check if a user exists"""
    try:
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute('SELECT * FROM userstable WHERE username = ?', (username,))
        data = c.fetchone()
        conn.close()
        exists = data is not None
        log(f"User {username} exists: {exists}")
        return exists
    except Exception as e:
        log(f"Error checking user exists: {str(e)}")
        return False

def get_user_info(username: str) -> dict:
    """Get user information"""
    try:
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute('SELECT username, email, created_at FROM userstable WHERE username = ?', (username,))
        data = c.fetchone()
        conn.close()
        
        if data:
            info = {
                'username': data[0],
                'email': data[1],
                'created_at': str(data[2]) if data[2] else 'N/A'
            }
            log(f"Got user info for {username}")
            return info
        
        log(f"No user info found for {username}")
        return {}
    except Exception as e:
        log(f"Error getting user info: {str(e)}")
        return {}

def delete_all_users():
    """DELETE ALL USERS - USE WITH CAUTION!"""
    try:
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute('DELETE FROM userstable')
        conn.commit()
        conn.close()
        log("🚨 ALL USERS DELETED")
        return True
    except Exception as e:
        log(f"Error deleting users: {str(e)}")
        return False

def show_all_users():
    """Show all users in database - DEBUG ONLY"""
    try:
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute('SELECT username, password, email FROM userstable')
        users = c.fetchall()
        conn.close()
        
        log(f"Database has {len(users)} users:")
        for username, pwd_hash, email in users:
            log(f"  - {username} | Email: {email} | Hash: {pwd_hash[:10]}...")
        
        return users
    except Exception as e:
        log(f"Error showing users: {str(e)}")
        return []

# Allow disabling debug logging
def disable_debug():
    global DEBUG
    DEBUG = False

def enable_debug():
    global DEBUG
    DEBUG = True