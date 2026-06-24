import sqlite3
import hashlib

def make_hashes(password):
    """Encrypts the password before saving it to the database"""
    return hashlib.sha256(str.encode(password)).hexdigest()

def create_usertable():
    """Creates the user database if it doesn't already exist"""
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS userstable(username TEXT UNIQUE, password TEXT)')
    conn.commit()
    conn.close()

def add_user(username, password):
    """Adds a new user to the database. Returns False if username exists."""
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    try:
        c.execute('INSERT INTO userstable(username, password) VALUES (?,?)', (username, password))
        conn.commit()
        success = True
    except sqlite3.IntegrityError:
        # This triggers if the username already exists due to the UNIQUE constraint
        success = False 
    conn.close()
    return success

def login_user(username, password):
    """Checks if the username and hashed password match the database"""
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('SELECT * FROM userstable WHERE username =? AND password = ?', (username, password))
    data = c.fetchall()
    conn.close()
    return data