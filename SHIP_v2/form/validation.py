import os
import sys

root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_dir)

import pandas as pd
from configs.vars import COLUMNS, BANK_NAMES


def validate_dataframe(df):

    errors = []
    # required_columns = ['LoanID', 'ClientID', 'LoanAmount', 'InterestRate', 'LoanStatus', 'StartDate']

    missing_cols = [col for col in COLUMNS if col not in df.columns]
    if missing_cols:
        errors.append(f"Missing required columns: {', '.join(missing_cols)}")
        return errors  

    for index, row in df.iterrows():
        try:
            # Rule: Must be registered bank name
            if row['Bank Name'] not in BANK_NAMES:
                errors.append({"Row": index, "Field": "Bank Name", "Value": row['Bank Name'],
                               "Reason": "Unrecognized bank name"})
            # Rule: Maturity date must be greater than disbursement date
            if not pd.to_datetime(row['Maturity Date']) >= pd.to_datetime(row['Disbursement Date']):
                errors.append({"Row": index, "Field": "Maturity Date", "Value": row['Maturity Date'],
                               "Reason": "Maturity date of the loan must be greater than it's disbursement date"})
            # Rule: TZS Disbursed Amount must be a positive number
            if not pd.to_numeric(row['TZS Disbursed Amount'], errors='coerce') > 0:
                errors.append(
                    {"Row": index, "Field": "TZS Disbursed Amount", "Value": row['TZS Disbursed Amount'],
                     "Reason": "Must be a positive number."})

            # Rule: Annual Interest Rate must be between 0 and 100
            rate = pd.to_numeric(row['Annual Interest Rate'], errors='coerce')
            if not (0 <= rate <= 100):
                errors.append({"Row": index, "Field": "Annual Interest Rate", "Value": row['Annual Interest Rate'],
                               "Reason": "Must be between 0 and 100."})
            
            # Rule: Location information should not be null
            if pd.isnull(row['Collateral Region']) or pd.isnull(row['Collateral District']) or pd.isnull(row['Collateral Ward']) or pd.isnull(row['Collateral Street']):
                errors.append({"Row": index, "Field": "Location of collateral", 
                               "Value": f"Region: {row['Collateral Region']}, District: {row['Collateral District']}, Ward: {row['Collateral Ward']}, Street: {row['Collateral Street']}",
                               "Reason": "Location information should not be null."})

        except (ValueError, TypeError) as e:
            errors.append({"Row": index, "Field": "StartDate", "Value": row['StartDate'],
                           "Reason": f"Invalid date format or value. Error: {e}"})

    return errors
