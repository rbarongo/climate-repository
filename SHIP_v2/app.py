import os
import sys

root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_dir)

from sqlalchemy import exc
import bcrypt

import streamlit as st
import pandas as pd
import altair as alt
from pathlib import Path
from configs.utils import stringify_currency
from configs.vars import COLUMN_MAPPING
# from streamlit_folium import st_folium
# from folium.plugins import MarkerCluster
from configs.loc_manage import load_location_data, get_regions, get_districts, populate_map
from db_postgres import get_loans, get_user, add_user, get_all_users_from_db, delete_user


if st.session_state.get("authenticated"):
    layout = "wide"
    page_title = "BOT Credit Flow Dashboard"
else:
    layout = "centered"
    page_title = "Authenticate"

st.set_page_config(
    page_title=page_title,
    page_icon=" ",
    layout=layout,
    initial_sidebar_state="expanded"
)

DB_PATH = Path(__file__).parent / "loans.db"


def check_credentials_db(username, password):
    record = get_user(username)
    if record:
        password_hash = record.password_hash
        role = record.role
        if bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8')):
            return role
    return None


def get_all_users():
    return get_all_users_from_db()


def add_user_to_db(username, password, role):
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    try:
        add_user(username, hashed_password, role)
        return True
    except exc.IntegrityError:
        return False


def delete_user_from_db(username):
    try:
        return delete_user(username)
    except Exception as e:
        print(f"Error deleting user: {e}")
        return False


def login_flow():
    # Removed st.set_page_config from here
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image("logo.png", width=200)

    if st.session_state.get("authenticated"):
        return True

    with st.form("login_form"):
        st.title("Climate Data Repository")
        st.subheader("Authenticate")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Log In")

        if submitted:
            role = check_credentials_db(username, password)
            if role:
                st.session_state.authenticated = True
                st.session_state.role = role
                st.rerun()
            else:
                st.error("Invalid username or password")
    return False


if login_flow():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap');
        :root {
            --primary: #4361ee; --secondary: #3f37c9; --success: #4cc9f0;
            --warning: #f72585; --info: #4895ef; --dark: #343a40; --light: #f8f9fa;
        }
        * { font-family: 'Poppins', sans-serif; }
        .metric-card { background-color: white; border-radius: 10px; padding: 1.5rem; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border-left: 4px solid var(--primary); transition: transform 0.3s ease; }
        .metric-card:hover { transform: translateY(-5px); box-shadow: 0 6px 12px rgba(0,0,0,0.15); }
        .metric-title { font-size: 1rem; font-weight: 600; color: var(--dark); margin-bottom: 0.5rem; }
        .metric-value { font-size: 1.8rem; font-weight: 600; color: var(--primary); margin-bottom: 0.25rem; }
        .metric-subtitle { font-size: 0.85rem; color: #6c757d; }
        .chart-container { background-color: white; border-radius: 10px; padding: 1.5rem; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 1.5rem; }
        .chart-title { font-size: 1.2rem; font-weight: 600; color: var(--dark); margin-bottom: 1.5rem; }
        .stDataFrame { border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        footer { text-align: center; padding: 1rem; color: #6c757d; font-size: 0.9rem; }
    </style>
    """, unsafe_allow_html=True)


    def format_currency(amount):
        if amount >= 1e9: return f"{amount / 1e9:,.1f}B TZS"
        if amount >= 1e6: return f"{amount / 1e6:,.1f}M TZS"
        return f"{amount:,.0f} TZS"


    @st.cache_data(ttl=30)
    def get_uplaoded_data_from_db():
        df = get_loans()
        if not df.empty:
            df['disbursement_date'] = pd.to_datetime(df['disbursement_date']).dt.date
            df['maturity_date'] = pd.to_datetime(df['maturity_date']).dt.date
            df['collateral_pledged_date'] = pd.to_datetime(df['collateral_pledged_date']).dt.date
        return df


    df_uploaded = get_uplaoded_data_from_db()
    location_df = load_location_data()

    if not df_uploaded.empty:
        if 'loan_amount' not in st.session_state:
            min_loan = float(df_uploaded['tzs_disbursed_amount'].min())
            max_loan = float(df_uploaded['tzs_disbursed_amount'].max())
            st.session_state.loan_amount = (min_loan, max_loan)

        if 'collateral_value' not in st.session_state:
            min_val = float(df_uploaded['collateral_market_value'].min())
            max_val = float(df_uploaded['collateral_market_value'].max())
            st.session_state.collateral_value = (min_val, max_val)
    else:
        if 'loan_amount' not in st.session_state:
            st.session_state.loan_amount = (0.0, 0.0)
        if 'collateral_value' not in st.session_state:
            st.session_state.collateral_value = (0.0, 0.0)

    st.sidebar.image('logo.png')
    st.sidebar.title("Filters")

    bank_names = sorted(df_uploaded['bank_name'].dropna().unique().tolist()) if not df_uploaded.empty else []
    selected_banks = st.sidebar.multiselect("Bank Name", bank_names, key='bank_name')

    with st.sidebar.expander("Loan Filters", expanded=False):
        loan_types = sorted(df_uploaded['loan_type'].dropna().unique().tolist()) if not df_uploaded.empty else []
        selected_loan_types = st.multiselect("Loan Type", loan_types, key='loan_type')

        loan_activities = sorted(
            df_uploaded['loan_economic_activity'].dropna().unique().tolist()) if not df_uploaded.empty else []
        selected_loan_activities = st.multiselect("Loan Economic Activity", loan_activities,
                                                  key='loan_economic_activity')

        loan_statuses = ['All'] + (
            sorted(df_uploaded['asset_classification'].unique().tolist()) if not df_uploaded.empty else [])
        selected_status = st.selectbox("Status", loan_statuses, key='loan_status')

        if not df_uploaded.empty:
            min_loan, max_loan = float(df_uploaded['tzs_disbursed_amount'].min()), float(
                df_uploaded['tzs_disbursed_amount'].max())
            st.slider("Amount (TZS)", min_loan, max_loan, key='loan_amount')
        else:
            st.slider("Amount (TZS)", 0.0, 0.0, key='loan_amount', disabled=True)

        loan_regions = ['All'] + get_regions(location_df)
        selected_loan_region = st.selectbox("Region", loan_regions, key='loan_region')

        if selected_loan_region != 'All':
            districts_for_region = ['All'] + get_districts(location_df, selected_loan_region)
        else:
            districts_for_region = ['All']
        selected_loan_district = st.selectbox("District", districts_for_region, key='loan_district')

        if not df_uploaded.empty:
            min_disb_date, max_disb_date = df_uploaded['disbursement_date'].min(), df_uploaded[
                'disbursement_date'].max()
            st.date_input("Disbursement Date", value=(min_disb_date, max_disb_date), min_value=min_disb_date,
                          max_value=max_disb_date, key='disbursement_date')

            min_mat_date, max_mat_date = df_uploaded['maturity_date'].min(), df_uploaded['maturity_date'].max()
            st.date_input("Maturity Date", value=(min_mat_date, max_mat_date), min_value=min_mat_date,
                          max_value=max_mat_date, key='maturity_date')
        else:
            st.date_input("Disbursement Date", value=(pd.to_datetime('today').date(), pd.to_datetime('today').date()),
                          disabled=True, key='disbursement_date')
            st.date_input("Maturity Date", value=(pd.to_datetime('today').date(), pd.to_datetime('today').date()),
                          disabled=True, key='maturity_date')

    with st.sidebar.expander("Collateral Filters", expanded=False):
        collateral_types = sorted(
            df_uploaded['collateral_pledged'].dropna().unique().tolist()) if not df_uploaded.empty else []
        selected_collateral_types = st.multiselect("Collateral Type", collateral_types, key='collateral_type')

        collateral_activities = sorted(
            df_uploaded['collateral_economic_activity'].dropna().unique().tolist()) if not df_uploaded.empty else []
        selected_collateral_activities = st.multiselect("Collateral Economic Activity", collateral_activities,
                                                        key='collateral_economic_activity')

        if not df_uploaded.empty:
            min_val, max_val = float(df_uploaded['collateral_market_value'].min()), float(
                df_uploaded['collateral_market_value'].max())
            st.slider("Market Value (TZS)", min_val, max_val, key='collateral_value')
        else:
            st.slider("Market Value (TZS)", 0.0, 0.0, key='collateral_value', disabled=True)

        collateral_regions = ['All'] + (
            sorted(df_uploaded['collateral_region'].dropna().unique().tolist()) if not df_uploaded.empty else [])
        selected_collateral_region = st.selectbox("Region", collateral_regions, key='collateral_region')

        if selected_collateral_region != 'All':
            collateral_districts = ['All'] + get_districts(location_df, selected_collateral_region)
        else:
            collateral_districts = ['All']
        selected_collateral_district = st.selectbox("District", collateral_districts, key='collateral_district')

        if not df_uploaded.empty:
            min_pledge_date, max_pledge_date = df_uploaded['collateral_pledged_date'].min(), df_uploaded[
                'collateral_pledged_date'].max()
            st.date_input("Pledged Date", value=(min_pledge_date, max_pledge_date), min_value=min_pledge_date,
                          max_value=max_pledge_date, key='collateral_pledged_date')
        else:
            st.date_input("Pledged Date", value=(pd.to_datetime('today').date(), pd.to_datetime('today').date()),
                          disabled=True, key='collateral_pledged_date')

    filtered_df = df_uploaded.copy()

    if not filtered_df.empty:
        # Apply Loan Filters
        if st.session_state.bank_name:
            filtered_df = filtered_df[filtered_df['bank_name'].isin(st.session_state.bank_name)]
        if st.session_state.loan_type:
            filtered_df = filtered_df[filtered_df['loan_type'].isin(st.session_state.loan_type)]
        if st.session_state.loan_economic_activity:
            filtered_df = filtered_df[
                filtered_df['loan_economic_activity'].isin(st.session_state.loan_economic_activity)]
        if st.session_state.loan_status != 'All':
            filtered_df = filtered_df[filtered_df['asset_classification'] == st.session_state.loan_status]
        if st.session_state.loan_region != 'All':
            filtered_df = filtered_df[filtered_df['loan_region'] == st.session_state.loan_region]
        if st.session_state.loan_district != 'All':
            filtered_df = filtered_df[filtered_df['loan_district'] == st.session_state.loan_district]

        filtered_df = filtered_df[filtered_df['tzs_disbursed_amount'].between(st.session_state.loan_amount[0],
                                                                              st.session_state.loan_amount[1])]

        if 'disbursement_date' in st.session_state and len(st.session_state.disbursement_date) == 2:
            start_date, end_date = st.session_state.disbursement_date
            filtered_df = filtered_df[filtered_df['disbursement_date'].between(start_date, end_date)]

        if 'maturity_date' in st.session_state and len(st.session_state.maturity_date) == 2:
            start_date, end_date = st.session_state.maturity_date
            filtered_df = filtered_df[filtered_df['maturity_date'].between(start_date, end_date)]

        # Apply Collateral Filters
        if st.session_state.collateral_type:
            filtered_df = filtered_df[filtered_df['collateral_pledged'].isin(st.session_state.collateral_type)]
        if st.session_state.collateral_economic_activity:
            filtered_df = filtered_df[
                filtered_df['collateral_economic_activity'].isin(st.session_state.collateral_economic_activity)]
        if st.session_state.collateral_region != 'All':
            filtered_df = filtered_df[filtered_df['collateral_region'] == st.session_state.collateral_region]
        if st.session_state.collateral_district != 'All':
            filtered_df = filtered_df[filtered_df['collateral_district'] == st.session_state.collateral_district]

        filtered_df = filtered_df[filtered_df['collateral_market_value'].between(st.session_state.collateral_value[0],
                                                                                 st.session_state.collateral_value[1])]

        if 'collateral_pledged_date' in st.session_state and len(st.session_state.collateral_pledged_date) == 2:
            start_date, end_date = st.session_state.collateral_pledged_date
            filtered_df = filtered_df[filtered_df['collateral_pledged_date'].between(start_date, end_date)]

    st.title("Climate Data Repository")
    st.markdown("---")

    total_disbursed_loan = filtered_df['tzs_disbursed_amount'].sum() if not filtered_df.empty else 0
    num_businesses = filtered_df['customer_id'].nunique() if not filtered_df.empty else 0
    total_defaults = filtered_df[filtered_df['asset_classification'] == 'Doubtful'].shape[
        0] if not filtered_df.empty else 0
    total_collateral_value = filtered_df['collateral_market_value'].sum() if not filtered_df.empty else 0

    if not filtered_df.empty and total_defaults > 0:
        doubtful_df = filtered_df[filtered_df['asset_classification'] == 'Doubtful']
        location_counts = doubtful_df['loan_district'].value_counts()
        if not location_counts.empty:
            top_location = location_counts.index[0]
            top_location_count = location_counts.iloc[0]
            top_location_subtitle = f"{top_location_count} doubtful assets"
        else:
            top_location = "N/A"
            top_location_subtitle = "No doubtful assets found"
    else:
        top_location = "N/A"
        top_location_subtitle = "No doubtful assets found"

    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.markdown(
            f'<div class="metric-card"><div class="metric-title">Total Disbursed Loan</div><div class="metric-value">{format_currency(total_disbursed_loan)}</div><div class="metric-subtitle">Issued loans in selection</div></div>',
            unsafe_allow_html=True)
    with col2:
        st.markdown(
            f'<div class="metric-card" style="border-left-color: #4cc9f0;"><div class="metric-title">Number of Businesses</div><div class="metric-value" style="color: #4cc9f0;">{num_businesses:,}</div><div class="metric-subtitle">Active businesses</div></div>',
            unsafe_allow_html=True)
    with col3:
        st.markdown(
            f'<div class="metric-card" style="border-left-color: #f72585;"><div class="metric-title">Total Doubtful Assets</div><div class="metric-value" style="color: #f72585;">{total_defaults}</div><div class="metric-subtitle">Loans in default</div></div>',
            unsafe_allow_html=True)
    with col4:
        st.markdown(
            f'<div class="metric-card" style="border-left-color: #7209b7;"><div class="metric-title">Total Collateral</div><div class="metric-value" style="color: #7209b7;">{format_currency(total_collateral_value)}</div><div class="metric-subtitle">Market value of collateral</div></div>',
            unsafe_allow_html=True)
    with col5:
        st.markdown(
            f'<div class="metric-card" style="border-left-color: #f9c74f;"><div class="metric-title">Top Doubtful Location</div><div class="metric-value" style="color: #f9c74f; font-size: 1.6rem;">{top_location}</div><div class="metric-subtitle">{top_location_subtitle}</div></div>',
            unsafe_allow_html=True)

    st.write("")

    ### SESSION MANAGEMENT
    tab_names = ["Main Dashboard", "Regional Analysis", "Other analytics", "Users"]
    if 'active_tab_index' not in st.session_state:
        st.session_state.active_tab_index = 0
    #### END SESSION

    if st.session_state.role == "admin":
        main_dash, map, uploaded_data, users = st.tabs(
            ["Main Dashboard", "Regional Analysis", "Other analytics", "Users"]
        )
    else:
        main_dash, map, uploaded_data = st.tabs(
            ["Main Dashboard", "Regional Analysis", "Other analytics"]
        )

    with main_dash:
        st.session_state.active_tab_index = 0

        st.subheader("Recent Uploads")
        if st.button("🔄  Refresh Data", key="upload_tab"):
            st.session_state.active_tab_index = 2
            st.cache_data.clear()
            st.rerun()

        if filtered_df.empty:
            st.warning("No data found for the selected filters.")

        existing_columns = filtered_df.columns
        df_display_uploaded = filtered_df[existing_columns].rename(columns=COLUMN_MAPPING)

        if 'Annual turn-over of the borrower' in df_display_uploaded.columns:
            df_display_uploaded['Annual turn-over of the borrower'] = df_display_uploaded[
                'Annual turn-over of the borrower'].apply(
                lambda x: stringify_currency(x))
        if 'TZS Disbursed Amount' in df_display_uploaded.columns:
            df_display_uploaded['TZS Disbursed Amount'] = df_display_uploaded['TZS Disbursed Amount'].apply(
                lambda x: stringify_currency(x))
        if 'TZS Outstanding Principal Amount' in df_display_uploaded.columns:
            df_display_uploaded['TZS Outstanding Principal Amount'] = df_display_uploaded[
                'TZS Outstanding Principal Amount'].apply(
                lambda x: stringify_currency(x))
        if 'TZS Market value of the collateral' in df_display_uploaded.columns:
            df_display_uploaded['TZS Market value of the collateral'] = df_display_uploaded[
                'TZS Market value of the collateral'].apply(
                lambda x: stringify_currency(x))
        if 'TZS Forced Sale Value of the collateral' in df_display_uploaded.columns:
            df_display_uploaded['TZS Forced Sale Value of the collateral'] = df_display_uploaded[
                'TZS Forced Sale Value of the collateral'].apply(
                lambda x: stringify_currency(x))
        if 'Value of Collateral Protected' in df_display_uploaded.columns:
            df_display_uploaded['Value of Collateral Protected'] = df_display_uploaded[
                'Value of Collateral Protected'].apply(
                lambda x: stringify_currency(x))

        st.write(f"{len(df_display_uploaded)} selected records")
        st.dataframe(df_display_uploaded, use_container_width=True)

    def reset_filters():
        st.session_state.bank_name = []
        st.session_state.loan_type = []
        st.session_state.loan_economic_activity = []
        st.session_state.loan_status = 'All'
        st.session_state.loan_region = 'All'
        st.session_state.loan_district = 'All'
        st.session_state.collateral_type = []
        st.session_state.collateral_economic_activity = []
        st.session_state.collateral_region = 'All'
        st.session_state.collateral_district = 'All'

        if not df_uploaded.empty:
            st.session_state.disbursement_date = (df_uploaded['disbursement_date'].min(),
                                                  df_uploaded['disbursement_date'].max())
            st.session_state.maturity_date = (df_uploaded['maturity_date'].min(), df_uploaded['maturity_date'].max())
            st.session_state.collateral_pledged_date = (df_uploaded['collateral_pledged_date'].min(),
                                                        df_uploaded['collateral_pledged_date'].max())

            st.session_state.loan_amount = (float(df_uploaded['tzs_disbursed_amount'].min()),
                                            float(df_uploaded['tzs_disbursed_amount'].max()))
            st.session_state.collateral_value = (float(df_uploaded['collateral_market_value'].min()),
                                                 float(df_uploaded['collateral_market_value'].max()))
        else:
            today = pd.to_datetime('today').date()
            st.session_state.disbursement_date = (today, today)
            st.session_state.maturity_date = (today, today)
            st.session_state.collateral_pledged_date = (today, today)
            st.session_state.loan_amount = (0.0, 0.0)
            st.session_state.collateral_value = (0.0, 0.0)


    st.sidebar.button("🔄  Reset Filters", on_click=reset_filters)

    if st.sidebar.button("Log Out"):
        st.session_state.authenticated = False
        st.session_state.role = None
        st.session_state.username = None
        st.rerun()

    with map:
        st.session_state.active_tab_index = 1
        st.subheader("Map Analysis")
        populate_map(filtered_df)

    with uploaded_data:
        if filtered_df.empty:
            st.warning("No data to display for the selected filters. Please adjust the filters in the sidebar.")
        else:
            # --- Total Disbursed Amount by Bank Name (Horizontal for better readability) ---
            st.markdown('<div class="chart-container"><div class="chart-title">Total Loan Amount by Bank</div>',
                        unsafe_allow_html=True)
            bank_loans = filtered_df.groupby('bank_name')['tzs_disbursed_amount'].sum().reset_index()

            chart1 = alt.Chart(bank_loans).mark_bar(
                cornerRadiusTopRight=5,
                cornerRadiusBottomRight=5
            ).encode(
                y=alt.Y('bank_name:N', sort='-x', title='Bank Name'),
                x=alt.X('tzs_disbursed_amount:Q', title='Total Disbursed Amount (TZS)'),
                tooltip=['bank_name', alt.Tooltip('tzs_disbursed_amount:Q', format=',.0f')]
            ).properties(
                height=400
            ).configure_view(
                stroke=None
            )
            st.altair_chart(chart1, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

            col1, col2 = st.columns(2)

            with col1:
                # --- Chart 2: Loan Status Distribution ---
                st.markdown('<div class="chart-container"><div class="chart-title">Loan Status Distribution</div>',
                            unsafe_allow_html=True)
                status_counts = filtered_df['asset_classification'].value_counts().reset_index()
                status_counts.columns = ['asset_classification', 'count']

                chart2 = alt.Chart(status_counts).mark_arc(
                    innerRadius=80
                ).encode(
                    theta=alt.Theta(field="count", type="quantitative"),
                    color=alt.Color(field="asset_classification", type="nominal", title="Asset Classification"),
                    tooltip=['asset_classification', 'count']
                ).properties(
                    height=400
                )
                st.altair_chart(chart2, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)

            with col2:
                # --- Top 3 Economic Activities by Loan Amount ---
                st.markdown(
                    '<div class="chart-container"><div class="chart-title">Top 5 Economic Activities by Loan Amount</div>',
                    unsafe_allow_html=True)
                activity_loans = filtered_df.groupby('loan_economic_activity')['tzs_disbursed_amount'].sum().nlargest(
                    5).reset_index()

                chart3 = alt.Chart(activity_loans).mark_bar(
                    cornerRadiusBottomRight=5,
                    cornerRadiusTopRight=5
                ).encode(
                    y=alt.Y('loan_economic_activity:N', sort='-x', title='Economic Activity'),
                    x=alt.X('tzs_disbursed_amount:Q', title='Total Disbursed Amount (TZS)'),
                    tooltip=['loan_economic_activity', alt.Tooltip('tzs_disbursed_amount:Q', format=',.0f')]
                ).properties(
                    height=400
                )
                st.altair_chart(chart3, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)

            # --- Monthly Loan Disbursement Trends (Time Series) ---
            st.markdown('<div class="chart-container"><div class="chart-title">Monthly Loan Disbursement Trends</div>',
                        unsafe_allow_html=True)

            ts_df = filtered_df.copy()
            ts_df['disbursement_date'] = pd.to_datetime(ts_df['disbursement_date'])
            monthly_loans = ts_df.set_index('disbursement_date').resample('MS')[
                'tzs_disbursed_amount'].sum().reset_index()
            monthly_loans.columns = ['month', 'total_amount']

            chart4 = alt.Chart(monthly_loans).mark_area(
                line={'color': '#4361ee'},
                color=alt.Gradient(
                    gradient='linear',
                    stops=[alt.GradientStop(color='white', offset=0),
                           alt.GradientStop(color='#4cc9f0', offset=1)],
                    x1=1,
                    x2=1,
                    y1=1,
                    y2=0
                )
            ).encode(
                x=alt.X('month:T', title='Month of Disbursement'),
                y=alt.Y('total_amount:Q', title='Total Disbursed Amount (TZS)'),
                tooltip=[alt.Tooltip('month:T', title='Month'),
                         alt.Tooltip('total_amount:Q', title='Total Amount', format=',.0f')]
            ).properties(
                height=450
            ).interactive()

            st.altair_chart(chart4, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)


    if st.session_state.role == "admin":
        with users:
            st.session_state.active_tab_index = 3
            with st.form('add_new_user_form', clear_on_submit=True):
                st.subheader("Admin Settings")
                st.write("Add new user")
                new_username = st.text_input("Enter new username: ")
                new_passw = st.text_input("Password: ", type="password")
                new_role = st.selectbox("Role", ['user', 'admin'])
                submitted = st.form_submit_button("Add User")
                if submitted:
                    if not new_username or not new_passw:
                        st.warning("Please provide both a username and password.")
                    else:
                        if add_user_to_db(new_username, new_passw, new_role):
                            st.success(f"User '{new_username}' added successfully!")
                        else:
                            st.error(f"Username '{new_username}' already exists.")

            st.markdown("---")
            st.subheader("Existing Users")
            st.dataframe(get_all_users(), use_container_width=True)

            st.markdown("---")
            st.subheader("Delete User")
            all_users_df = get_all_users()

            users_to_delete = all_users_df[all_users_df['username'] != st.session_state.get('username')]

            if users_to_delete.empty:
                st.info("No other users available to delete.")
            else:
                user_to_delete = st.selectbox("Select a user to delete", users_to_delete['username'].tolist())
                if st.button(f"Delete User '{user_to_delete}'", key=f"delete_{user_to_delete}"):
                    if delete_user_from_db(user_to_delete):
                        st.success(f"User '{user_to_delete}' has been deleted.")
                        st.rerun()
                    else:
                        st.error(f"An error occurred while trying to delete user '{user_to_delete}'.")

