import sqlite3
import hashlib
from typing import Tuple

DATABASE_FILE = 'users.db'

def make_hashes(password: str) -> str:
    return hashlib.sha256(str.encode(password)).hexdigest()

def create_usertable():
    try:
        conn = sqlite3.connect(DATABASE_FILE, timeout=10.0)
        cursor = conn.cursor()
        
        cursor.execute('''
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
    except Exception as e:
        print(f"Error: {str(e)}")

def add_user(username: str, password: str, email: str = None) -> Tuple[bool, str]:
    if not username or not password:
        return False, "❌ Username and password required!"
    
    try:
        conn = sqlite3.connect(DATABASE_FILE, timeout=10.0)
        cursor = conn.cursor()
        
        hashed_pwd = make_hashes(password)
        cursor.execute(
            'INSERT INTO userstable(username, password, email) VALUES (?,?,?)',
            (username, hashed_pwd, email)
        )
        conn.commit()
        conn.close()
        
        return True, f"✅ Account created successfully!"
    
    except sqlite3.IntegrityError:
        return False, "❌ Username already exists!"
    except Exception as e:
        return False, f"❌ Error: {str(e)}"

def login_user(username: str, password: str) -> Tuple[bool, str]:
    if not username or not password:
        return False, "❌ Please enter username and password!"
    
    try:
        conn = sqlite3.connect(DATABASE_FILE, timeout=10.0)
        cursor = conn.cursor()
        
        hashed_pwd = make_hashes(password)
        cursor.execute(
            'SELECT username, password FROM userstable WHERE username = ?',
            (username,)
        )
        result = cursor.fetchone()
        conn.close()
        
        if result is None:
            return False, "❌ Username not found!"
        
        stored_username, stored_hash = result
        
        if hashed_pwd == stored_hash:
            return True, f"✅ Welcome back, {username}!"
        else:
            return False, "❌ Username or password is incorrect!"
    
    except Exception as e:
        return False, f"❌ Error: {str(e)}"

def user_exists(username: str) -> bool:
    try:
        conn = sqlite3.connect(DATABASE_FILE, timeout=5.0)
        cursor = conn.cursor()
        cursor.execute('SELECT 1 FROM userstable WHERE username = ? LIMIT 1', (username,))
        result = cursor.fetchone()
        conn.close()
        return result is not None
    except:
        return False

def get_user_info(username: str) -> dict:
    try:
        conn = sqlite3.connect(DATABASE_FILE, timeout=5.0)
        cursor = conn.cursor()
        cursor.execute('SELECT username, email, created_at FROM userstable WHERE username = ?', (username,))
        data = cursor.fetchone()
        conn.close()
        
        if data:
            return {
                'username': data[0],
                'email': data[1],
                'created_at': str(data[2]) if data[2] else 'N/A'
            }
        return {}
    except:
        return {}

def show_all_users():
    try:
        conn = sqlite3.connect(DATABASE_FILE, timeout=5.0)
        cursor = conn.cursor()
        cursor.execute('SELECT username, password, email, created_at FROM userstable')
        users = cursor.fetchall()
        conn.close()
        
        print("\n" + "="*80)
        print("📋 ALL USERS IN DATABASE:")
        print("="*80)
        if users:
            for username, pwd, email, created in users:
                print(f"Username: {username}")
                print(f"  Email: {email}")
                print(f"  Password Hash: {pwd[:20]}...")
                print(f"  Created: {created}")
                print()
        else:
            print("❌ NO USERS IN DATABASE")
        print("="*80 + "\n")
        
        return users
    except Exception as e:
        print(f"Error: {str(e)}")
        return []
def verify_database() -> bool:
    """Checks if the userstable exists in the database."""
    try:
        conn = sqlite3.connect(DATABASE_FILE, timeout=5.0)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='userstable';")
        exists = cursor.fetchone() is not None
        conn.close()
        return exists
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        return False

create_usertable()