# create_admin.py

import bcrypt
import getpass
from sqlalchemy import exc

from db_postgres import add_user, init_db


def create_initial_admin():

    print("--- Create Initial Admin User ---")

    try:
        print("Initializing database to ensure tables exist...")
        init_db()
    except Exception as e:
        print(f"Database initialization check failed: {e}")
        return

    username = input("Enter admin username: ")
    password = getpass.getpass("Enter admin password: ")

    if not username or not password:
        print("Username and password cannot be empty.")
        return
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    try:
        add_user(username, hashed_password, 'admin')
        print(f"\n✅ Success! Admin user '{username}' created.")
    except exc.IntegrityError:
        print(f"\n❌ Error: User '{username}' already exists.")
    except Exception as e:
        print(f"\n❌ An unexpected error occurred: {e}")


if __name__ == "__main__":
    create_initial_admin()