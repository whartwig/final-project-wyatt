from os.path import join
import os
from pathlib import Path
import altair as alt
import pandas as pd
import numpy as np
from statsmodels.stats.weightstats import DescrStatsW as dsw
import statsmodels.formula.api as smf
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

cities =  fisc[fisc['city'].isin(['Kansas City', 'St. Louis', 'Average for Core FiSCs',
                                  'San Antonio', 'Columbus', 'Phoenix', 'Hosuton',
                                  'Milwaukee', 'San Jose', 'Consolidated',
                                  'NonConsolidated', 'Nashville', 'Louisville',
                                  'University City'])]

cities_subset = pd.concat([
    cities.loc[:, 'state':'cpi'], 
    cities.loc[:, 'rev_general':'consolidated_govt']
], axis=1)


def plot_fisc_data(df: pd.DataFrame, column: str, title_prefix: str = None):
    if title_prefix is None:
        # Map known columns to readable names used in original functions
        mapping = {
            'debt_outstanding': 'Per Capita Debt',
            'taxes': 'Per Capita Taxes',
            'tax_property': 'Per Capita Property Tax',
            'igr_federal': 'Per Capita Federal Transfers',
            'charges': 'Per Capita Charges',
            'rev_utility': 'Per Capita Utility Costs',
            'spending_general': 'Per Capita Spending'
        }
        title_prefix = mapping.get(column, column.replace('_', ' ').title())
    
    full_title = f"{title_prefix} by Year for Selected US Fiscally Standardized Cities (1977-2022)"
    
    bar_sort = alt.EncodingSortField(field=column, op='sum', order='descending')

    chart = alt.Chart(df).transform_filter('datum.year%5-2==0').mark_bar().encode(
        alt.X('year:O', title=''),
        alt.Y(f'{column}:Q', title='2022 Dollars'),
        alt.Color('city:N', sort=bar_sort),
        alt.XOffset('city:N', sort=bar_sort),
        tooltip=['city', column]
    ).properties(title=full_title).interactive()

    return chart

cities_subset_2022 = cities_subset[cities_subset['year']==2022]
plot_fisc_data(cities_subset_2022, 'debt_outstanding')
plot_fisc_data(cities_subset_2022, 'taxes') 
plot_fisc_data(cities_subset_2022, 'tax_property')
plot_fisc_data(cities_subset_2022, 'igr_federal')
plot_fisc_data(cities_subset_2022, 'charges')
plot_fisc_data(cities_subset_2022, 'rev_utility')
plot_fisc_data(cities_subset_2022, 'spending_general')
plot_fisc_data(cities_subset_2022, 'public_safety', 'Per Capita Public Saftey Spend')
plot_fisc_data(cities_subset_2022, 'police', 'Per Capita Police Spending')
plot_fisc_data(cities_subset_2022, 'fire', 'Per Cpaita Fire Spending')
plot_fisc_data(cities_subset_2022, 'administration', 'Per Capita Admin Costs')
plot_fisc_data(cities_subset_2022, 'spending_utility', 'Per Capita Utility Spend')




fisc_2022 = fisc[fisc['year']==2022]
fisc_2022 = fisc_2022[~fisc_2022['city'].isin(['Washington', 'New York', 'Los Angeles',
                                             'Chicago', 'Houston', 'San Francisco', 'Oakland'])]
chart = alt.Chart(fisc_2022).mark_point().encode(
    alt.X('city_population'),
    alt.Y('igr_federal'),
    tooltip = ['city']
)
chart + chart.transform_regression('city_population', 'igr_federal').mark_line()




cols_interest = ['debt_outstanding', 'taxes', 'tax_property', 'igr_federal', 'charges',
                 'rev_utility','spending_general', 'public_safety', 'police', 'fire',
                 'administration', 'spending_utility']
summary_df = []
for col in cols_interest:
    model = smf.ols(f'{col} ~ consolidated_govt + city_population + C(state)', data=fisc_2022).fit()
    
    summary_df.append({
    'Variable': col,
    'Coeff': model.params['consolidated_govt'],
    'Standard Error': model.bse['consolidated_govt'],
    't-score': model.tvalues['consolidated_govt'],
    'P>|t|': model.pvalues['consolidated_govt']
    })
summary_df = pd.DataFrame(summary_df).sort_values('P>|t|')
summary_df