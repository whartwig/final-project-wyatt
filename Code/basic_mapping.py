from itertools import count
from math import nan
import pandas as pd
import matplotlib.pyplot as plt
import os
from pathlib import Path
import pip
import seaborn as sns
import geopandas as gpd
import json
import pyproj
from pyproj import CRS
from pyproj import Proj
from shapely import Point, LineString, Polygon
from shapely.geometry import linestring
import numpy as np
import folium as fol
from folium.plugins import MarkerCluster

# os.chdir('C:\Users\wyatt\student30538-w26\final-project-whartwig')
base_dir = Path(__file__).resolve().parent.parent
path_raw_data = os.path.join(base_dir, 'data', 'raw-data')
path_cleaned_data = os.path.join(base_dir, 'data', 'derived-data')

# # Read in cleaned files
stl_tracts = gpd.read_file(os.path.join(path_cleaned_data, 'all_tracts.geojson'))
stl_select = gpd.read_file(os.path.join(path_cleaned_data, 'newstl_tracts.geojson'))
newstl = gpd.read_file(os.path.join(path_cleaned_data, 'newstl_dis.geojson'))
newcounty = gpd.read_file(os.path.join(path_cleaned_data,'county_minus_newstl.geojson'))
county_all = gpd.read_file(os.path.join(path_cleaned_data, 'county_plus_newstl.geojson'))
# stl_tracts


# --- Mapping ---

# ## Base map
# All cencus tracts in current STL City/County
all_tracts = fol.Map(location = [38.625029, -90.186772], tiles='cartodb positron', zoom_start = 10)
fol.GeoJson(stl_tracts, tooltip=fol.GeoJsonTooltip(fields=['COUNTY', 'TRACT', 'Total Population']),
            popup=fol.GeoJsonPopup(fields=['COUNTY', 'TRACT', 'Total Population', 'DENSITY']),
            style_function=lambda x: {'fillColor':'blue', 'color':'black', 'weight': 1,
                                      'fillOpacity': 0.1,}).add_to(all_tracts)
# all_tracts


# ## New city cencus tracts
# Proposed City in new St. Louis County by Census Tract
new_stl = fol.Map(location = [38.625029, -90.186772], tiles='cartodb positron', zoom_start = 10)
fol.GeoJson(stl_select, tooltip=fol.GeoJsonTooltip(fields=['COUNTY', 'TRACT', 'Total Population']),
            popup=fol.GeoJsonPopup(fields=['COUNTY', 'TRACT', 'Total Population', 'DENSITY']),
            style_function=lambda x: {'fillColor':'blue', 'color':'black', 'weight': 1,
                                      'fillOpacity': 0.1,}).add_to(new_stl)
# new_stl

# ## New city and county
# New St. Louis City and County Boundry and Stats
stl_next = fol.Map(location = [38.625029, -90.186772], tiles='cartodb positron', zoom_start = 10)
fol.GeoJson(newstl, name='New St. Louis', tooltip=fol.GeoJsonTooltip(fields=['NAME']),
            popup=fol.GeoJsonPopup(fields=['NAME', 'Total Population', 'SQMI', 'DENSITY']),
            style_function=lambda x: {'fillColor':'blue', 'color':'black', 'weight': 1,
                                      'fillOpacity': 0.1,}).add_to(stl_next)
fol.GeoJson(newcounty, name='New County Without St. Louis',
            tooltip=fol.GeoJsonTooltip(fields=['NAME']),
            popup=fol.GeoJsonPopup(fields=['NAME', 'Total Population', 'SQMI']),
            style_function=lambda x: {'fillColor':'red', 'color':'black', 'weight': 1,
                                      'fillOpacity': 0.1,}).add_to(stl_next)
fol.GeoJson(county_all, name='New County with St. Louis',
            tooltip=fol.GeoJsonTooltip(fields=['NAME']),
            popup=fol.GeoJsonPopup(fields=['NAME', 'Total Population', 'SQMI']),
            style_function=lambda x: {'fillColor':'orange', 'color':'black', 'weight': 1,
                                      'fillOpacity': 0.1,}).add_to(stl_next)
fol.LayerControl().add_to(stl_next)

stl_next
