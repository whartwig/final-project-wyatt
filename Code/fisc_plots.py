# --- 0. Packages and formatting ---
from os.path import join
import os
from pathlib import Path
import altair as alt
import pandas as pd
import numpy as np
from statsmodels.stats.weightstats import DescrStatsW as dsw
import statsmodels.formula.api as smf

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

def my_theme():
    font = "sans-serif"
    primary_color = "#F63366"
    font_color = "#262730"
    grey_color = "#A8A8A8"
    base_size = 16
    lg_font = base_size * 1.25
    sm_font = base_size * 0.8  # st.table size
    xl_font = base_size * 1.75

    return {
        "config": {
            "mark": {"lineBreak":"\n"},
            "background": '#C0AF97',
            "view": {"fill": grey_color, "stroke": "transparent"},
            "arc": {"fill": primary_color},
            "area": {"fill": primary_color},
            "circle": {"fill": primary_color, "stroke": font_color, "strokeWidth": 0.5},
            "line": {"stroke": primary_color},
            "path": {"stroke": primary_color},
            "point": {"stroke": primary_color},
            "rect": {"fill": primary_color},
            "shape": {"stroke": primary_color},
            "symbol": {"fill": primary_color},
            "title": {
                "font": font,
                "color": font_color,
                "fontSize": lg_font,
                "anchor": "middle",
                "lineBreak": "\n",
                "align": "center",
            },
            "axis": {
                "titleFont": font,
                "titleColor": font_color,
                "titleFontSize": sm_font,
                "labelFont": font,
                "labelColor": font_color,
                "labelFontSize": sm_font,
                "gridColor": "#F2F0EF",
                "domainColor": font_color,
                "tickColor": font_color,
                "lineBreak": "\n",
            },
            "header": {
                "labelFont": font,
                "titleFont": font,
                "labelFontSize": base_size,
                "titleFontSize": base_size,
                "lineBreak": "\n",
                "align": "center"
            },
            "legend": {
                "titleFont": font,
                "titleColor": font_color,
                "titleFontSize": sm_font,
                "labelFont": font,
                "labelColor": font_color,
                "labelFontSize": sm_font,
                "lineBreak": "\n",
            },
            "range": {
                "category": ['#e41a1c', '#377eb8', '#4daf4a', '#984ea3',
                             '#ff7f00', '#ffff33'],
                "diverging": [
                    "#850018",
                    "#cd1549",
                    "#f6618d",
                    "#fbafc4",
                    "#f5f5f5",
                    "#93c5fe",
                    "#5091e6",
                    "#1d5ebd",
                    "#002f84",
                ],
                "heatmap": [
                    "#ffb5d4",
                    "#ff97b8",
                    "#ff7499",
                    "#fc4c78",
                    "#ec245f",
                    "#d2004b",
                    "#b10034",
                    "#91001f",
                    "#720008",
                ],
                "ramp": [
                    "#ffb5d4",
                    "#ff97b8",
                    "#ff7499",
                    "#fc4c78",
                    "#ec245f",
                    "#d2004b",
                    "#b10034",
                    "#91001f",
                    "#720008",
                ],
                "ordinal": [
                    "#ffb5d4",
                    "#ff97b8",
                    "#ff7499",
                    "#fc4c78",
                    "#ec245f",
                    "#d2004b",
                    "#b10034",
                    "#91001f",
                    "#720008",
                ],
            },
        }
    }

alt.themes.register('my_theme', my_theme)
alt.themes.enable('my_theme')

############################################################################



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



# --- 2. SET UP TO PLOT COMPAREABLE CITIES ---

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
    base = alt.Chart(df).transform_fold(
        columns,
        as_=['Metric', 'Value']
    ).mark_bar().encode(
        x=alt.X('Metric:N', title=None, sort=columns, axis=alt.Axis(labelAngle=0)),
        y=alt.Y('Value:Q', title='2022 Dollars'),
        color=alt.Color('city:N', title='City'),
        xOffset='city:N',
        tooltip=['city', 'Metric:N', 'Value:Q']
    )

    footer = alt.Chart({'values': [{}]}).mark_text(
        align="right",
        baseline="top",
        fontSize=10,
        text="Source: 2022 Lincoln Institute Fiscally Standardized Cities Data",
        clip=False  
    ).encode(
        x=alt.value(250), 
        y=alt.value(290)  
    )

    # Combine the charts
    chart = (base + footer).properties(
        width=500,
        height=250,
        title=title 
    )
    
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



#--- 3. SET UP STATS EXPRESSION FOR CONSOLIDATED CITIES ---

fisc_2022 = fisc[fisc['year']==2022]
fisc_2022 = fisc_2022[~fisc_2022['state'].isin(['Average for All Cities','Average for Core FiSCs',
                                               'Median for All Cities', 'Median for Core FiSCs',
                                               'Median for Legacy Cities'])]
fisc_2022 = fisc_2022[~fisc_2022['state'].isna()]
outliers = ['Washington', 'New York']
fisc_2022 = fisc_2022[~fisc_2022['city'].isin(outliers)]


cols_interest = ['debt_outstanding', 'taxes', 'tax_property', 'igr_federal', 'charges',
                 'rev_utility','spending_general', 'public_safety', 'police', 'fire',
                 'administration', 'spending_utility']

summary_df = []
for col in cols_interest:
    # Transform to log to better capture relationships
    fisc_2022[f'{col}_log'] = np.log(fisc_2022[col] + 1) # +1 prevents ln(0) issues
    fisc_2022['pop_log'] = np.log(fisc_2022['city_population'])
    
    # Naive model
    formula = f'{col}_log ~ consolidated_govt + pop_log + C(state)'
    model = smf.ols(formula, data=fisc_2022).fit()
    ci = model.conf_int(alpha=0.05)

    summary_df.append({
    'Variable': col,
    'Coeff': model.params['consolidated_govt'],
    'Standard Error': model.bse['consolidated_govt'],
    't-score': model.tvalues['consolidated_govt'],
    'P>|t|': model.pvalues['consolidated_govt'],
    'ci_lower': ci.loc['consolidated_govt', 0],
    'ci_upper': ci.loc['consolidated_govt', 1]
    })

summary_df = pd.DataFrame(summary_df).sort_values('P>|t|')

# Map to make plot names pretty
label_map = {
    'debt_outstanding': 'Total Outstanding Debt',
    'taxes': 'Total Tax Revenue',
    'tax_property': 'Property Tax Revenue',
    'igr_federal': 'Federal Intergovernmental Revenue',
    'charges': 'Current Charges & Fees',
    'rev_utility': 'Utility Revenue',
    'spending_general': 'General Direct Expenditure',
    'public_safety': 'Total Public Safety Spending',
    'police': 'Police Protection Spending',
    'fire': 'Fire Protection Spending',
    'administration': 'Government Administration Spending',
    'spending_utility': 'Utility Expenditure'}
summary_df['Label'] = summary_df['Variable'].replace(label_map)

# Plot layering
base = alt.Chart(summary_df).encode(
    y=alt.Y('Label:N', sort='-x', title='Financial Category'))
error_bars = base.mark_rule().encode(
    x=alt.X('ci_lower:Q', title='Coefficient (Effect of Consolidated Govt)'),
    x2='ci_upper:Q')
points = base.mark_point(filled=True, size=100, color='black').encode(
    x=alt.X('Coeff:Q'),
    tooltip=['Label', 'Coeff', 'P>|t|'] ) # For HTML
zero_line = alt.Chart(pd.DataFrame({'x': [0]})).mark_rule( # Shows statistical significance
    color='red', 
    strokeDash=[5, 5],
    strokeWidth=3).encode(
    x='x:Q')
footer = alt.Chart({'values': [{}]}).mark_text(
        align="right",
        baseline="top",
        fontSize=10,
        text="Source: 2022 Lincoln Institute Fiscally Standardized Cities Data",
        clip=False
    ).encode(
        x=alt.value(125), 
        y=alt.value(450))

coef_plot = (zero_line + error_bars + points + footer).properties(
    title='Impact of Consolidated Government on Municipal Finance Categories',
    width=600,
    height=400).configure_axis(
    labelFontSize=12,
    titleFontSize=14).configure_title(
    fontSize=16,
    anchor='middle')



# --- 4. DISPLAY PLOTS ---

revenue_chart.display()
spending_chart.display()
general_comp.display()
coef_plot.display()


