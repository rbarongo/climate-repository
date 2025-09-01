import pandas as pd
from sqlalchemy import create_engine, text
import os
# from platformshconfig import Config


# todo use env vars
DB_CONFIG = {
    'user': 'cc_admin',
    'password': 'cc_admin',
    'host': 'localhost',
    'port': '5432',
    'database': 'loans_db'
}
#
DATABASE_URL = f"postgresql+psycopg2://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
# config = Config()
# db_credentials = config.credentials('database')
# DATABASE_URL = f"postgresql+psycopg2://{db_credentials['username']}:{db_credentials['password']}@{db_credentials['host']}:{db_credentials['port']}/{db_credentials['path']}"
engine = create_engine(DATABASE_URL)


def init_db():
    table_creation_queries = [
        """
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
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL 
         );
        """,
    ]

    try:
        with engine.connect() as connection:
            for query in table_creation_queries:
                connection.execute(text(query))
            connection.commit()
            print("Database initialized successfully.")
    except Exception as e:
        print(f"An error occurred during database initialization: {e}")


# --- Loan Functions ---
def add_loan_data(df: pd.DataFrame):
    df.to_sql('loans', engine, if_exists='append', index=False)


def get_loans():
    return pd.read_sql('SELECT * FROM loans', engine)


# --- User Functions ---
def add_user(username, password_hash, role):
    query = text("INSERT INTO users (username, password_hash, role) VALUES (:username, :password_hash, :role)")
    with engine.connect() as connection:
        connection.execute(query, {"username": username, "password_hash": password_hash, "role": role})
        connection.commit()


def get_user(username):
    query = text("SELECT * FROM users WHERE username = :username")
    with engine.connect() as connection:
        result = connection.execute(query, {"username": username}).fetchone()
        return result


def get_all_users_from_db():
    return pd.read_sql("SELECT username, role FROM users", engine)


def delete_user(username):
    query = text("DELETE FROM users WHERE username = :username")
    with engine.connect() as connection:
        connection.execute(query, {"username": username})
        connection.commit()
        return True