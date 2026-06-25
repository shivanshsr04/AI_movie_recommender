"""
Authentication Module using SQLite
Handles user registration, login, and password hashing
"""

import sqlite3
import hashlib
from typing import Tuple

def make_hashes(password: str) -> str:
    """
    Hash password using SHA-256
    
    Args:
        password: Plain text password
        
    Returns:
        Hashed password string
    """
    return hashlib.sha256(str.encode(password)).hexdigest()

def create_usertable():
    """Creates the user database table if it doesn't already exist"""
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
    print("✓ User table created/verified")

def add_user(username: str, password: str, email: str = None) -> Tuple[bool, str]:
    """
    Add a new user to the database
    
    Args:
        username: User's username (must be unique)
        password: User's password (will be hashed)
        email: User's email (optional)
        
    Returns:
        Tuple of (success: bool, message: str)
    """
    if not username or not password:
        return False, "❌ Username and password are required!"
    
    if len(username) < 3:
        return False, "❌ Username must be at least 3 characters!"
    
    if len(password) < 6:
        return False, "❌ Password must be at least 6 characters!"
    
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    
    try:
        hashed_pwd = make_hashes(password)
        c.execute(
            'INSERT INTO userstable(username, password, email) VALUES (?,?,?)',
            (username, hashed_pwd, email)
        )
        conn.commit()
        conn.close()
        return True, f"✅ Account '{username}' created successfully!"
    
    except sqlite3.IntegrityError as e:
        conn.close()
        if 'username' in str(e):
            return False, f"❌ Username '{username}' already exists!"
        elif 'email' in str(e):
            return False, f"❌ Email '{email}' is already registered!"
        else:
            return False, f"❌ Error: {str(e)}"
    
    except Exception as e:
        conn.close()
        return False, f"❌ Error creating account: {str(e)}"

def login_user(username: str, password: str) -> Tuple[bool, str]:
    """
    Login user by verifying username and password
    
    Args:
        username: User's username
        password: User's password (plain text, will be hashed)
        
    Returns:
        Tuple of (success: bool, message: str)
    """
    if not username or not password:
        return False, "❌ Please enter both username and password!"
    
    try:
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        
        hashed_pwd = make_hashes(password)
        c.execute(
            'SELECT * FROM userstable WHERE username =? AND password = ?',
            (username, hashed_pwd)
        )
        data = c.fetchone()
        conn.close()
        
        if data:
            return True, f"✅ Welcome back, {username}!"
        else:
            return False, "❌ Username or password is incorrect!"
    
    except Exception as e:
        return False, f"❌ Login error: {str(e)}"

def user_exists(username: str) -> bool:
    """
    Check if a user exists in the database
    
    Args:
        username: Username to check
        
    Returns:
        True if user exists, False otherwise
    """
    try:
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute('SELECT * FROM userstable WHERE username = ?', (username,))
        data = c.fetchone()
        conn.close()
        return data is not None
    except:
        return False

def get_user_info(username: str) -> dict:
    """
    Get user information from database
    
    Args:
        username: Username
        
    Returns:
        Dictionary with user info or empty dict if not found
    """
    try:
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute('SELECT username, email, created_at FROM userstable WHERE username = ?', (username,))
        data = c.fetchone()
        conn.close()
        
        if data:
            return {
                'username': data[0],
                'email': data[1],
                'created_at': data[2]
            }
        return {}
    except:
        return {}

def delete_user(username: str, password: str) -> Tuple[bool, str]:
    """
    Delete a user account (requires password verification)
    
    Args:
        username: Username to delete
        password: User's password (for verification)
        
    Returns:
        Tuple of (success: bool, message: str)
    """
    try:
        # First verify password
        is_valid, _ = login_user(username, password)
        if not is_valid:
            return False, "❌ Invalid password! Cannot delete account."
        
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute('DELETE FROM userstable WHERE username = ?', (username,))
        conn.commit()
        conn.close()
        
        return True, f"✅ Account '{username}' has been deleted."
    
    except Exception as e:
        return False, f"❌ Error deleting account: {str(e)}"

def change_password(username: str, old_password: str, new_password: str) -> Tuple[bool, str]:
    """
    Change user password
    
    Args:
        username: Username
        old_password: Current password (for verification)
        new_password: New password
        
    Returns:
        Tuple of (success: bool, message: str)
    """
    # Verify old password
    is_valid, _ = login_user(username, old_password)
    if not is_valid:
        return False, "❌ Current password is incorrect!"
    
    if len(new_password) < 6:
        return False, "❌ New password must be at least 6 characters!"
    
    try:
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        
        hashed_new_pwd = make_hashes(new_password)
        c.execute(
            'UPDATE userstable SET password = ? WHERE username = ?',
            (hashed_new_pwd, username)
        )
        conn.commit()
        conn.close()
        
        return True, "✅ Password changed successfully!"
    
    except Exception as e:
        return False, f"❌ Error changing password: {str(e)}"

def get_all_users() -> list:
    """
    Get list of all users (for admin purposes)
    
    Returns:
        List of usernames
    """
    try:
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute('SELECT username FROM userstable')
        users = [row[0] for row in c.fetchall()]
        conn.close()
        return users
    except:
        return []