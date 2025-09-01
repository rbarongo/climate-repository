import os
import sys


root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_dir)

import streamlit as st
import pandas as pd
import requests
from validation import validate_dataframe
from configs.utils import stringify_currency
from configs.vars import SERVER_URL

st.set_page_config(page_title="Data Collection", page_icon="logo.png", layout="wide")
logo_col, title_col = st.columns([1, 7], gap="small")
with logo_col:
    st.image('../logo.png', width=100)
with title_col:
    st.title("Data collection for climate risk assessment")

manual_tab, upload_tab = st.tabs(["Manual Entry", "Bulk Upload"])

with manual_tab:
    st.header("Enter Loan Data Manually")
    st.info("The manual data entry form is available here.")

with upload_tab:
    st.header("Upload Loan Data File")
    st.info("Upload a CSV file with loan data. Please use the provided template.")

    uploader_type = st.radio("Select Uploader Type", ["Bank", "TMA"])

    if uploader_type == "Bank":

        uploaded_file = st.file_uploader(
            "Choose a file",
            type=['csv', 'xlsx']
        )

        if uploaded_file:
            try:
                if uploaded_file.name.endswith('.csv'):
                    df_ui = pd.read_csv(uploaded_file)
                    df = df_ui.copy()
                    if 'Annual turn-over of the borrower' in df_ui.columns:
                        df_ui['Annual turn-over of the borrower'] = df_ui['Annual turn-over of the borrower'].apply(
                            lambda x: stringify_currency(x))
                    if 'TZS Disbursed Amount' in df_ui.columns:
                        df_ui['TZS Disbursed Amount'] = df_ui['TZS Disbursed Amount'].apply(lambda x: stringify_currency(x))
                    if 'TZS Outstanding Principal Amount' in df_ui.columns:
                        df_ui['TZS Outstanding Principal Amount'] = df_ui['TZS Outstanding Principal Amount'].apply(
                            lambda x: stringify_currency(x))
                    if 'TZS Market value of the collateral' in df_ui.columns:
                        df_ui['TZS Market value of the collateral'] = df_ui['TZS Market value of the collateral'].apply(
                            lambda x: stringify_currency(x))
                    if 'TZS Forced Sale Value of the collateral' in df_ui.columns:
                        df_ui['TZS Forced Sale Value of the collateral'] = df_ui[
                            'TZS Forced Sale Value of the collateral'].apply(lambda x: stringify_currency(x))
                    if 'Value of Collateral Protected' in df_ui.columns:
                        df_ui['Value of Collateral Protected'] = df_ui['Value of Collateral Protected'].apply(
                            lambda x: stringify_currency(x))
                else:
                    df_ui = pd.read_excel(uploaded_file)
                    df = df_ui.copy()
                    if 'Annual turn-over of the borrower' in df_ui.columns:
                        df_ui['Annual turn-over of the borrower'] = df_ui['Annual turn-over of the borrower'].apply(
                            lambda x: stringify_currency(x))
                    if 'TZS Disbursed Amount' in df_ui.columns:
                        df_ui['TZS Disbursed Amount'] = df_ui['TZS Disbursed Amount'].apply(lambda x: stringify_currency(x))
                    if 'TZS Outstanding Principal Amount' in df_ui.columns:
                        df_ui['TZS Outstanding Principal Amount'] = df_ui['TZS Outstanding Principal Amount'].apply(
                            lambda x: stringify_currency(x))
                    if 'TZS Market value of the collateral' in df_ui.columns:
                        df_ui['TZS Market value of the collateral'] = df_ui['TZS Market value of the collateral'].apply(
                            lambda x: stringify_currency(x))
                    if 'TZS Forced Sale Value of the collateral' in df_ui.columns:
                        df_ui['TZS Forced Sale Value of the collateral'] = df_ui[
                            'TZS Forced Sale Value of the collateral'].apply(lambda x: stringify_currency(x))
                    if 'Value of Collateral Protected' in df_ui.columns:
                        df_ui['Value of Collateral Protected'] = df_ui['Value of Collateral Protected'].apply(
                            lambda x: stringify_currency(x))

                st.write("Preview of Uploaded Data:")
                st.dataframe(df_ui)

                # --- Validation Step ---
                if st.button("Validate and Submit Data"):
                    with st.spinner("Validating data..."):
                        errors = validate_dataframe(df)

                    if errors:
                        st.error("Validation Failed! Please correct the following errors in your file an upload again:")
                        error_df = pd.DataFrame(errors)

                        st.dataframe(error_df)
                    else:
                        # df['uploader_type'] = uploader_type
                        # df['region'] = region
                        # df['district'] = district
                        payload = df.to_dict(orient="records")
                        st.success("Validation Successful! Data is ready for submission.")

                        st.info("Data submission step would happen here.")
                        try:
                            response = requests.post(SERVER_URL, json=payload)
                            if response.status_code == 201:
                                st.success("Success! Data submitted")
                            else:
                                st.error(f"Failed to submit data. Server responded with: {response.text}")
                        except requests.exceptions.ConnectionError:
                            st.error(f"Connection Error: Could not connect to the server at {SERVER_URL}.")
                        except Exception as e:
                            st.error(f"An unexpected error occurred: {e}")

            except Exception as e:
                st.error(f"An error occurred while processing the file: {e}")
    else:
        st.info("TMA upload functionality is not implemented yet.")