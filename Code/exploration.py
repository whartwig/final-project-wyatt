import geopandas as gpd
from os.path import join
import os
from pathlib import Path
import altair as alt
import pandas as pd
import numpy as np
import time
import folium as fol
from statsmodels.stats.weightstats import DescrStatsW as dsw
#os.chdir('C:\\Users\\wyatt\\student30538-w26\\final-project-whartwig')
base_dir = Path(__file__).resolve().parent.parent
path_raw_data = os.path.join(base_dir, 'data', 'raw-data')
path_cleaned_data = os.path.join(base_dir, 'data', 'derived-data')

# improve graph resolution
import tempfile
from IPython.display import SVG, display, Image
import vl_convert as vlc

import warnings 
warnings.filterwarnings('ignore')
#alt.renderers.enable("png")
alt.data_transformers.disable_max_rows()

#This function will work with (alt.Chat + alt.Chart) as well
def display_to_pdf(altchart, scale=2):
    png_bytes = vlc.vegalite_to_png(altchart.to_dict(), scale=scale)
    display(Image(png_bytes))


############################################################################3

stl_munis = gpd.read_file(os.path.join(path_raw_data,
                                       'Municipal_Boundaries.geojson'))
stl_munis['last_edited_date'] = stl_munis['last_edited_date'].astype(str)
stl_munis['MUNICIPALITY'] = stl_munis['MUNICIPALITY'].str.title()
stl_munis = stl_munis[stl_munis['MUNICIPALITY']!='Unincorporated']
stl_munis

stl_munis_demos = pd.read_csv(os.path.join(path_raw_data, 'stl_demographics_manual.csv'))
stl_munis_demos['MUNICIPALITY'] = stl_munis_demos['MUNICIPALITY'].str.title()
stl_munis_merged = stl_munis.merge(stl_munis_demos, on='MUNICIPALITY')

stl_munis_merged


munis = fol.Map(location = [38.625029, -90.186772], tiles='cartodb positron', zoom_start = 10)
fol.GeoJson(stl_munis, name='St. Louis Area Municipalities',
            tooltip=fol.GeoJsonTooltip(fields=['MUNICIPALITY']),
            popup=fol.GeoJsonPopup(fields=['MUNICIPALITY']),
            style_function=lambda x: {'fillColor':'blue', 'color':'black', 'weight': 1,
                                      'fillOpacity': 0.1,}).add_to(munis)
fol.GeoJson(stl_munis_merged, name='St. Louis Area Municipalities',
            tooltip=fol.GeoJsonTooltip(fields=['MUNICIPALITY']),
            popup=fol.GeoJsonPopup(fields=['MUNICIPALITY', 'POPULATION', 'DENSITY SQMI']),
            style_function=lambda x: {'fillColor':'orange', 'color':'black', 'weight': 1,
                                      'fillOpacity': 0.4,}).add_to(munis)
fol.LayerControl().add_to(munis)
munis





fisc = pd.read_csv(os.path.join(path_raw_data, 'fisc_data.csv'))
fisc[['state', 'city']] = fisc['city_name'].str.split(':', n=1, expand=True)
fisc['city'] = fisc['city'].str.strip()
fisc['state'] = fisc['state'].str.strip()
cols_to_move = ['state', 'city']
new_order = cols_to_move + [c for c in fisc.columns if c not in cols_to_move]
fisc = fisc[new_order]
fisc['city'] = np.where(fisc['state']=='Average for Core FiSCs', fisc['state'], fisc['city'])
fisc.drop('city_name', axis=1, inplace=True)

def get_weighted_means(group: pd.DataFrame):
    # Drop the weight column itself
    numeric_cols = group.select_dtypes(include='number').drop(columns=['city_population'])
    stats = dsw(numeric_cols, weights=group['city_population'])
    return pd.Series(stats.mean, index=numeric_cols.columns)

# Apply the custom function to your grouped data
weighted_fisc_data = fisc.groupby(['year', 'consolidated_govt']).apply(get_weighted_means).drop(columns=['consolidated_govt', 'year']).reset_index()
weighted_fisc_data['city'] = np.where(weighted_fisc_data['consolidated_govt']==0,
                                      'NonConsolidated', 'Consolidated')
fisc = pd.concat([fisc, weighted_fisc_data])
fisc

kc = fisc[fisc['city']=='Kansas City']
#[['city', 'year', 'city_population']]
cities =  fisc[fisc['city'].isin(['Kansas City', 'St. Louis', 'Average for Core FiSCs',
                                  'San Antonio', 'Columbus', 'Phoenix', 'Hosuton',
                                  'Milwaukee', 'San Jose', 'Consolidated',
                                  'NonConsolidated', 'Nashville'])]

def plot_debt(df: pd.DataFrame):
    bar_sort = alt.EncodingSortField(field='debt_outstanding', op='sum',
                                     order='descending')

    debt = alt.Chart(df).transform_filter('datum.year%5-2==0').mark_bar().encode(
        alt.X('year:O', title=''),
        alt.Y('debt_outstanding:Q', title='2022 Dollars'),
        alt.Color('city:N', sort=bar_sort),
        alt.XOffset('city:N', sort=bar_sort),
        tooltip = ['city', 'debt_outstanding']
    ).properties(title='Per Capita Debt by Year for Selected US Fiscally Standardized Cities (1977-2022)').interactive()

    return debt
plot_debt(cities)

len(fisc[fisc['consolidated_govt']==1]['city'].unique())

plot_debt(fisc[fisc['city'].isin(fisc[fisc['consolidated_govt']==1]['city'].unique())])







stl_tracts = gpd.read_file(os.path.join(path_cleaned_data, 'all_tracts.geojson'))
stl_select = gpd.read_file(os.path.join(path_cleaned_data, 'newstl_tracts.geojson'))
newstl = gpd.read_file(os.path.join(path_cleaned_data, 'newstl_dis.geojson'))
newcounty = gpd.read_file(os.path.join(path_cleaned_data,'county_minus_newstl.geojson'))
county_all = gpd.read_file(os.path.join(path_cleaned_data, 'county_plus_newstl.geojson'))

m = fol.Map(location = [38.625029, -90.186772], tiles='cartodb positron', zoom_start = 10)
fol.GeoJson(county_all,
            style_function=lambda x: {'fillColor':'blue', 'color':'black', 'weight': 1,
                                      'fillOpacity': 0.1,}).add_to(m)
m