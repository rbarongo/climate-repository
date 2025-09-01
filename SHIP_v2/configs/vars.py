SERVER_URL = "http://127.0.0.1:5001/submit_loan"

TANZANIA_REGIONS = [
    "Arusha", "Dar es Salaam", "Dodoma", "Geita", "Iringa", "Kagera",
    "Katavi", "Kigoma", "Kilimanjaro", "Lindi", "Manyara", "Mara",
    "Mbeya", "Mjini Magharibi (Zanzibar Urban West)", "Morogoro",
    "Mtwara", "Mwanza", "Njombe", "Pemba North", "Pemba South",
    "Pwani", "Rukwa", "Ruvuma", "Shinyanga", "Simiyu", "Singida",
    "Songwe", "Tabora", "Tanga", "Unguja North (Zanzibar North)",
    "Unguja South (Zanzibar South)"
]

COLUMNS = [
    'Customer Identification Number', 'Bank Name', 'Branch Code', 'Branch name',
    'Client Type', 'Size of the business', 'Annual turn-over of the borrower',
    'Balance sheet size of the borrower', 'Loan number', 'Disbursement Date',
    'Maturity Date', 'Currency', 'TZS Disbursed Amount', 'TZS Outstanding Principal Amount',
    'Frequency of repayment', 'Interest Rate Type', 'Annual Interest Rate',
    'Loan authorization type', 'loan Type/ General Category', 'Loan Economic Activity',
    'Purpose of the loan', 'Asset Classification Category',
    'Location of invested loan (Region)', 'Location of invested loan (District)',
    'Location of invested loan (Ward)', 'Location of invested loan (Street)',
    'Invested Loan Geographical coordinates-Latitude',
    'Invested Loan Geographical coordinates-Longitude',
    'Collateral Pledged', 'Collateral Pledged Date',
    'TZS Market value of the collateral', 'TZS Forced Sale Value of the collateral',
    'Collateral Economic activity ', 'Collateral Region', 'Collateral District',
    'Collateral Ward', 'Collateral Street',
    'Collateral Geographical Coordinates-Latitude',
    'Collateral Geographical Coordinates-Longitude',
    'Insurance coverage of the collateral against climate risks ',
    'Type of insurance policy', 'Name of insurance provider',
    'Value of Collateral Protected'
]

BANK_NAMES = [
    "Absa Bank", "Access Bank", "Akiba Commercial Bank", "Amana Bank", "Azania Bank",
    "Bank of Africa", "Bank of Baroda", "Bank of India", "China Dasheng Bank", "Citibank",
    "CRDB Bank", "DCB Commercial Bank", "Diamond Trust Bank", "Ecobank", "Equity Bank",
    "Exim Bank", "Guaranty Trust Bank", "Habib African Bank", "I&M Bank",
    "International Commercial Bank", "KCB Bank", "Letshego Faidika Bank", "Maendeleo Bank",
    "Mkombozi Commercial Bank", "Mwalimu Commercial Bank", "Mwanga Hakika Bank",
    "National Bank of Commerce", "NCBA Bank", "National Microfinance Bank (NMB)",
    "People’s Bank of Zanzibar", "Stanbic Bank", "Standard Chartered Bank",
    "Tanzania Commercial Bank", "United Bank for Africa (UBA)", "Mwanga Bank",
    "Co-operative Bank of Tanzania", "Mufindi Community Bank", "Uchumi Commercial Bank",
    "Finca Microfinance Bank", "Selcom Microfinance Bank", "VisionFund Tanzania Microfinance Bank",
    "TIB Development Bank", "Tanzania Agricultural Development Bank", "NMB Bank", "Stanbick Bank",
    "First Housing Company Tanzania", "Tanzania Mortgage Refinance Company", "CRDB", "NBC Bank"
]


COLUMN_MAPPING = {
    'customer_id': 'Customer Identification Number',
    'bank_name': 'Bank Name',
    'branch_code': 'Branch Code',
    'branch_name': 'Branch name',
    'client_type': 'Client Type',
    'business_size': 'Size of the business',
    'annual_turnover': 'Annual turn-over of the borrower',
    'loan_number': 'Loan number',
    'disbursement_date': 'Disbursement Date',
    'maturity_date': 'Maturity Date',
    'currency': 'Currency',
    'tzs_disbursed_amount': 'TZS Disbursed Amount',
    'tzs_outstanding_principal': 'TZS Outstanding Principal Amount',
    'annual_interest_rate': 'Annual Interest Rate',
    'loan_type': 'loan Type/ General Category',
    'loan_economic_activity': 'Loan Economic Activity',
    'loan_purpose': 'Purpose of the loan',
    'asset_classification': 'Asset Classification Category',
    'loan_region': 'Location of invested loan (Region)',
    'loan_latitude': 'Invested Loan Geographical coordinates-Latitude',
    'loan_longitude': 'Invested Loan Geographical coordinates-Longitude',
    'collateral_pledged': 'Collateral Pledged',
    'collateral_pledged_date': 'Collateral Pledged Date',
    'collateral_market_value': 'TZS Market value of the collateral',
    'collateral_forced_sale_value': 'TZS Forced Sale Value of the collateral',
    'collateral_economic_activity': 'Collateral Economic activity ',
    'collateral_region': 'Location of the collateral (Region)',
    'collateral_latitude': 'Collateral Geographical Coordinates-Latitude',
    'collateral_longitude': 'Collateral Geographical Coordinates-Longitude',
    'climate_risk_insurance': 'Insurance coverage of the collateral against climate risks ',
    'insurance_type': 'Type of insurance policy',
    'insurance_provider': 'Name of insurance provider',
    'collateral_protected_value': 'Value of Collateral Protected'
}
