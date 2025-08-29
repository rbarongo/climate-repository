import sqlite3
import bcrypt
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from matplotlib.backend_tools import cursors
from plotly.subplots import make_subplots
import json
from pathlib import Path
from form.utils import stringify_currency
from form.vars import COLUMN_MAPPING
import pydeck as pdk
# from streamlit_folium import st_folium
# from folium.plugins import MarkerCluster
import folium
import json
import leafmap.foliumap as leafmap
import geopandas as gpd


DB_PATH = Path(__file__).parent / "loans.db"


def check_credentials_db(username, password):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT password_hash, role FROM users WHERE username = ?",
                   (username,))
    record = cursor.fetchone()
    conn.close()

    if record:
        password_hash, role = record
        if bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8')):
            return role
    return None


def get_all_users():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT username, role FROM users", conn)
    conn.close()
    return df


def add_user_to_db(username, password, role):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    try:
        cursor.execute("INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                       (username, hashed_password, role))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def login_flow():
    st.set_page_config(
        page_title="Authenticate",
        # page_icon="📊",
        layout="centered",
        initial_sidebar_state="expanded"
    )
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
    # st.sidebar.success(f"Logged in as {st.session_state.role}")
    st.set_page_config(
        page_title="BOT Credit Flow Dashboard",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )
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
        conn = sqlite3.connect(DB_PATH)
        try:
            df = pd.read_sql_query("SELECT * FROM loans", conn)
        except pd.io.sql.DatabaseError:
            return pd.DataFrame()
        finally:
            conn.close()

        if not df.empty:
            df['disbursement_date'] = pd.to_datetime(df['disbursement_date']).dt.date
            df['maturity_date'] = pd.to_datetime(df['maturity_date']).dt.date
            df['collateral_pledged_date'] = pd.to_datetime(df['collateral_pledged_date']).dt.date
        return df


    df_uploaded = get_uplaoded_data_from_db()

    st.sidebar.image('logo.png')
    st.sidebar.title("Filters")

    
    bank_names = sorted(df_uploaded['bank_name'].dropna().unique().tolist())
    selected_banks = st.sidebar.multiselect("Bank Name", bank_names, key='bank_name')

    with st.sidebar.expander("Loan Filters", expanded=False):
        loan_types = sorted(df_uploaded['loan_type'].dropna().unique().tolist())
        selected_loan_types = st.multiselect("Loan Type", loan_types, key='loan_type')

        loan_activities = sorted(df_uploaded['loan_economic_activity'].dropna().unique().tolist())
        selected_loan_activities = st.multiselect("Loan Economic Activity", loan_activities, key='loan_economic_activity')
        # Loan Status
        loan_statuses = ['All'] + sorted(df_uploaded['asset_classification'].unique().tolist())
        selected_status = st.selectbox("Status", loan_statuses, key='loan_status')
        
        # Loan Amount
        min_loan, max_loan = float(df_uploaded['tzs_disbursed_amount'].min()), float(df_uploaded['tzs_disbursed_amount'].max())
        selected_loan_range = st.slider("Amount (TZS)", min_loan, max_loan, value=(min_loan, max_loan), key='loan_amount')
        
        # Loan Location (Dependent Dropdowns)
        loan_regions = ['All'] + sorted(df_uploaded['loan_region'].dropna().unique().tolist())
        selected_loan_region = st.selectbox("Region", loan_regions, key='loan_region')
        
        if selected_loan_region != 'All':
            districts = ['All'] + sorted(df_uploaded[df_uploaded['loan_region'] == selected_loan_region]['loan_district'].dropna().unique().tolist())
        else:
            districts = ['All']
        selected_loan_district = st.selectbox("District", districts, key='loan_district')

        min_disb_date, max_disb_date = df_uploaded['disbursement_date'].min(), df_uploaded['disbursement_date'].max()
        st.date_input("Disbursement Date", value=(min_disb_date, max_disb_date), min_value=min_disb_date, max_value=max_disb_date, key='disbursement_date')

        min_mat_date, max_mat_date = df_uploaded['maturity_date'].min(), df_uploaded['maturity_date'].max()
        st.date_input("Maturity Date", value=(min_mat_date, max_mat_date), min_value=min_mat_date, max_value=max_mat_date, key='maturity_date')




    # --- Collateral Filters ---
    with st.sidebar.expander("Collateral Filters", expanded=False):
        # Collateral Type Filte
        collateral_types = sorted(df_uploaded['collateral_pledged'].dropna().unique().tolist())
        selected_collateral_types = st.multiselect("Collateral Type", collateral_types, key='collateral_type')

        # --- Collateral Economic Activity Filter ---
        collateral_activities = sorted(df_uploaded['collateral_economic_activity'].dropna().unique().tolist())
        selected_collateral_activities = st.multiselect("Collateral Economic Activity", collateral_activities, key='collateral_economic_activity')
        # Collateral Type
        # collateral_types = ['All'] + sorted(df_uploaded['collateral_pledged'].unique().tolist())
        # selected_collateral = st.selectbox("Type", collateral_types, key='collateral_type')
        
        # Collateral Value
        min_val, max_val = float(df_uploaded['collateral_market_value'].min()), float(df_uploaded['collateral_market_value'].max())
        selected_value_range = st.slider("Market Value (TZS)", min_val, max_val, value=(min_val, max_val), key='collateral_value')

        # Collateral Location (Dependent Dropdowns)
        collateral_regions = ['All'] + sorted(df_uploaded['collateral_region'].dropna().unique().tolist())
        selected_collateral_region = st.selectbox("Region", collateral_regions, key='collateral_region')
        
        if selected_collateral_region != 'All':
            districts = ['All'] + sorted(df_uploaded[df_uploaded['collateral_region'] == selected_collateral_region]['collateral_district'].dropna().unique().tolist())
        else:
            districts = ['All']
        selected_collateral_district = st.selectbox("District", districts, key='collateral_district')
        min_pledge_date, max_pledge_date = df_uploaded['collateral_pledged_date'].min(), df_uploaded['collateral_pledged_date'].max()
        st.date_input("Pledged Date", value=(min_pledge_date, max_pledge_date), min_value=min_pledge_date, max_value=max_pledge_date, key='collateral_pledged_date')

    filtered_df = df_uploaded.copy()

    # Apply Loan Filters
    if st.session_state.loan_type: 
        filtered_df = filtered_df[filtered_df['loan_type'].isin(st.session_state.loan_type)]
    if st.session_state.loan_economic_activity: 
        filtered_df = filtered_df[filtered_df['loan_economic_activity'].isin(st.session_state.loan_economic_activity)]
    if st.session_state.loan_status != 'All':
        filtered_df = filtered_df[filtered_df['asset_classification'] == st.session_state.loan_status]
    if st.session_state.loan_region != 'All':
        filtered_df = filtered_df[filtered_df['loan_region'] == st.session_state.loan_region]
    if st.session_state.loan_district != 'All':
        filtered_df = filtered_df[filtered_df['loan_district'] == st.session_state.loan_district]
    filtered_df = filtered_df[filtered_df['tzs_disbursed_amount'].between(st.session_state.loan_amount[0], st.session_state.loan_amount[1])]


    # Apply Collateral Filters
    if st.session_state.collateral_type: 
        filtered_df = filtered_df[filtered_df['collateral_pledged'].isin(st.session_state.collateral_type)]
    if st.session_state.collateral_economic_activity: 
        filtered_df = filtered_df[filtered_df['collateral_economic_activity'].isin(st.session_state.collateral_economic_activity)]
    if st.session_state.collateral_region != 'All':
        filtered_df = filtered_df[filtered_df['collateral_region'] == st.session_state.collateral_region]
    if st.session_state.collateral_district != 'All':
        filtered_df = filtered_df[filtered_df['collateral_district'] == st.session_state.collateral_district]
    filtered_df = filtered_df[filtered_df['collateral_market_value'].between(st.session_state.collateral_value[0], st.session_state.collateral_value[1])]

    
    st.title("Climate Data Repository")
    st.markdown("---")
    # st.write(filtered_df.columns)

    # Calculations for Metric Cards
    total_disbursed_loan = filtered_df['tzs_disbursed_amount'].sum()
    num_businesses = filtered_df['customer_id'].nunique()
    total_defaults = filtered_df[filtered_df['asset_classification'] == 'Doubtful'].shape[0]
    total_collateral_value = filtered_df['collateral_market_value'].sum()

    # Calculation for location with most doubtful assets
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

    #todo change how the tab content is managed
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
        if st.button("🔄 Refresh Data", key="upload_tab"):
            st.session_state.active_tab_index = 2
            st.cache_data.clear()
            st.rerun()

        if filtered_df.empty:
            st.warning("No data found")

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

        st.markdown("---")
        st.subheader("Charts")
        col_chart, col_side = st.columns([7, 3])
        with col_chart:
            st.markdown(
                '<div class="chart-container"><div class="chart-title">Total Loans Issued vs. Paid per Month</div>',
                unsafe_allow_html=True)

        with col_side:
            st.markdown('<div class="chart-container"><div class="chart-title">Loan Status Distribution</div>',
                        unsafe_allow_html=True)


    def reset_filters():
        st.session_state.bank_name = []
        st.session_state.loan_type = []
        st.session_state.loan_economic_activity = []
        st.session_state.loan_status = 'All'
        st.session_state.disbursement_date = (df_uploaded['disbursement_date'].min(), df_uploaded['disbursement_date'].max())
        st.session_state.maturity_date = (df_uploaded['maturity_date'].min(), df_uploaded['maturity_date'].max())
        st.session_state.loan_region = 'All'
        st.session_state.loan_district = 'All'
        st.session_state.loan_amount = (df_uploaded['tzs_disbursed_amount'].min(), df_uploaded['tzs_disbursed_amount'].max())
        st.session_state.collateral_type = []
        st.session_state.collateral_economic_activity = []
        st.session_state.collateral_pledged_date = (df_uploaded['collateral_pledged_date'].min(), df_uploaded['collateral_pledged_date'].max())
        st.session_state.collateral_region = 'All'
        st.session_state.collateral_district = 'All'
        st.session_state.collateral_value = (df_uploaded['collateral_market_value'].min(), df_uploaded['collateral_market_value'].max())


    st.sidebar.button("🔄 Reset Filters", on_click=reset_filters)

    if st.sidebar.button("Log Out"):
        st.session_state.authenticated = False
        st.session_state.role = None
        st.rerun()

    with map:
        st.session_state.active_tab_index = 1
        st.subheader("Map Analysis")
        st.session_state.active_tab_index = 1
        if filtered_df.empty:
            st.warning("No data available for the selected filters to display on the map.")
        else:
            
            df_agg = filtered_df.copy()
            df_agg['is_doubtful'] = (df_agg['asset_classification'] == 'Doubtful').astype(int)

            district_summary = df_agg.groupby('loan_district').agg(
                total_disbursed=('tzs_disbursed_amount', 'sum'),
                total_collateral=('collateral_market_value', 'sum'),
                doubtful_count=('is_doubtful', 'sum')
            ).reset_index()

            geojson_file_path = 'map_data/districts.geojson'

            try:
                gdf = gpd.read_file(geojson_file_path)

                geojson_district_col = 'dist_name' 
                if geojson_district_col not in gdf.columns:
                     st.error(f"CRITICAL: The column '{geojson_district_col}' was not found in your GeoJSON file. "
                              f"Please update this variable in the code with the correct column name. "
                              f"Available columns are: {list(gdf.columns)}")
                else:
                    merged_gdf = gdf.merge(
                        district_summary,
                        left_on=geojson_district_col,
                        right_on='loan_district',
                        how='left'
                    )

                    merged_gdf[['total_disbursed', 'total_collateral', 'doubtful_count']] = merged_gdf[
                        ['total_disbursed', 'total_collateral', 'doubtful_count']].fillna(0)

                    merged_gdf['total_disbursed_str'] = merged_gdf['total_disbursed'].apply(format_currency)
                    merged_gdf['total_collateral_str'] = merged_gdf['total_collateral'].apply(format_currency)

                    m = leafmap.Map(center=[-6.3690, 34.8888], zoom=6, tiles="CartoDB positron")

                    style = {"stroke": True, "color": "#333", "weight": 1, "opacity": 0.8, "fillColor": "#4361ee", "fillOpacity": 0.3}

                    tooltip = folium.GeoJsonTooltip(
                        fields=['loan_district', 'total_disbursed_str', 'total_collateral_str', 'doubtful_count'],
                        aliases=['District:', 'Total Disbursed:', 'Total Collateral Value:', 'Number of Doubtful Loans:'],
                        localize=True,
                        sticky=False,
                        style="""
                            background-color: #F0EFEF;
                            border: 2px solid black;
                            border-radius: 3px;
                            box-shadow: 3px;
                        """
                    )
                    
                    g = folium.GeoJson(
                        merged_gdf,
                        style_function=lambda x: style,
                        tooltip=tooltip
                    )
                    g.add_to(m)

                    m.to_streamlit(height=700)
            
            except Exception as e:
                st.error(f"Could not load or process the GeoJSON file at '{geojson_file_path}'. Please ensure it is a valid file.")
                st.error(f"Error details: {e}")


    with uploaded_data:
        st.write("Coming soon...")

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
