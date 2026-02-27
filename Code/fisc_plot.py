# --- 0. Packages and formatting ---
from os.path import join
import os
from pathlib import Path
import altair as alt
import pandas as pd
import numpy as np
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



# --- 1. Load and alter fisc data for analysis and plotting ---

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
    # Don't want the weight column in the calculation
    numeric_cols = group.select_dtypes(include='number').drop(columns=['city_population'])
    stats = dsw(numeric_cols, weights=group['city_population'])
    return pd.Series(stats.mean, index=numeric_cols.columns)

# Apply get_weighted_means to the groupby dataframe
weighted_fisc_data = fisc.groupby(['year', 'consolidated_govt']).apply(get_weighted_means).drop(columns=['consolidated_govt', 'year']).reset_index()
weighted_fisc_data['city'] = np.where(weighted_fisc_data['consolidated_govt']==0,
                                      'NonConsolidated', 'Consolidated')
fisc = pd.concat([fisc, weighted_fisc_data])
fisc



# --- 2. Plotting ---

# Craft subset data for plotting
cities =  fisc = fisc[fisc['year']==2022]
cities = fisc[fisc['city'].isin(['St. Louis', 'University City', 'Consolidated',
                                 'NonConsolidated', 'Louisville'])]
cities_subset = pd.concat([
    cities.loc[:, 'state':'cpi'], 
    cities.loc[:, 'rev_general':'consolidated_govt']
], axis=1)

# Plot metrics on x-axis across cities of interest
def plot_fisc_comparison(df: pd.DataFrame, columns: list, title: str):
    chart = alt.Chart(df).transform_fold(
        columns,
        as_=['Metric', 'Value']
    ).mark_bar().encode(
        alt.X('Metric:N', title=None, sort=columns),
        alt.Y('Value:Q', title='2022 Dollars'),
        color=alt.Color('city:N', title='City'),
        xOffset='city:N',
        tooltip=['city', 'Metric:N', 'Value:Q']
    ).properties(
        title=title,
        width=alt.Step(40)
    ).interactive()

    return chart

rename_dict = {'taxes': 'All Taxes',
               'tax_property':'Property Tax',
               'igr_federal':'Federal Transfers',
               'charges':'Charges', 'police':'Police',
               'fire':'Fire', 'public_safety':'Public Safety',
               'administration':'Administration',
               'spending_utility':'Utility Spending',
               'debt_outstanding':'Outstanding Debt',
               'spending_general':'General Spending'}
cities_subset.rename(columns=rename_dict, inplace=True)

# Comparison of various revenue sources
revenue_metrics = ['All Taxes', 'Property Tax', 'Federal Transfers', 'Charges']
revenue_chart = plot_fisc_comparison(cities_subset, revenue_metrics, 'Per Capita Revenue Sources (2022)')

# Comparison of spending categories
spending_metrics = ['Police', 'Fire', 'Administration', 'Utility Spending']
spending_chart = plot_fisc_comparison(cities_subset, spending_metrics, 'Per Capita Spending Categories (2022)')

# Broad comparison
general_comp = plot_fisc_comparison(cities_subset, ['Outstanding Debt', 'General Spending'], 'Debt vs General Spending (2022)')


revenue_metrics.display()
spending_chart.display()
general_comp.display()