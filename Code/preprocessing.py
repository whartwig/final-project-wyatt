# --- 0. PACKAGES AND SETUP ---
import pandas as pd
import numpy as np
import os
from pathlib import Path
import geopandas as gpd
import censusdata
from census import Census

# os.chdir('C:\Users\wyatt\student30538-w26\final-project-whartwig')
base_dir = Path(__file__).resolve().parent.parent
path_raw_data = os.path.join(base_dir, 'data', 'raw-data')
path_cleaned_data = os.path.join(base_dir, 'data', 'derived-data')

# The below code will take the .shp and its dependencies to convert to a more usable .geojson file type. 
o_data = gpd.read_file(os.path.join(path_raw_data, 'census_tracts.shp'))
stl_tracts = o_data[(o_data['NAMELSADCO']=='St. Louis County') | (o_data['NAMELSADCO']=='St. Louis city')]
stl_tracts = gpd.GeoDataFrame(stl_tracts).set_crs('EPSG:4326')
stl_tracts.to_file(os.path.join(path_cleaned_data, 'stl_tracts.geojson'), driver='GeoJSON')



# Below, I am processing the converted files and preparing them for later merging. 
# The last line takes the city and county demogrpahics, concatinating into one dataset 
# for easier manipulation.
stl_tracts = gpd.read_file(os.path.join(path_cleaned_data, 'stl_tracts.geojson'))
stl_tracts = gpd.GeoDataFrame(stl_tracts[['COUNTYFP', 'NAME', 'NAMELSADCO', 'ALAND',
                                          'AWATER', 'geometry']])



# --- 1. PULL CENSUS DATA AND CLEAN ---

# 1. To run this code replace the below code with your API key
my_census_api = ''
c = Census("baa1b6b805c1bab4f4f8f32b5eb3958fb8ac3ce8")

# 2. Define the exact variables we need
variables = (
    'NAME',
    'B01003_001E',  # Total Pop
    'B19013_001E',  # Median HHI
    'B19013A_001E', # Median HHI White
    'B19013B_001E', # Median HHI Black
    'B15003_001E',  # Education Total
    'B15003_017E', 'B15003_018E', # High School & GED
    'B15003_021E',  # Associate's
    'B15003_022E',  # Bachelor's
    'B15003_023E', 'B15003_024E', 'B15003_025E', # Master's, Prof, Doctorate
    'B02001_001E',  # Race Total
    'B02001_002E',  # White Alone
    'B02001_003E',  # Black Alone
    'B25003_001E',  # Total Housing Units
    'B25003_002E'   # Owner Occupied Units
)

# We also need to generate the list of "Less than High School" variables (002E through 016E)
less_than_hs_vars = [f'B15003_{str(i).zfill(3)}E' for i in range(2, 17)]
variables = variables + tuple(less_than_hs_vars)

# 3. Pull the data for all tracts in a specific state (e.g., Illinois FIPS is '17', Cook County is '031')
# To get all states, you would loop through state FIPS codes.
stlc = pd.DataFrame(c.acs5.state_county_tract(variables, state_fips='29',
                                 county_fips='189', tract='*'))
stl = pd.DataFrame(c.acs5.state_county_tract(variables,state_fips='29',
                                              county_fips='510', tract='*'))

# 4. Convert to a Pandas DataFrame
df = pd.concat([stl, stlc])

# 5. Calculate your specific requested columns
df['Less than High School'] = df[less_than_hs_vars].sum(axis=1) / df['B15003_001E']
df['High School'] = (df['B15003_017E'] + df['B15003_018E']) / df['B15003_001E']
df["Associate's Degree"] = df['B15003_021E'] / df['B15003_001E']
df["Bachelor's Degree"] = df['B15003_022E'] / df['B15003_001E']
df["Master's Degree or Higher"] = (df['B15003_023E'] + df['B15003_024E'] + df['B15003_025E']) / df['B15003_001E']

df['Proportion White'] = df['B02001_002E'] / df['B02001_001E']
df['Proportion Black'] = df['B02001_003E'] / df['B02001_001E']
df['Proportion All Other Races'] = (df['B02001_001E'] - df['B02001_002E'] - df['B02001_003E']) / df['B02001_001E']

df['Home Ownership Rate'] = df['B25003_002E'] / df['B25003_001E']

# 6. Rename the straight-pull columns to match your desired output
df = df.rename(columns={
    'B01003_001E': 'Total Population',
    'B19013_001E': 'Median HHI',
    'B19013A_001E': 'Median HHI White',
    'B19013B_001E': 'Median HHI Black'
})

# 7. Keep ONLY your desired columns
final_columns = [
    'NAME', 'Total Population', 'Median HHI', 'Median HHI White', 'Median HHI Black',
    'Less than High School', 'High School', "Associate's Degree", "Bachelor's Degree", 
    "Master's Degree or Higher", 'Proportion White', 'Proportion Black', 
    'Proportion All Other Races', 'Home Ownership Rate'
]

final_df = df[final_columns]

census_nulls = [
    -666666666, '-666666666', -666666666.0,
    -888888888, '-888888888', -888888888.0,
    -999999999, '-999999999', -999999999.0
]
final_df = final_df.replace(census_nulls, np.nan)

final_df['NAME'] = final_df['NAME'].str.extract(r'Census Tract ([\d\.]+)')

# Export to CSV if you would like, not required for project workflow
#final_df.to_csv(os.path.join(path_raw_data, 'clean_census_tracts.csv'), index=False)



# --- 2. MERGE DEMOGRAPHIC AND SHAPE DATA ---

# Here I am taking the combined demo data and merging it with the geographic data to
# prepare a dataset for later mapping with GeoPandas.

stl_tracts = stl_tracts.merge(final_df, on='NAME')
stl_tracts.rename({'NAME':'TRACT', 'NAMELSADCO':'COUNTY'}, axis=1, inplace=True)
stl_tracts['AREA'] = stl_tracts['ALAND'] + stl_tracts['AWATER']
stl_tracts['SQMI'] = stl_tracts['AREA']*3.8610215854245E-7
stl_tracts['DENSITY'] = round(stl_tracts['Total Population']/stl_tracts['SQMI'])

# Here I am discerning the boundries of the proposed new city, which requires some 
# mannual tuning for geographic considerations.
# Density selection
stl_select = stl_tracts[(stl_tracts['COUNTY']=='St. Louis city') | (stl_tracts['DENSITY']>=3600)]

# Remove tracts for compactness
non_cont_tracts = ['2215.06', '2179.44', '2179.23', '2179.31', '2179.42', '2181.05', '2214.25',
                   '2180.16', '2115.45', '2115.46', '2150.05', '2132.04', '2149.02', '2146.01',
                   '2146.02', '2144', '2135', '2134.01', '2134.02', '2133.02', '2148', '2116',
                   '2111.01', '2110.02', '2110.01', '2109.25', '2109.26', '2109.28', '2109.24',
                   '2109.23', '2113.01', '2113.31', '2113.32', '2151.45', '2151.46', '2147',
                   '2107.04', '2184.01', '2151.02', '2118.01']

# #Add tracts for contiguity
add_tracts = ['2201.02','2206.01', '2206.02', '2203', '2197','2207.01', '2208.01', '2192', '2193',
              '2213.37', '2213.37', '2204.50', '2204.42', '2186', '2219', '2189.01', '2173',
              '2166', '2139', '2141', '2104', '2120.02', '2118.01', '2202', '2124']

stl_select = stl_select[~stl_select['TRACT'].isin(non_cont_tracts)]
stl_select = pd.concat([stl_tracts[stl_tracts['TRACT'].isin(add_tracts)], stl_select],
                       ignore_index=True)
stl_select.drop_duplicates(inplace=True)

# Basic calculations for verification
print(stl_select['Total Population'].sum())
print(stl_select['SQMI'].sum())
print(stl_select['Total Population'].sum()/stl_select['SQMI'].sum())

# Here I dissolve the cencus tracts for visual presentation purposes, removing internal
# tract boarders.
newstl = stl_select.copy()
newstl['DISID'] = 1
newstl = newstl.dissolve(by='DISID', aggfunc={'Total Population':'sum', 'SQMI':'sum'})
newstl['DENSITY'] = round(newstl['Total Population']/newstl['SQMI'])
newstl['NAME'] = 'New St. Louis'
print(newstl)

# New County all in
county_all = stl_tracts.copy()
county_all['DISID'] = 1
county_all = county_all.dissolve(by='DISID', aggfunc={'Total Population':'sum', 'SQMI':'sum'})
county_all['NAME'] = 'New Combined St. Louis County'

# New St. Louis County (minus the new city)
newstl_tracts = stl_select['TRACT']
newcounty = stl_tracts[~stl_tracts['TRACT'].isin(newstl_tracts)]
newcounty = newcounty.dissolve(by='COUNTY', aggfunc={'Total Population':'sum', 'SQMI':'sum'})
newcounty['NAME'] = 'St. Louis County (without STL)'



# --- 2a. Municipality level data ---

stl_munis = gpd.read_file(os.path.join(path_raw_data,
                                       'Municipal_Boundaries.geojson'))
stl_munis['last_edited_date'] = stl_munis['last_edited_date'].astype(str)
stl_munis['MUNICIPALITY'] = stl_munis['MUNICIPALITY'].str.title()
stl_munis.rename(columns={'MUNICIPALITY': 'Municipality'}, inplace=True)
stl_munis = stl_munis[stl_munis['Municipality']!='Unincorporated']

muni_fin = pd.read_csv(os.path.join(path_raw_data,'muni_finances_merged.csv'))
muni_fin.drop(columns='Population', inplace=True)
muni_gov = pd.read_csv(os.path.join(path_raw_data,'muni_governance_merged.csv'))
muni_data = muni_fin.merge(muni_gov, on='Municipality')
muni_data['Municipality'].replace(['Saint Ann', 'Saint John'], ['St Ann', 'St John'],
                                  inplace=True)

munis_merged = stl_munis.merge(muni_data, on='Municipality', how='right')
munis_merged[munis_merged['geometry']==None]

# Manually add the missing geometry
current_city_geom = stl_tracts[stl_tracts['COUNTY'] == 'St. Louis city'].dissolve().geometry.iloc[0]
current_county_geom = stl_tracts[stl_tracts['COUNTY'] == 'St. Louis County'].dissolve().geometry.iloc[0]

# Calculate incorporated union to find unincorporated area
incorporated_union = stl_munis.unary_union
unincorporated_geom = current_county_geom.difference(incorporated_union)

munis_merged.loc[munis_merged['Municipality'] == 'STL County', 'geometry'] = unincorporated_geom
munis_merged.loc[munis_merged['Municipality'] == 'Saint Louis City', 'geometry'] = current_city_geom
munis_merged.drop(columns='last_edited_date', inplace=True)

# Ensure it's a GeoDataFrame before renaming/saving
munis_merged = gpd.GeoDataFrame(munis_merged, crs='EPSG:4326')

# Rename columns for human readability
rename_dict = {
    'Year_Inc': 'Year Incorporated',
    'Total_Rev': 'Total Revenue',
    'Sales_Tax_Rev': 'Sales Tax Revenue',
    'Property_Tax_Rev': 'Property Tax Revenue',
    'Utility_Tax_Rev': 'Utility Tax Revenue',
    'Court_Fines_Rev': 'Court Fines Revenue',
    'Total_Exp': 'Total Expenditures',
    'Top_Exp_Type': 'Top Expenditure Type',
    'Median_HH_Inc': 'Median Household Income',
    'Poverty_Rate': 'Poverty Rate',
    'HS_Grad_Rate': 'HS Graduation Rate',
    'Median_House_Value': 'Median House Value',
    'Housing_Units': 'Housing Units',
    'Percent_White': 'Percent White',
    'Percent_Black': 'Percent Black',
    'Percent_Asian': 'Percent Asian',
    'Percent_Hispanic': 'Percent Hispanic',
    'Total_Elected_Officials': 'Total Elected Officials',
    'Aldermen_Count': 'Aldermen Count',
    'Total_Aldermen_Pay': 'Total Aldermen Pay',
    'Mayor_Pay': 'Mayor Pay',
    'Admin_Position': 'Admin Position',
    'Admin_Pay': 'Admin Pay',
    'Sum_Total_Payroll': 'Sum Total Payroll',
    'Per_Capita_Admin_Cost': 'Per Capita Admin Cost'
}
munis_merged.rename(columns=rename_dict, inplace=True)

munis_merged['Year Incorporated'] = np.where(munis_merged['Municipality']=='STL County', 1812, munis_merged['Year Incorporated'])
munis_merged['Year Incorporated'] = np.where(munis_merged['Municipality']=='Green Park', 1995, munis_merged['Year Incorporated'])

# Craft per capita metrics
# List of columns to calculate per capita and winsorize
pc_cols = ['Total Revenue', 'Sales Tax Revenue', 'Property Tax Revenue', 
           'Utility Tax Revenue', 'Court Fines Revenue', 'Total Expenditures',
           'Total Elected Officials']

# Ensure population is numeric and handle zeros to avoid division error
munis_merged['Population'] = pd.to_numeric(munis_merged['Population'], errors='coerce')
pop_safe = munis_merged['Population'].replace(0, np.nan)

# Loop through to get new values
for col in pc_cols:
    # Ensure column is numeric (handle potential string/comma issues)
    if munis_merged[col].dtype == 'object':
        munis_merged[col] = pd.to_numeric(munis_merged[col].astype(str).str.replace(',', ''), errors='coerce')

    if col == 'Total Elected Officials':
        pc_name = 'Elected Officials Per 50,000 People'
        wins_name = 'Elected Officials Per 50,000 People (winsorized)'
        # Calculate Per 50,000
        munis_merged[pc_name] = (munis_merged[col] / pop_safe) * 50000
    else:
        pc_name = f'{col} Per Capita'
        wins_name = f'{col} Per Capita (winsorized)'
        # Calculate Per Capita
        munis_merged[pc_name] = munis_merged[col] / pop_safe

    # Calculate Winsorized version 
    upper = munis_merged[pc_name].quantile(0.90)
    munis_merged[wins_name] = munis_merged[pc_name].clip(upper=upper)

munis_merged['Per Capita Admin Cost (winsorized)'] = munis_merged['Per Capita Admin Cost'].clip(upper=munis_merged['Per Capita Admin Cost'].quantile(0.95))  



# --- 3. TRANSIT AND PUBLIC SAFTEY OVERLAYS ---

# Police and Fire
police = gpd.read_file(os.path.join(path_raw_data, 'police.geojson'))
firestat = gpd.read_file(os.path.join(path_raw_data, 'stl_firestat.geojson'))
firedist = gpd.read_file(os.path.join(path_raw_data, 'stlc_firedist.geojson'))

# Transit
busstat = gpd.read_file(os.path.join(path_raw_data, 'stations_bus.geojson'))
metrostat = gpd.read_file(os.path.join(path_raw_data, 'stations_metro.geojson'))
busroute = gpd.read_file(os.path.join(path_raw_data, 'routes_bus.geojson'))
metroroute = gpd.read_file(os.path.join(path_raw_data, 'routes_metro.geojson'))

# Cleaning safety data
police = police[['OBJECTID', 'Police_Dep', 'Precinct', 'Muni',
                 'Address', 'geometry']]
police.rename(columns={'Police_Dep':'Police Dept.', 'Muni': 'Municipality'},
              inplace=True)
firestat = firestat[['Engine', 'Address', 'Dist', 'HOUSENUM', 'geometry']]
firestat.rename(columns={'Dist':'District', 'HOUSENUM': 'House Number'},
                inplace=True)
firedist = firedist[['GlobalID', 'FD_TYPE', 'FIRE_DISTRICT', 'SQ_MILES', 'geometry']]
firedist.rename(columns={'FD_TYPE':'Type', 'FIRE_DISTRICT': 'District',
                         'SQ_MILES':'Square Miles'}, inplace=True)

# Cleaning transit data
busstat = busstat[['OBJECTID', 'StopID', 'StopName', 'Lines', 'Routes',
                   'CountyName', 'geometry']]
metrostat = metrostat[['OBJECTID', 'StopID', 'StopName', 'BusCxn',
                       'City', 'CountyName', 'geometry']]
metrostat.rename(columns={'City':'Municipality', 'BusCxn':'Bus Connection'},
                 inplace=True)
busroute = busroute[['OBJECTID', 'LineName', 'LineNum', 'geometry']]

# Econ data
econ = pd.read_csv(os.path.join(path_raw_data, 'stl_innovation_geo.csv'))
econ['geometry'] = gpd.points_from_xy(econ['long'], econ['lat'])
econ = gpd.GeoDataFrame(econ, geometry='geometry', crs='EPSG:4326')



# --- 4. ADD PROCESSED DATA TO DERIVED DATA FOLDER ---

# Run code blocks to drop cleaned boundry data into the proper project folder for use 
# in visualizations
# All tracts map
stl_tracts.to_file(os.path.join(path_cleaned_data, 'all_tracts.geojson'), driver='GeoJSON')

# New proposed city boundires without dissolve
stl_select.to_file(os.path.join(path_cleaned_data, 'newstl_tracts.geojson'), driver='GeoJSON')

# New proposed city boundries with dissolve
newstl.to_file(os.path.join(path_cleaned_data, 'newstl_dis.geojson'), driver='GeoJSON')

# New county boundries with dissolve (minus stl)
newcounty.to_file(os.path.join(path_cleaned_data, 'county_minus_newstl.geojson'), driver='GeoJSON')

# New county boundries with dissolve (incl stl)
county_all.to_file(os.path.join(path_cleaned_data, 'county_plus_newstl.geojson'), driver='GeoJSON')

# Municipalities geo data with finance data
munis_merged.to_file(os.path.join(path_cleaned_data, 'munis_merged.geojson'), driver='GeoJSON')

# Infra.
police.to_file(os.path.join(path_cleaned_data, 'police.geojson'), driver='GeoJSON')
firestat.to_file(os.path.join(path_cleaned_data, 'firestat.geojson'), driver='GeoJSON')
firedist.to_file(os.path.join(path_cleaned_data, 'firedist.geojson'), driver='GeoJSON')
busstat.to_file(os.path.join(path_cleaned_data, 'busstat.geojson'), driver='GeoJSON')
busroute.to_file(os.path.join(path_cleaned_data, 'busroute.geojson'), driver='GeoJSON')
metroroute.to_file(os.path.join(path_cleaned_data, 'metroroute.geojson'), driver='GeoJSON')
metrostat.to_file(os.path.join(path_cleaned_data, 'metrostat.geojson'), driver='GeoJSON')
econ.to_file(os.path.join(path_cleaned_data, 'stl_econ.geojson'), driver='GeoJSON')
