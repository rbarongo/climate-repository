import os
import sys

root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_dir)

import pandas as pd
import streamlit as st
import folium
import leafmap.foliumap as leafmap
import geopandas as gpd
from .utils import stringify_currency


@st.cache_data
def load_location_data():

    try:
        df = pd.read_csv("map_data/admin_names.csv")
        return df
    except FileNotFoundError:
        return pd.DataFrame(columns=['Region_Nam', 'Dist_Nam', 'Ward_Nam', 'Village_Na'])


def get_regions(df):
    if 'Region_Nam' in df.columns:
        return sorted(df['Region_Nam'].dropna().unique().tolist())
    return []


def get_districts(df, region):
    if 'Dist_Nam' in df.columns and region:
        return sorted(df[df['Region_Nam'] == region]['Dist_Nam'].dropna().unique().tolist())
    return []


def get_wards(df, district):
    if 'Ward_Nam' in df.columns and district:
        return sorted(df[df['Dist_Nam'] == district]['Ward_Nam'].dropna().unique().tolist())
    return []


def get_street(df, ward):
    if 'Village_Na' in df.columns and ward:
        return sorted(df[df['Ward_Nam'] == ward]['Village_Na'].dropna().unique().tolist())
    return []


def populate_map(df):
    initial_df = df.copy()

    if initial_df.empty:
        st.warning("No data available to display on the map.")
    else:
        initial_df['is_doubtful'] = (initial_df['asset_classification'] == 'Doubtful').astype(int)

        district_summary = initial_df.groupby('loan_district').agg(
            total_disbursed=('tzs_disbursed_amount', 'sum'),
            total_collateral=('collateral_market_value', 'sum'),
            doubtful_count=('is_doubtful', 'sum')
        ).reset_index()

        # Aggregate by Region
        region_summary = initial_df.groupby('loan_region').agg(
            total_disbursed=('tzs_disbursed_amount', 'sum'),
            total_collateral=('collateral_market_value', 'sum'),
            doubtful_count=('is_doubtful', 'sum')
        ).reset_index()

        regions_geojson_path = 'map_data/regions.geojson'
        districts_geojson_path = 'map_data/districts.geojson'

        region_key_col = 'reg_name'
        district_key_col = 'dist_name'

        try:
            gdf_regions = gpd.read_file(regions_geojson_path)
            gdf_districts = gpd.read_file(districts_geojson_path)

            merged_gdf_regions = gdf_regions.merge(region_summary, left_on=region_key_col, right_on='loan_region',
                                                   how='left').fillna(0)

            merged_gdf_regions['total_disbursed_str'] = merged_gdf_regions['total_disbursed'].apply(stringify_currency)
            merged_gdf_regions['total_collateral_str'] = merged_gdf_regions['total_collateral'].apply(stringify_currency)

            merged_gdf_districts = gdf_districts.merge(district_summary, left_on=district_key_col,
                                                       right_on='loan_district', how='left').fillna(0)
            merged_gdf_districts['total_disbursed_str'] = merged_gdf_districts['total_disbursed'].apply(stringify_currency)
            merged_gdf_districts['total_collateral_str'] = merged_gdf_districts['total_collateral'].apply(
                stringify_currency)

            m = leafmap.Map(center=[-6.3690, 34.8888], zoom=6, tiles="CartoDB positron")

            regions_with_no_data = merged_gdf_regions[merged_gdf_regions['total_disbursed'] == 0]
            folium.GeoJson(
                regions_with_no_data,
                style_function=lambda x: {"fillColor": "#D3D3D3", "color": "#808080", "weight": 1, "fillOpacity": 0.7},
                tooltip="No loan data available for this region",
                name="Regions (No data)"
            ).add_to(m)

            choro_regions = folium.Choropleth(
                geo_data=merged_gdf_regions[merged_gdf_regions['total_disbursed'] > 0],
                data=merged_gdf_regions,
                columns=[region_key_col, 'total_disbursed'],
                key_on=f'feature.properties.{region_key_col}',
                fill_color='YlOrRd',
                fill_opacity=0.7,
                line_opacity=0.2,
                bins=4,
                # legend_name='Total Disbursed Loan (TZS) by Region',
                name='Regions View',
                show=True,
            )

            region_tooltip = folium.GeoJsonTooltip(
                fields=['loan_region', 'total_disbursed_str', 'total_collateral_str', 'doubtful_count'],
                aliases=['Region:', 'Total Disbursed:', 'Total Collateral Value:', '# of Doubtful Loans:'],
                localize=True, sticky=False
            )

            tooltip_with_no_data = folium.GeoJsonTooltip(
                fields=['loan_region'],
                aliases=['Region:'],
                localize=True, sticky=False
            )

            choro_regions.geojson.add_child(region_tooltip)
            choro_regions.add_to(m)

            districts_with_no_data = merged_gdf_districts[merged_gdf_districts['total_disbursed'] == 0]
            folium.GeoJson(
                districts_with_no_data,
                style_function=lambda x: {"fillColor": "#D3D3D3", "color": "#808080", "weight": 1, "fillOpacity": 0.7},
                tooltip=["No loan data available for this district"],
                name='Districts (No Data)',
                show=False
            ).add_to(m)

            # Choropleth for districts WITH data
            choro_districts = folium.Choropleth(
                geo_data=merged_gdf_districts[merged_gdf_districts['total_disbursed'] > 0],
                data=merged_gdf_districts,
                columns=[district_key_col, 'total_disbursed'],
                key_on=f'feature.properties.{district_key_col}',
                fill_color='BuPu',
                fill_opacity=0.7,
                line_opacity=0.2,
                bins=4,
                name='Districts View',
                show=False,
            )

            district_tooltip = folium.GeoJsonTooltip(
                fields=['loan_district', 'total_disbursed_str', 'total_collateral_str', 'doubtful_count'],
                aliases=['District:', 'Total Disbursed:', 'Total Collateral Value:', '# of Doubtful Loans:'],
                localize=True, sticky=False
            )
            choro_districts.geojson.add_child(district_tooltip)
            choro_districts.add_to(m)

            folium.LayerControl().add_to(m)

            # Render the map
            m.to_streamlit(height=700)

        except Exception as e:
            st.error(
                f"An error occurred while building the map. Please ensure GeoJSON files and key columns are correct.")
            st.error(f"Details: {e}")

