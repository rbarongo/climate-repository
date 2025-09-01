import pandas as pd
import numpy as np
from faker import Faker
import random
from loc_manage import load_location_data, get_regions

fake = Faker()



def simulate_bank_data(bank_name, num_records=200):
    loans = []
    for i in range(num_records):
        loans.append({
            'Customer Identification Number': fake.uuid4(),
            'Bank Name': bank_name,  # Use the provided bank name
            'Branch Code': fake.bothify(text='BR###'),
            'Branch name': random .choice(['Ilala Branch', 'Arusha City Branch', 'Kinondoni Branch', 'Ubungo Branch', 'Nyamagana Branch', 'Mbeya City Branch', 'Tanga City Branch', 'Kilosa Branch', 'Sokoine Branch']),
            'Client Type': random.choice(['Individual', 'SME', 'Corporate', 'Staff', 'Related parties',
                                          'Salaried', 'Non-salaried', 'microfinance serviec providers', 'pension fund members',
                                          'DC', 'MC']),
            'Size of the business': random.choice(['Micro', 'Small', 'Medium', 'Large']),
            'Annual turn-over of the borrower': round(random.uniform(1e6, 1e9), 2),
            'Balance sheet size of the borrower': round(random.uniform(1e6, 1e9), 2),
            'Loan number': fake.bothify(text='LN#######'),
            'Disbursement Date': fake.date_between(start_date='-3y', end_date='-1y'),
            'Maturity Date': fake.date_between(start_date='today', end_date='+3y'),
            'Currency': 'TZS',
            'TZS Disbursed Amount': round(random.uniform(1e5, 1e8), 2),
            'TZS Outstanding Principal Amount': round(random.uniform(1e4, 1e7), 2),
            'Frequency of repayment': random.choice(['Weekly','Monthly', 'Quarterly', 'Semi-Annual', 'Annual']),
            'Interest Rate Type': random.choice(['Fixed', 'Floating']),
            'Annual Interest Rate': round(random.uniform(5.0, 20.0), 2),
            'Loan authorization type': random.choice(['SLA', 'FIA', 'BUL', 'Others']),
            'loan Type/ General Category': random.choice(['Mortgage', 'Personal', 'Business', 'Agricultural']),
            'Loan Economic Activity': random.choice(['Retail', 'Manufacturing', 'Farming']),
            'Purpose of the loan': random.choice(['Working Capital', 'Asset Purchase', 'Expansion']),
            'Asset Classification Category': random.choice(['Standard', 'Substandard', 'Doubtful']),
            'Location of invested loan (Region)': random.choice(get_regions(load_location_data())),
            'Location of invested loan (District)': random.choice(['Ilala', 'Arusha City', 'Kinondoni', 'Ubungo', 'Nyamagana', 'Mbeya City', 'Tanga City', 'Morogoro Urban', 'Mjini Magharibi']),
            'Location of invested loan (Ward)': random.choice(['Ilala', 'Kaloleni', 'Mikocheni', 'Kijitonyama', 'Ndugumbi', 'Nyamagana', 'Sabasaba', 'Makumbusho', 'Mjini']),
            'Location of invested loan (Street)': random.choice(['Regeant', 'Maktaba', 'Nyerere', 'Sam Nujoma', 'Azikiwe', 'Sokoine', 'Uhuru', 'Lumumba']),
            'Invested Loan Geographical coordinates-Latitude': random.choice([
                        -6.8182, -6.7387, -6.8549, -6.7944, -6.8786,
                        -3.3382, -3.4173, -3.4526, -3.3991, -3.5149,
                        -6.1512, -6.1438, -6.2039, -6.1857, -6.1294,
                        -2.4821, -2.5223, -2.4698, -2.5146, -2.4915,
                        -8.9045, -8.8873, -8.9264, -8.9151, -8.9398,
                        -5.0741, -5.0315, -5.0968, -5.0582, -5.0157,
                        -6.8284, -6.8097, -6.8451, -6.8679, -6.8125,
                        -6.1702, -6.2044, -6.1947, -6.1831, -6.1578
                    ]),
            'Invested Loan Geographical coordinates-Longitude': random.choice([
                        39.2701, 39.2174, 39.2916, 39.2049, 39.2268,
                        36.6428, 36.7039, 36.5827, 36.6643, 36.6198,
                        35.7813, 35.8226, 35.7647, 35.8102, 35.7790,
                        32.9278, 32.8981, 32.8567, 32.9624, 32.8766,
                        33.4339, 33.4742, 33.4987, 33.4528, 33.4631,
                        39.1107, 39.0843, 39.1262, 39.0715, 39.0983,
                        37.6605, 37.6847, 37.6932, 37.6494, 37.6358,
                        39.2136, 39.2169, 39.2471, 39.2315, 39.2246
                    ]),
            'Collateral Pledged': random.choice(['Gold', 'Cash', 'Deposits', 'Government Securities',
                                                 'Guarantee from Revolutionary Government of Zanzibar',
                                                 'Terminal Benefits', 'Guarantee of Unconditional and irrevocable '
                                                                      'guarantee of a first class international bank '
                                                                      'or a first class international financial '
                                                                      'institution.',
                                                 'Residential mortgage', 'Commercial real estate', 'agricultural land', 'Guarantee from Local government units',
                                                 'Parastatals Guarantee', 'Other mortgages eg chattels', 'Compulsory '
                                                                                                         'savings',
                                                 'Stocks', 'Equipment',
                                                 'MotorVehicle', 'Letter of Hypothecation', 'Debenture', 'Unsecured']),
            'Collateral Pledged Date': fake.date_between(start_date='-3y', end_date='today'),
            'TZS Market value of the collateral': round(random.uniform(1e5, 1e7), 2),
            'TZS Forced Sale Value of the collateral': round(random.uniform(5e4, 9e6), 2),
            'Collateral Economic activity ': random.choice(['Agriculture', 'Transport', 'Construction']),
            'Collateral Region': random.choice(get_regions(load_location_data())),
            'Collateral District': random.choice(['Ilala', 'Arusha City', 'Kinondoni', 'Ubungo', 'Nyamagana', 'Mbeya City', 'Tanga City', 'Morogoro Urban', 'Mjini Magharibi']),
            'Collateral Ward': random.choice(['Ilala', 'Kaloleni', 'Mikocheni', 'Kijitonyama', 'Ndugumbi', 'Nyamagana', 'Sabasaba', 'Makumbusho', 'Mjini']),
            'Collateral Street': random.choice(['Regeant', 'Maktaba', 'Nyerere', 'Sam Nujoma', 'Azikiwe', 'Sokoine', 'Uhuru', 'Lumumba']),
            'Collateral Geographical Coordinates-Latitude': random.choice([
                -6.8182, -6.7387, -6.8549, -6.7944, -6.8786,
                -3.3382, -3.4173, -3.4526, -3.3991, -3.5149,
                -6.1512, -6.1438, -6.2039, -6.1857, -6.1294,
                -2.4821, -2.5223, -2.4698, -2.5146, -2.4915,
                -8.9045, -8.8873, -8.9264, -8.9151, -8.9398,
                -5.0741, -5.0315, -5.0968, -5.0582, -5.0157,
                -6.8284, -6.8097, -6.8451, -6.8679, -6.8125,
                -6.1702, -6.2044, -6.1947, -6.1831, -6.1578
            ]),
            'Collateral Geographical Coordinates-Longitude': random.choice([
                39.2701, 39.2174, 39.2916, 39.2049, 39.2268,
                36.6428, 36.7039, 36.5827, 36.6643, 36.6198,
                35.7813, 35.8226, 35.7647, 35.8102, 35.7790,
                32.9278, 32.8981, 32.8567, 32.9624, 32.8766,
                33.4339, 33.4742, 33.4987, 33.4528, 33.4631,
                39.1107, 39.0843, 39.1262, 39.0715, 39.0983,
                37.6605, 37.6847, 37.6932, 37.6494, 37.6358,
                39.2136, 39.2169, 39.2471, 39.2315, 39.2246
            ]),
            'Insurance coverage of the collateral against climate risks ': random.choice(['Yes', 'No']),
            'Type of insurance policy': random.choice(['Comprehensive', 'Fire & Theft', 'Climate Risk']),
            'Name of insurance provider': fake.company(),
            'Value of Collateral Protected': round(random.uniform(1e5, 1e7), 2)
        })

    loans_df = pd.DataFrame(loans)
    return loans_df


def introduce_noise(df, noise_fraction=0.6):
    noisy_df = df.copy()
    num_noise_rows = int(len(df) * noise_fraction)
    noise_indices = np.random.choice(df.index, size=num_noise_rows, replace=False)

    for i in noise_indices:
        col_for_noise = random.choice(['Maturity Date', 'Annual Interest Rate', 'TZS Disbursed Amount'])
        if col_for_noise == 'Maturity Date':
            noisy_df.loc[i, col_for_noise] = fake.date_between(start_date='-5y', end_date='-4y')
        elif col_for_noise == 'Annual Interest Rate':
            noisy_df.loc[i, col_for_noise] = random.choice([150, 500, 300])
        elif col_for_noise == 'TZS Disbursed Amount':
            noisy_df.loc[i, col_for_noise] = round(random.uniform(-1e5, -1e7), 2)
        elif col_for_noise == 'Location of invested loan (Region)':
            noisy_df.loc[i, col_for_noise] = None
        elif col_for_noise == 'Location of invested loan (Ward)':
            noisy_df.loc[i, col_for_noise] = None

    return noisy_df


if __name__ == '__main__':
    dest_dir = '../form/dummy_data'
    banks = ['CRDB Bank', 'Mwanga Bank', 'NBC Bank', 'NMB Bank', 'Stanbick Bank', 'Absa Bank']
    for bank in banks:
        bank_df = simulate_bank_data(bank, num_records=1000)

        bank_df.to_csv(f'{dest_dir}/{bank.replace(" ", "_")}_dummyNew.csv', index=False)

        noisy_bank_df = introduce_noise(bank_df)
        noisy_bank_df.to_csv(f'{dest_dir}/{bank.replace(" ", "_")}_noisy_dummyNew.csv', index=False)

    print("Data generation complete. Files are saved in the current directory.")