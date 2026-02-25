import pandas as pd
import numpy as np
import re
import os
from pathlib import Path

base_dir = Path(__file__).resolve().parent.parent
path_raw_data = os.path.join(base_dir, 'data', 'raw-data')
path_cleaned_data = os.path.join(base_dir, 'data', 'derived-data')

def clean_num(val):
    if pd.isna(val) or val == '':
        return 0
    # Remove $, commas, and bracketed references like [1]
    s = str(val).replace('$', '').replace(',', '').strip()
    s = re.sub(r'\[\d+\]', '', s)
    if 'Information Not Provided' in s or 'N/A' in s or 'does not exist' in s or 'Vacant' in s:
        return 0
    try:
        return float(s)
    except:
        return 0

# Raw data extraction from OCR (Tables 1-4 combined logic)
# Municipality, Pop, ElectedOff, AldCount, AldTotalPay, MayorPay, AdminPosition, AdminPay
muni_data = [
    ["Ballwin", 30404, 9, 8, 33600, 8400, "City Administrator", 145000],
    ["Bel-Nor", 1499, 5, 4, 4800, 1800, "City Clerk", 34000],
    ["Bel-Ridge", 2737, 9, 8, 0, 0, "City Clerk", 36400],
    ["Bella Villa", 729, 7, 6, 21600, 3000, "City Clerk", 31988],
    ["Bellefontaine Neighbors", 10860, 9, 8, 0, 0, "City Clerk", 41633],
    ["Bellerive Acres", 188, 5, 4, 0, 0, "City Administrator", 9000],
    ["Berkeley", 8978, 7, 6, 12600, 2100, "City Manager", 80000],
    ["Beverly Hills", 574, 5, 4, 14400, 4800, "City Administrator", 0],
    ["Black Jack", 6929, 10, 8, 57600, 24000, "City Clerk", 44387],
    ["Breckenridge Hills", 4746, 9, 8, 0, 0, "None Provided", 0],
    ["Brentwood", 8055, 9, 8, 57600, 14400, "City Administrator", 120622],
    ["Bridgeton", 11550, 10, 8, 4800, 15000, "City Administrator", 122846],
    ["Calverton Park", 1293, 5, 4, 2400, 2400, "City Clerk", 39374],
    ["Champ", 13, 5, 4, 0, 0, "Village Clerk", 0],
    ["Charlack", 1363, 5, 4, 0, 0, "City Clerk", 31200],
    ["Chesterfield", 47484, 9, 8, 48000, 12000, "City Administrator", 160332],
    ["Clarkson Valley", 2632, 7, 6, 7200, 5400, "City Clerk", 36582],
    ["Clayton", 15939, 7, 6, 14400, 6000, "City Manager", 161244],
    ["Cool Valley", 1196, 5, 4, 9600, 3600, "City Clerk", 43514],
    ["Country Club Hills", 1274, 5, 4, 0, 0, "City Clerk", 18462],
    ["Country Life Acres", 74, 5, 4, 4, 1, "None Provided", 0],
    ["Crestwood", 11912, 9, 8, 33600, 8400, "City Administrator", 93500],
    ["Creve Coeur", 17833, 9, 8, 76800, 14400, "City Administrator", 158616],
    ["Crystal Lake Park", 470, 5, 4, 0, 0, "City Clerk", 23400],
    ["Dellwood", 5025, 9, 8, 33600, 8400, "City Administrator", 55000],
    ["Des Peres", 8373, 8, 6, 41400, 13200, "City Administrator", 142192],
    ["Edmundson", 834, 5, 4, 19200, 9600, "City Clerk", 66414],
    ["Ellisville", 9133, 7, 6, 37500, 9200, "City Manager", 136500],
    ["Eureka", 10189, 7, 6, 28800, 8400, "City Administrator", 108972],
    ["Fenton", 4022, 9, 8, 0, 0, "City Clerk", 77600],
    ["Ferguson", 21203, 7, 6, 18000, 4200, "City Manager", 110000],
    ["Flordell Hills", 822, 5, 4, 14400, 4800, "City Clerk", 35360],
    ["Florissant", 52158, 10, 9, 104112, 135746, "City Clerk", 70450],
    ["Frontenac", 3482, 7, 6, 0, 0, "City Administrator", 142099],
    ["Glen Echo Park", 160, 5, 4, 4800, 1200, "Village Clerk", 0],
    ["Glendale", 5925, 7, 6, 16200, 3600, "City Administrator", 82424],
    ["Grantwood Village", 863, 5, 4, 19200, 5400, "Village Clerk", 4800],
    ["Green Park", 2622, 7, 6, 18600, 5400, "City Administrator", 54997],
    ["Greendale", 651, 5, 4, 4800, 3600, "City Administrator", 41600],
    ["Hanley Hills", 2101, 9, 8, 0, 0, "Village Clerk", 34320],
    ["Hazelwood", 25703, 9, 8, 19200, 3000, "City Manager", 124444],
    ["Hillsdale", 1478, 5, 4, 4800, 1800, "City Manager", 20000],
    ["Huntleigh", 334, 6, 4, 0, 0, "City Clerk", 0],
    ["Jennings", 14712, 9, 8, 57600, 25000, "City Clerk", 61191],
    ["Kinloch", 298, 5, 4, 0, 0, "City Manager", 55000],
    ["Kirkwood", 27540, 7, 6, 14400, 3600, "Chief Admin Officer", 161200],
    ["Ladue", 8521, 7, 6, 0, 0, "City Clerk", 104000],
    ["Lakeshire", 1432, 7, 6, 39312, 2616, "City Clerk", 5182],
    ["Mackenzie", 134, 5, 4, 0, 0, "None Provided", 0],
    ["Manchester", 18094, 7, 6, 27000, 10800, "City Administrator", 99323],
    ["Maplewood", 8046, 7, 6, 17700, 4800, "City Manager", 162702],
    ["Marlborough", 2179, 5, 4, 12000, 3000, "Village Clerk", 45942],
    ["Maryland Heights", 27472, 9, 8, 57600, 14400, "City Administrator", 160000],
    ["Moline Acres", 2442, 5, 4, 24000, 7200, "City Clerk", 52000],
    ["Normandy", 5008, 9, 8, 24000, 10800, "City Administrator", 64000],
    ["Northwoods", 4227, 9, 8, 57600, 9000, "City Administrator", 71469],
    ["Norwood Court", 959, 5, 4, 39600, 9900, "Village Clerk", 9600],
    ["Oakland", 1381, 5, 4, 8880, 6000, "City Administrator", 65200],
    ["Olivette", 7737, 5, 4, 4800, 1200, "City Manager", 97375],
    ["Overland", 16062, 9, 8, 48000, 12000, "City Administrator", 102622],
    ["Pacific", 7002, 10, 6, 27450, 7990, "City Administrator", 76000],
    ["Pagedale", 3304, 7, 6, 50400, 18000, "City Clerk", 0],
    ["Pasadena Hills", 930, 5, 4, 0, 0, "City Administrator", 38500],
    ["Pasadena Park", 470, 5, 4, 12000, 3000, "Village Clerk", 14400],
    ["Pine Lawn", 3275, 9, 8, 48000, 60000, "City Clerk", 34944],
    ["Richmond Heights", 8603, 9, 8, 9600, 1000, "City Manager", 129051],
    ["Riverview", 2856, 5, 4, 4800, 1200, "Village Clerk", 27000],
    ["Rock Hill", 4635, 7, 6, 19800, 6600, "City Administrator", 82000],
    ["Saint Ann", 13020, 10, 8, 72000, 20700, "City Administrator", 90686],
    ["Saint John", 6517, 7, 6, 10800, 1800, "City Manager", 110850],
    ["Saint Louis City", 319294, 38, 29, 1116000, 131820, "None", 0],
    ["Shrewsbury", 6254, 7, 6, 27000, 9000, "Director of Administration", 92507],
    ["STL County", 998954, 10, 7, 145000, 140000, "None", 0],
    ["Sunset Hills", 8496, 10, 8, 38400, 6000, "City Administrator", 59301],
    ["Sycamore Hills", 668, 5, 4, 6480, 2400, "Village Clerk", 2550],
    ["Town & Country", 10815, 9, 8, 40320, 6000, "City Administrator", 140036],
    ["Twin Oaks", 392, 5, 4, 0, 0, "Village Clerk", 0],
    ["University City", 35371, 7, 6, 14400, 4800, "City Manager", 135252],
    ["Uplands Park", 445, 5, 4, 0, 2700, "Village Clerk", 32000],
    ["Valley Park", 6942, 9, 8, 38400, 9600, "City Clerk", 57097],
    ["Velda City", 1420, 5, 4, 14400, 9000, "City Clerk", 33280],
    ["Velda Village Hills", 1055, 5, 4, 21000, 6300, "City Clerk", 33280],
    ["Vinita Park", 1880, 7, 6, 48240, 40680, "City Clerk", 45323],
    ["Vinita Terrace", 277, 5, 4, 1924, 4849, "Village Clerk", 5400],
    ["Warson Woods", 1962, 9, 8, 9600, 3000, "City Clerk", 55755],
    ["Webster Groves", 22995, 7, 6, 3600, 750, "City Manager", 166306],
    ["Wellston", 2313, 7, 6, 45000, 20000, "City Administrator", 10000],
    ["Westwood", 278, 5, 4, 0, 0, "N/A", 0],
    ["Wilbur Park", 471, 5, 4, 10400, 3000, "N/A", 0],
    ["Wildwood", 35517, 17, 16, 40000, 5000, "City Administrator", 136500],
    ["Winchester", 1547, 5, 4, 14880, 5040, "City Administrator", 63000],
    ["Woodson Terrace", 4063, 11, 8, 48000, 24456, "City Clerk", 55000]
]

columns = [
    "Municipality", "Population", "Total_Elected_Officials", "Aldermen_Count", 
    "Total_Aldermen_Pay", "Mayor_Pay", "Admin_Position", "Admin_Pay"
]

df = pd.DataFrame(muni_data, columns=columns)

# Calculate Sum Total
df['Sum_Total_Payroll'] = df['Total_Aldermen_Pay'] + df['Mayor_Pay'] + df['Admin_Pay']
df['Per_Capita_Admin_Cost'] = df['Sum_Total_Payroll'] / df['Population']

# Save to derived-data
df.to_csv(os.path.join(path_cleaned_data, 'muni_governance_merged.csv'), index=False)
print("Merged CSV generated successfully.")
