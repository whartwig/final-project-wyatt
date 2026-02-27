# final-project-whartwig
STL = St. Louis City
STLC = St. Louis County



# Sequence of Files
1. data_cleaning_and_processing.py
2. Plotting: run fisc_plot.py
3. Streamlit: app.py


# Steamlit Community Cloud
Link: 

# Structure
data/
  raw-data/           # Raw data files
    muni_finances_merged.csv #St. Louis area municipal finances 2015
    muni_governance_merged.csv #St. Louis area municipal gov finances 2015
    stl_innovation_geo.csv #St. Louis area economic clusters
    police.geojson #Police stations in St. Louis area
    stl_firestat.geojson #St. Louis fire stations
    stl_firedist.geojson #STL County fire districts
    stations_bus.gejson #St. Louis area bus stations
    station_metro.gejson #MetroLink station
    routes_bus.geojson #Area bus routes
    routes_metro.geojson #MetroLink tracks
    fisc_data.csv #Linclon Institute fiscally standardized city data
    census_tracts.dbf and census_tracts.shx #Dependances of census_tracts.shp
    census_tracts.shp #All census tracts in the region
    Municipal_Boundries.geojson #St. Louis area municipality borders
  derived-data/       # Filtered data and output plots
    stl_econ.geojson  #conversion with gpd of stl_innovation.csv
    busroute.geojson #Filtered bus routes
    metroroute.geojson #Filtered metro routes
    metrostat.geojson #filtered metro stations
    busstat.geojson #filtered bus station
    firedis.geojson #filtered fire stations
    firestat.geojson #filtered fire stations
    police.geojson #filtered/cleaned police districts/stations
    muni_merged.geojson #combined stl area municipal data and borders
    all_tracts.geojson #all area census tracts with minor filtering
    county_plus_newstl.geojson #combined borders for new county
    newstl_dis.geojson #proposed st louis city borders dissolved by census tract
    newstl_tracts.geojson #census tracts filtered to the new city 
    stl_tracts.geojson #census tracts for filtered to the current city
code/
  data_cleaning_and_processing.py    # Reads in, gathers, cleans, and filters various datasets from raw-data and places them into derived-data for use
  app.py       # stramlit dashboard code for interactive mapping
  fisc_plot.py #plots graphs of fisc analysis for relevent cities
  








# Data Sourcing
Infrastructure data: 
    MetroBus: https://data-metrostl.opendata.arcgis.com/datasets/METROSTL::currentsystem-registered/explore?layer=4&location=38.636254%2C-90.252426%2C11
    MetroLink: https://data-metrostl.opendata.arcgis.com/datasets/METROSTL::currentsystem-registered/explore?layer=3&location=38.646980%2C-90.268905%2C10
    StationsBus: https://data-metrostl.opendata.arcgis.com/datasets/METROSTL::currentsystem-registered/explore?layer=2&location=38.646980%2C-90.268905%2C10
    StationsMetroLink: https://data-metrostl.opendata.arcgis.com/datasets/METROSTL::currentsystem-registered/explore?layer=1&location=38.646980%2C-90.268905%2C10

Public Saftey Data:
    FireProtection (STLC): https://data-stlcogis.opendata.arcgis.com/datasets/fire-districts/explore?location=38.659442%2C-90.330583%2C11&showTable=true
    FireStation (STLC) [not an immediate data source]: https://wiki.radioreference.com/index.php/St._Louis_County_(MO)_Fire/EMS_Stations
    FireStations (STL): https://hub.planstl.com/datasets/fire-stations-1/explore?location=38.638327%2C-90.235081%2C11
    PolicePrecinct (all): https://data.stlouisco.com/datasets/stlcogis::alldepartments-2024/explore?location=38.640936%2C-90.416034%2C10
    
GeoData:
    TractGIS: https://catalog.data.gov/dataset/tiger-line-shapefile-2021-state-missouri-census-tracts/resource/7e9d9218-f9ab-4866-b090-b470de3b987a
    MunicipalGIS: https://data-stlcogis.opendata.arcgis.com/datasets/municipal-boundaries-4/explore?location=38.639600%2C-90.427400%2C10

Business:
    stl_innovation_geo.csv: Manual input data gathered online

Municipal Finance:
    municipal_governance_merged.csv: Manual input data derived from Better Together 2017 data found at https://www.bettertogetherstl.com/wp-content/uploads/2015/12/General-Administration-Report-Study-3-Final.pdf
    muni_finances_merged.csv: Manual input data derived from Better Together 2017 data found at https://www.bettertogetherstl.com/wp-content/uploads/2015/12/Better-Together-General-Administration-Report-2-FINAL-.pdf
    fisc_data.csv: https://www.lincolninst.edu/app/uploads/2026/01/FiSC-Full-Dataset-2023-Update.xlsx