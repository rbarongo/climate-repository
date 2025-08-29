from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
from datetime import datetime
import uuid
from pathlib import Path
from database import create_table

DB_PATH = Path(__file__).parent / "loans.db"

app = Flask(__name__)
CORS(app)
create_table()
print(f"Database setup complete. located at: {DB_PATH}")

def add_loan_to_db(data):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    for record in data:
        cursor.execute('''
            INSERT INTO loans (
                customer_id, bank_name, branch_code, branch_name, client_type,
                business_size, annual_turnover, balance_sheet_size, loan_number,
                disbursement_date, maturity_date, currency, tzs_disbursed_amount,
                tzs_outstanding_principal, frequency_of_repayment, interest_rate_type,
                loan_authorization_type, annual_interest_rate, loan_type,
                loan_economic_activity, loan_purpose, asset_classification,
                loan_region, loan_district, loan_ward, loan_street,
                loan_latitude, loan_longitude, collateral_pledged,
                collateral_pledged_date, collateral_market_value,
                collateral_forced_sale_value, collateral_economic_activity,
                collateral_region, collateral_district, collateral_ward,
                collateral_street, collateral_latitude, collateral_longitude,
                climate_risk_insurance, insurance_type, insurance_provider,
                collateral_protected_value
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            record.get('Customer Identification Number'),
            record.get('Bank Name'),
            record.get('Branch Code'),
            record.get('Branch name'),
            record.get('Client Type'),
            record.get('Size of the business'),
            record.get('Annual turn-over of the borrower'),
            record.get('Balance Sheet Size'),
            record.get('Loan number'),
            record.get('Disbursement Date'),
            record.get('Maturity Date'),
            record.get('Currency'),
            record.get('TZS Disbursed Amount'),
            record.get('TZS Outstanding Principal Amount'),
            record.get('Frequency of Repayment'),
            record.get('Interest Rate Type'),
            record.get('Loan Authorization Type'),
            record.get('Annual Interest Rate'),
            record.get('loan Type/ General Category'),
            record.get('Loan Economic Activity'),
            record.get('Purpose of the loan'),
            record.get('Asset Classification Category'),
            record.get('Location of invested loan (Region)'),
            record.get('Location of invested loan (District)'),
            record.get('Location of invested loan (Ward)'),
            record.get('Location of invested loan (Street)'),
            record.get('Invested Loan Geographical coordinates-Latitude'),
            record.get('Invested Loan Geographical coordinates-Longitude'),
            record.get('Collateral Pledged'),
            record.get('Collateral Pledged Date'),
            record.get('TZS Market value of the collateral'),
            record.get('TZS Forced Sale Value of the collateral'),
            record.get('Collateral Economic activity '),
            record.get('Collateral Region'),
            record.get('Collateral District'),
            record.get('Collateral Ward'),
            record.get('Collateral Street'),
            record.get('Collateral Geographical Coordinates-Latitude'),
            record.get('Collateral Geographical Coordinates-Longitude'),
            record.get('Insurance coverage of the collateral against climate risks '),
            record.get('Type of insurance policy'),
            record.get('Name of insurance provider'),
            record.get('Value of Collateral Protected'),

        ))
    conn.commit()
    conn.close()


@app.route('/submit_loan', methods=['POST'])
def submit_loan():
    data = request.json
    try:
        add_loan_to_db(data)
        return jsonify({"status": "success", "message": "Loan data submitted successfully."}), 201
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)