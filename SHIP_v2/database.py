import sqlite3
from pathlib import Path

import bcrypt

DB_PATH = Path(__file__).parent / "loans.db"


def create_users():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL 
         )
     ''')

    cursor.execute("SELECT * FROM users")
    if not cursor.fetchall():
        try:
            username = "admin"
            password = "admin123"
            role = "admin"
            hashed_pass = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

            cursor.execute("INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                           (username, hashed_pass, role))
            print("Default user admin with password **** created successfully")
        except sqlite3.IntegrityError:
            print("Default user admin already exists")

    conn.commit()
    conn.close()


def create_table():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS loans (
        customer_id TEXT,
        bank_name TEXT, 
        branch_code TEXT,
        branch_name TEXT,
        client_type TEXT,
        business_size TEXT,
        annual_turnover REAL,
        balance_sheet_size REAL,
        loan_number TEXT,
        disbursement_date TEXT,
        maturity_date TEXT,
        currency TEXT,
        tzs_disbursed_amount REAL,
        tzs_outstanding_principal REAL,
        frequency_of_repayment TEXT,
        interest_rate_type TEXT,
        loan_authorization_type TEXT,
        annual_interest_rate REAL,
        loan_type TEXT,
        loan_economic_activity TEXT,
        loan_purpose TEXT,
        asset_classification TEXT,
        loan_region TEXT,
        loan_district TEXT,
        loan_ward TEXT,
        loan_street TEXT,
        loan_latitude REAL,
        loan_longitude REAL,
        collateral_pledged TEXT,
        collateral_pledged_date TEXT,
        collateral_market_value REAL,
        collateral_forced_sale_value REAL,
        collateral_economic_activity TEXT,
        collateral_region TEXT,
        collateral_district TEXT,
        collateral_ward TEXT,
        collateral_street TEXT,
        collateral_latitude REAL,
        collateral_longitude REAL,
        climate_risk_insurance TEXT,
        insurance_type TEXT,
        insurance_provider TEXT,
        collateral_protected_value REAL
        )
    ''')
    conn.commit()
    conn.close()


if __name__ == '__main__':
    create_users()
    create_table()
    print(f"Database setup complete. located at: {DB_PATH}")