"""
Debug Password Issue
Check what's stored in database vs what you're entering
"""

import sqlite3
import hashlib

def make_hashes(password: str) -> str:
    return hashlib.sha256(str.encode(password)).hexdigest()

print("=" * 80)
print("🔍 PASSWORD DEBUG SCRIPT")
print("=" * 80)

# Check if database exists
import os
if not os.path.exists('users.db'):
    print("❌ users.db does NOT exist!")
    print("💡 Create an account first, then run this script again")
    exit()

print("✅ users.db found\n")

# Check database contents
conn = sqlite3.connect('users.db')
c = conn.cursor()

# Get all users
c.execute('SELECT username, password FROM userstable')
users = c.fetchall()

if not users:
    print("❌ NO USERS IN DATABASE!")
    print("💡 Create an account first")
    conn.close()
    exit()

print(f"📋 USERS IN DATABASE: {len(users)} user(s)\n")

for username, stored_hash in users:
    print(f"Username: {username}")
    print(f"Stored hash: {stored_hash}")
    print(f"Hash length: {len(stored_hash)}")
    
    # Test with different passwords
    test_passwords = [
        "demo123",      # Demo password
        "demo123456",   # 6 chars version
        "test123456",   # Test password
        "demo",         # Short version
    ]
    
    print("\n🧪 Testing passwords:")
    for test_pwd in test_passwords:
        test_hash = make_hashes(test_pwd)
        matches = test_hash == stored_hash
        status = "✅ MATCH!" if matches else "❌ No match"
        print(f"  '{test_pwd}' → {status}")
    
    print("\n" + "-" * 80 + "\n")

conn.close()

print("=" * 80)
print("💡 WHAT THIS MEANS:")
print("=" * 80)
print("""
If you see ❌ No match for the password you entered:
1. The password you're using is DIFFERENT from what was registered
2. Or the signup didn't save correctly

NEXT STEP: Delete users.db and create account again
  rm users.db
  streamlit run streamlit_app.py
  Create new account
  Test login
""")