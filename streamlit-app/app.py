# --- 0. PACKAGES ---
import streamlit as st
import pandas as pd
import numpy as np
import geopandas as gpd
import folium as fol
from streamlit_folium import st_folium
import os
from pathlib import Path


# --- 1. SETUP ---
st.set_page_config(layout="wide", page_title="St. Louis Municipal Consolidation Dashboard")

base_dir = Path(__file__).resolve().parent.parent
path_cleaned_data = os.path.join(base_dir, 'data', 'derived-data')
path_raw_data = os.path.join(base_dir, 'data', 'raw-data')


# Cache data loading for performance
@st.cache_data
def load_geojson(path_dir, filename):
    path = os.path.join(path_dir, filename)
    if not os.path.exists(path):
        return None
    gdf = gpd.read_file(path)
    
    # Convert any datetime columns to strings to avoid JSON serialization errors
    for col in gdf.columns:
        if pd.api.types.is_datetime64_any_dtype(gdf[col]):
            gdf[col] = gdf[col].astype(str)
            
    return gdf

# Load datasets
all_tracts = load_geojson(path_cleaned_data, 'all_tracts.geojson')
newstl_dis = load_geojson(path_cleaned_data, 'newstl_dis.geojson')
newstl_tracts = load_geojson(path_cleaned_data, 'newstl_tracts.geojson')
county_plus_newstl = load_geojson(path_cleaned_data, 'county_plus_newstl.geojson')
munis_merged = load_geojson(path_cleaned_data, 'munis_merged.geojson')

@st.cache_data
def get_current_city_boundary(_gdf):
    city_gdf = _gdf[_gdf['COUNTY'] == 'St. Louis city'].copy()
    city_gdf['DISID'] = 1
    # Dissolve to get just the outer boundary
    return city_gdf.dissolve(by='DISID')

if all_tracts is not None:
    cur_city_dis = get_current_city_boundary(all_tracts)
else:
    cur_city_dis = None

# --- 2. SIDEBAR NAVIGATION ---
st.sidebar.title("Navigation")
page = st.sidebar.radio("Select View", ["Regional Density Analysis", "Municipal Comparison", "Critical Infrastructure"])

# --- 3. PAGE: REGIONAL DENSITY ANALYSIS ---
if page == "Regional Density Analysis":
    # --- HEADER ---
    st.title("St. Louis Region: Reimagining Municipal Boundaries")
    st.markdown("""
    This dashboard explores the impact of redefining St. Louis city boundaries based on census tract density 
    and merging the city with St. Louis County. 
    Use the sidebar to toggle between different geographic layers and demographic views.
    """)

    # --- SIDEBAR CONTROLS ---
    st.sidebar.header("Map Controls")

    # Layer Toggles
    show_all_tracts = st.sidebar.checkbox("Show All Census Tracts", value=True)
    show_newstl_border = st.sidebar.checkbox("Show Proposed 'New St. Louis' Boundary", value=True)
    show_cur_city_border = st.sidebar.checkbox("Show Current St. Louis City Boundary", value=True)

    # Demographic Selector for Choropleth
    demo_col = st.sidebar.selectbox(
        "Select Demographic Variable for Tract View",
        options=["DENSITY", "Median Household Income", "Total Population", "Proportion Black",
                 "Proportion White", "Home Ownership Rate", 'Less than High School',
                 'High School', "Associate's Degree", "Bachelor's Degree", 
                 "Master's Degree or Higher"],
        index=0
    )

    # --- MAP RENDERING ---
    # Center the map on St. Louis
    m = fol.Map(location=[38.64293421087117, -90.32506114168913], zoom_start=10, tiles='cartodb positron')

    # Add All Tracts with Choropleth logic
    if show_all_tracts and all_tracts is not None:
        # Fill NA for choropleth
        plot_df = all_tracts.copy()
        # Handle cases where the demo_col might not match exactly due to previous renames
        if demo_col == "Median Household Income" and "Median HHI" in plot_df.columns:
            target_col = "Median HHI"
        else:
            target_col = demo_col
            
        plot_df[target_col] = plot_df[target_col].fillna(0)
        
        fol.Choropleth(
            geo_data=plot_df,
            name="Census Tracts",
            data=plot_df,
            columns=['TRACT', target_col],
            key_on="feature.properties.TRACT",
            fill_color="YlGnBu",
            fill_opacity=0.7,
            line_opacity=0.2,
            legend_name=demo_col,
        ).add_to(m)
        
        # Add tooltips
        fol.GeoJson(
            plot_df,
            style_function=lambda x: {'fillColor': 'transparent',
                                      'color': 'transparent'},
            tooltip=fol.GeoJsonTooltip(
                fields=['TRACT', 'COUNTY', target_col],
                aliases=['Tract:', 'County:', f'{demo_col}:'],
                localize=True
            )
        ).add_to(m)

    # Add New St. Louis Dissolved Boundary
    if show_newstl_border and newstl_dis is not None:
        fol.GeoJson(
            newstl_dis,
            name="Proposed New St. Louis",
            style_function=lambda x: {
                'fillColor': 'none',
                'color': '#ff4b4b',
                'weight': 4,
                'dashArray': '5, 5'
            }
        ).add_to(m)

    # Add Current STL Boundary
    if show_cur_city_border and cur_city_dis is not None:
        fol.GeoJson(
            cur_city_dis,
            name="Current City",
            style_function=lambda x: {
                'fillColor': 'none',
                'color': '#2c3e50',
                'weight': 3
            }
        ).add_to(m)

    # Display Map
    st_folium(m, width=1000, height=600)

    # --- SUMMARY STATISTICS ---
    st.subheader("Regional Summary Statistics")
    col1, col2, col3 = st.columns(3)

    if all_tracts is not None:
        with col1:
            old_city_pop = all_tracts[all_tracts['COUNTY'] == 'St. Louis city']['Total Population'].sum()
            st.metric("Current City Population", f"{old_city_pop:,.0f}")

        with col2:
            new_city_pop = newstl_tracts['Total Population'].sum() if newstl_tracts is not None else 0
            st.metric("Proposed 'New St. Louis' Population", f"{new_city_pop:,.0f}")

        with col3:
            county_pop = county_plus_newstl['Total Population'].sum() if county_plus_newstl is not None else 0
            st.metric("Total Regional Population", f"{county_pop:,.0f}")

    st.info("The 'New St. Louis' boundary is defined by census tracts with a density ≥ 3,600 people/sq mi, adjusted for contiguity.")

# --- 4. PAGE: MUNICIPAL COMPARISON ---
elif page == "Municipal Comparison":
    st.title("Municipal Comparison: Financial and Demographic Insights")
    st.markdown("""
    Explore fiscal and demographic data across individual municipalities in St. Louis County and the City. 
    Use the dropdown to change the variable displayed on the map.
    """)

    if munis_merged is not None:
        # Variable Selector
        muni_demo_col = st.sidebar.selectbox(
            "Select Municipal Variable",
            options=[
                'Population',
                'Year Incorporated', 
                'Median Household Income', 
                'Percent Black', 
                'Per Capita Admin Cost (winsorized)',
                'Total Revenue Per Capita (winsorized)',
                'Sales Tax Revenue Per Capita (winsorized)',
                'Property Tax Revenue Per Capita (winsorized)',
                'Utility Tax Revenue Per Capita (winsorized)',
                'Court Fines Revenue Per Capita (winsorized)',
                'Total Expenditures Per Capita (winsorized)',
                'Elected Officials Per 50,000 People (winsorized)'
            ],
            index=4
        )

        # Prepare data
        muni_plot_df = munis_merged.copy()
        
        # Filter out STL County for Population view as it skews the scale significantly
        if muni_demo_col == "Population":
            muni_plot_df = muni_plot_df[muni_plot_df['Municipality'] != 'STL County']
            muni_plot_df = muni_plot_df[muni_plot_df['Municipality'] != 'Saint Louis City']
        
        # Special handling for Year Incorporated if it's a string like "1950" or contains non-numeric
        if muni_demo_col == "Year Incorporated":
            muni_plot_df[muni_demo_col] = pd.to_numeric(muni_plot_df[muni_demo_col], errors='coerce').fillna(0)
        
        muni_plot_df[muni_demo_col] = muni_plot_df[muni_demo_col].fillna(0)

        # Map Rendering
        m_muni = fol.Map(location=[38.64293421087117, -90.32506114168913], zoom_start=10, tiles='cartodb positron')

        fol.Choropleth(
            geo_data=muni_plot_df,
            name="Municipalities",
            data=muni_plot_df,
            columns=['Municipality', muni_demo_col],
            key_on="feature.properties.Municipality",
            fill_color="OrRd",
            fill_opacity=0.7,
            line_opacity=0.2,
            legend_name=muni_demo_col,
        ).add_to(m_muni)

        # Tooltips
        fol.GeoJson(
            muni_plot_df,
            style_function=lambda x: {'fillColor': 'transparent', 'color': 'transparent'},
            tooltip=fol.GeoJsonTooltip(
                fields=['Municipality', 'Classification', muni_demo_col, 'Population'],
                aliases=['Municipality:', 'Class:', f'{muni_demo_col}:', 'Population:'],
                localize=True
            )
        ).add_to(m_muni)

        st_folium(m_muni, width=1000, height=600)
        
        st.subheader("Municipal Data Table")
        # Display all columns from options plus Municipality and Classification
        display_cols = ['Municipality', 'Classification'] + [
            'Population', 'Year Incorporated', 'Median Household Income', 'Percent Black'
        ]
        # Filter to only columns that actually exist in the dataframe
        actual_display_cols = [c for c in display_cols if c in munis_merged.columns]
        st.dataframe(munis_merged[actual_display_cols].sort_values('Municipality'))
    else:
        st.error("Municipal data (munis_merged.geojson) not found. Please run the data cleaning script.")

# --- 5. PAGE: CRITICAL INFRASTRUCTURE ---
elif page == "Critical Infrastructure":
    st.title("Critical Infrastructure: Assets and Services")
    st.markdown("""
    This view overlays critical infrastructure assets including police, fire, bus, and metro services 
    onto the current and proposed regional boundaries.
    """)

    st.sidebar.header("Infrastructure Toggles")
    show_econ = st.sidebar.checkbox("Economic Assets", value=True)
    show_police = st.sidebar.checkbox("Police Stations", value=False)
    show_fire_stat = st.sidebar.checkbox("STL Fire Stations", value=False)
    show_fire_dist = st.sidebar.checkbox("County Fire Districts", value=True)
    show_metro_stations = st.sidebar.checkbox("Metro Stations", value=False)
    show_metro_routes = st.sidebar.checkbox("Metro Routes", value=False)
    show_bus_stations = st.sidebar.checkbox("Bus Stations", value=False)
    show_bus_routes = st.sidebar.checkbox("Bus Routes", value=False)

    # Base Map
    m_infra = fol.Map(location=[38.64293421087117, -90.32506114168913], zoom_start=11, tiles='cartodb positron')

    # Add Boundaries for Context
    if cur_city_dis is not None:
        fol.GeoJson(cur_city_dis, name="Current City", style_function=lambda x: {'fillColor': 'none', 'color': '#2c3e50', 'weight': 2}).add_to(m_infra)
    if newstl_dis is not None:
        fol.GeoJson(newstl_dis, name="Proposed New STL", style_function=lambda x: {'fillColor': 'none', 'color': '#ff4b4b', 'weight': 3, 'dashArray': '5, 5'}).add_to(m_infra)

    # Load and Add Infrastructure Layers
    if show_econ:
        econ = load_geojson(path_cleaned_data, 'stl_econ.geojson')
        if econ is not None:
            fol.GeoJson(
                econ, 
                name="Economic Assets",
                marker=fol.Marker(icon=fol.Icon(color='orange', icon='briefcase', prefix='fa')),
                tooltip=fol.GeoJsonTooltip(
                    fields=['Asset Name', 'Asset Type'],
                    aliases=['Name:', 'Type:'],
                    localize=True
                )
            ).add_to(m_infra)

    if show_police:
        police = load_geojson(path_raw_data, 'police.geojson')
        if police is not None:
            fol.GeoJson(police,
                        name="Police Stations",
                        marker=fol.Marker(icon=fol.Icon(color='blue',
                                                        icon='shield',
                                                        prefix='fa'))).add_to(m_infra)

    if show_fire_stat:
        fire_stat = load_geojson(path_raw_data, 'stl_firestat.geojson')
        if fire_stat is not None:
            fol.GeoJson(fire_stat, 
                        name="STL Fire Stations",
                        marker=fol.Marker(icon=fol.Icon(color='red',
                                                        icon='fire',
                                                        prefix='fa'))).add_to(m_infra)

    if show_fire_dist:
        fire_dist = load_geojson(path_raw_data, 'stlc_firedist.geojson')
        if fire_dist is not None:
            fol.GeoJson(fire_dist,
                        name="County Fire Districts",
                        style_function=lambda x: {'fillColor': 'red', 'color': 'black', 'weight': 1, 'fillOpacity': 0.1}).add_to(m_infra)

    if show_metro_routes:
        metro_routes = load_geojson(path_raw_data, 'routes_metro.geojson')
        if metro_routes is not None:
            fol.GeoJson(metro_routes,
                        name="Metro Routes",
                        style_function=lambda x: {'color': '#007bff', 'weight': 4}).add_to(m_infra)

    if show_metro_stations:
        metro_stations = load_geojson(path_raw_data, 'stations_metro.geojson')
        if metro_stations is not None:
            fol.GeoJson(metro_stations,
                        name="Metro Stations",
                        marker=fol.CircleMarker(radius=5,
                                                color='white',
                                                fill=True,
                                                fill_color='#007bff',
                                                fill_opacity=1)).add_to(m_infra)

    if show_bus_routes:
        bus_routes = load_geojson(path_raw_data, 'routes_bus.geojson')
        if bus_routes is not None:
            fol.GeoJson(bus_routes,
                        name="Bus Routes",
                        style_function=lambda x: {'color': '#28a745', 'weight': 2, 'opacity': 0.5}).add_to(m_infra)

    if show_bus_stations:
        bus_stations = load_geojson(path_raw_data, 'stations_bus.geojson')
        if bus_stations is not None:
            # For bus stations, we use CircleMarkers due to high volume
            for idx, row in bus_stations.iterrows():
                if row.geometry.type == 'Point':
                    fol.CircleMarker(location=[row.geometry.y, row.geometry.x], radius=2, color='#28a745', fill=True).add_to(m_infra)

    st_folium(m_infra, width=1000, height=700)
    st.info("Transit and emergency service assets are shown relative to the proposed 'New St. Louis' boundary.")
