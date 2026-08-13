#!/usr/bin/env python3
"""Generate bcrypt hash for admin password.

Usage:
    python3 generate_admin_hash.py

This will prompt for a password and output the bcrypt hash to use in the
ADMIN_PASSWORD_HASH environment variable.
"""
import bcrypt
import getpass

def main():
    print("Generate Admin Password Hash")
    print("=" * 40)
    print()

    while True:
        password = getpass.getpass("Enter admin password (min 12 chars): ")
        if len(password) < 12:
            print("❌ Password must be at least 12 characters")
            continue

        confirm = getpass.getpass("Confirm password: ")
        if password != confirm:
            print("❌ Passwords don't match")
            continue

        break

    # Generate bcrypt hash
    salt = bcrypt.gensalt()
    password_hash = bcrypt.hashpw(password.encode(), salt).decode()

    print()
    print("✅ Password hash generated successfully!")
    print()
    print("Add this to your .env file:")
    print("=" * 40)
    print(f"ADMIN_PASSWORD_HASH={password_hash}")
    print("=" * 40)
    print()
    print("⚠️  Keep this hash secure and never commit it to version control!")

if __name__ == "__main__":
    main()
