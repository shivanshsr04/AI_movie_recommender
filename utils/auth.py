"""Optional local-account helpers; the public demo uses guest access.

Legacy SHA-256 hashes are upgraded after a successful login. Importing this
module does not create a database or print account records.
"""
import hashlib
import hmac
import secrets
import sqlite3
from pathlib import Path

DATABASE_FILE = str(Path(__file__).resolve().parents[1] / 'users.db')
ITERATIONS = 600_000


def make_hashes(password):
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac('sha256', password.encode(), bytes.fromhex(salt), ITERATIONS).hex()
    return f'pbkdf2_sha256${ITERATIONS}${salt}${digest}'


def verify_password(password, stored):
    try:
        if stored.startswith('pbkdf2_sha256$'):
            _, rounds, salt, digest = stored.split('$')
            rounds = int(rounds)
            if not 1 <= rounds <= 2_000_000:
                return False
            actual = hashlib.pbkdf2_hmac('sha256', password.encode(), bytes.fromhex(salt), rounds).hex()
            return hmac.compare_digest(actual, digest)
        if len(stored) == 64:
            return hmac.compare_digest(hashlib.sha256(password.encode()).hexdigest(), stored)
    except (ValueError, TypeError):
        pass
    return False


def create_usertable():
    with sqlite3.connect(DATABASE_FILE) as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS userstable (
            id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL, email TEXT UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')


def add_user(username, password, email=None):
    if not username or len(password) < 8:
        return False, 'A username and password of at least 8 characters are required.'
    create_usertable()
    try:
        with sqlite3.connect(DATABASE_FILE) as conn:
            conn.execute('INSERT INTO userstable(username,password,email) VALUES (?,?,?)',
                         (username.strip(), make_hashes(password), email))
        return True, 'Account created.'
    except sqlite3.IntegrityError:
        return False, 'Username or email already exists.'


def login_user(username, password):
    create_usertable()
    with sqlite3.connect(DATABASE_FILE) as conn:
        row = conn.execute('SELECT password FROM userstable WHERE username=?', (username,)).fetchone()
        if row is None or not verify_password(password, row[0]):
            return False, 'Invalid username or password.'
        if not row[0].startswith('pbkdf2_sha256$'):
            conn.execute('UPDATE userstable SET password=? WHERE username=?', (make_hashes(password), username))
    return True, 'Signed in.'


def user_exists(username):
    create_usertable()
    with sqlite3.connect(DATABASE_FILE) as conn:
        return conn.execute('SELECT 1 FROM userstable WHERE username=?', (username,)).fetchone() is not None


def get_user_info(username):
    create_usertable()
    with sqlite3.connect(DATABASE_FILE) as conn:
        row = conn.execute('SELECT username,email,created_at FROM userstable WHERE username=?', (username,)).fetchone()
    return dict(zip(['username', 'email', 'created_at'], row)) if row else {}
