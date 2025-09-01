from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
from db_postgres import add_loan_data, init_db

app = Flask(__name__)
CORS(app)

try:
    init_db()
    print("PostgreSQL database setup complete.")
except Exception as e:
    print(f"Error during database initialization: {e}")


@app.route('/submit_loan', methods=['POST'])
def submit_loan():
    json_data = request.json
    if not json_data:
        return jsonify({"status": "error", "message": "No data received."}), 400

    try:
        df = pd.DataFrame(json_data)
        column_mapping = {
            'Customer Identification Number': 'customer_id',
            'Bank Name': 'bank_name',
            'Branch Code': 'branch_code',
            'Branch name': 'branch_name',
            'Client Type': 'client_type',
            'Size of the business': 'business_size',
            'Annual turn-over of the borrower': 'annual_turnover',
            'Balance Sheet Size': 'balance_sheet_size',
            'Loan number': 'loan_number',
            'Disbursement Date': 'disbursement_date',
            'Maturity Date': 'maturity_date',
            'Currency': 'currency',
            'TZS Disbursed Amount': 'tzs_disbursed_amount',
            'TZS Outstanding Principal Amount': 'tzs_outstanding_principal',
            'Frequency of Repayment': 'frequency_of_repayment',
            'Interest Rate Type': 'interest_rate_type',
            'Loan Authorization Type': 'loan_authorization_type',
            'Annual Interest Rate': 'annual_interest_rate',
            'loan Type/ General Category': 'loan_type',
            'Loan Economic Activity': 'loan_economic_activity',
            'Purpose of the loan': 'loan_purpose',
            'Asset Classification Category': 'asset_classification',
            'Location of invested loan (Region)': 'loan_region',
            'Location of invested loan (District)': 'loan_district',
            'Location of invested loan (Ward)': 'loan_ward',
            'Location of invested loan (Street)': 'loan_street',
            'Invested Loan Geographical coordinates-Latitude': 'loan_latitude',
            'Invested Loan Geographical coordinates-Longitude': 'loan_longitude',
            'Collateral Pledged': 'collateral_pledged',
            'Collateral Pledged Date': 'collateral_pledged_date',
            'TZS Market value of the collateral': 'collateral_market_value',
            'TZS Forced Sale Value of the collateral': 'collateral_forced_sale_value',
            'Collateral Economic activity ': 'collateral_economic_activity',
            'Collateral Region': 'collateral_region',
            'Collateral District': 'collateral_district',
            'Collateral Ward': 'collateral_ward',
            'Collateral Street': 'collateral_street',
            'Collateral Geographical Coordinates-Latitude': 'collateral_latitude',
            'Collateral Geographical Coordinates-Longitude': 'collateral_longitude',
            'Insurance coverage of the collateral against climate risks ': 'climate_risk_insurance',
            'Type of insurance policy': 'insurance_type',
            'Name of insurance provider': 'insurance_provider',
            'Value of Collateral Protected': 'collateral_protected_value'
        }
        df.rename(columns=column_mapping, inplace=True)
        add_loan_data(df)

        return jsonify({"status": "success", "message": "Loan data submitted successfully."}), 201

    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)