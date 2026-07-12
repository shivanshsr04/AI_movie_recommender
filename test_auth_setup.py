"""
SETUP & TEST SCRIPT
Run this FIRST to ensure everything works
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

from utils.auth import (
    create_usertable, add_user, login_user, 
    user_exists, show_all_users, verify_database
)

def print_section(title):
    """Print formatted section"""
    print("\n" + "="*80)
    print(f"🔧 {title}")
    print("="*80 + "\n")

def main():
    """Main setup script"""
    
    print_section("AUTHENTICATION SYSTEM SETUP & TEST")
    
    # Step 1: Verify database
    print("1️⃣  Verifying database...")
    verify_database()
    print("✅ Database verified\n")
    
    # Step 2: Show current users
    print("2️⃣  Checking existing users...")
    existing_users = show_all_users()
    
    # Step 3: Delete test users if they exist
    if existing_users:
        response = input("\n⚠️  Delete all existing users to start fresh? (yes/no): ")
        if response.lower() == 'yes':
            print("🗑️  Deleting database and recreating...")
            if os.path.exists('users.db'):
                os.remove('users.db')
            create_usertable()
            print("✅ Database reset\n")
    
    # Step 4: Create test account
    print_section("STEP 3: CREATE TEST ACCOUNT")
    
    test_username = "testuser"
    test_password = "test123456"
    test_email = "test@example.com"
    
    print(f"Creating test account:")
    print(f"  Username: {test_username}")
    print(f"  Password: {test_password}")
    print(f"  Email: {test_email}\n")
    
    success, message = add_user(test_username, test_password, test_email)
    print(f"Result: {message}")
    
    if not success:
        print("❌ Failed to create account. Stopping.")
        return False
    
    # Step 5: Verify user was saved
    print("\n5️⃣  Verifying user was saved to database...")
    if user_exists(test_username):
        print(f"✅ User '{test_username}' found in database")
    else:
        print(f"❌ User '{test_username}' NOT found in database")
        print("This is the problem! Signup is not saving to database.")
        return False
    
    # Step 6: Test login with correct password
    print_section("STEP 6: TEST LOGIN WITH CORRECT PASSWORD")
    
    print(f"Attempting login:")
    print(f"  Username: {test_username}")
    print(f"  Password: {test_password}\n")
    
    success, message = login_user(test_username, test_password)
    print(f"Result: {message}")
    
    if not success:
        print("❌ Login failed with correct password!")
        print("This means password hashing is broken.")
        return False
    
    print("✅ Login successful with correct password")
    
    # Step 7: Test login with wrong password
    print_section("STEP 7: TEST LOGIN WITH WRONG PASSWORD")
    
    print(f"Attempting login with wrong password:")
    print(f"  Username: {test_username}")
    print(f"  Password: wrongpassword\n")
    
    success, message = login_user(test_username, "wrongpassword")
    print(f"Result: {message}")
    
    if success:
        print("❌ Login succeeded with wrong password! Authentication is broken.")
        return False
    
    print("✅ Login correctly rejected wrong password")
    
    # Step 8: Show all users
    print_section("STEP 8: FINAL DATABASE STATE")
    show_all_users()
    
    # Step 9: Success!
    print_section("✅ ALL TESTS PASSED!")
    print("""
Your authentication system is working correctly!

Next steps:
1. Replace utils/auth.py with auth_PERMANENT_FIX.py
2. Use streamlit_app_FINAL.py
3. Run: streamlit run streamlit_app.py

The system should now work perfectly.
    """)
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)