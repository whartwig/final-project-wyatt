# final-project-whartwig
STL = St. Louis City
STLC = St. Louis County


# Data Sources
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

Population Data:
    EconMeasures: https://data.census.gov/table/ACSST5Y2024.S2503?t=Income+(Households,+Families,+Individuals):Owner/Renter+(Householder)+Characteristics&g=050XX00US29189$1400000,29510$1400000
    DemoEduMeasures: https://data.census.gov/table/ACSDT5YSPT2021.B15002?t=-00:001:Educational+Attainment&g=050XX00US29189$1400000,29510$1400000
    muni_demos.csv: Manual input data from the ACS estimates
    
GeoData:
    TractGIS: https://catalog.data.gov/dataset/tiger-line-shapefile-2021-state-missouri-census-tracts/resource/7e9d9218-f9ab-4866-b090-b470de3b987a
    MunicipalGIS: https://data-stlcogis.opendata.arcgis.com/datasets/municipal-boundaries-4/explore?location=38.639600%2C-90.427400%2C10

Business:
    stl_innovation_geo.csv: Manual input data gathered online

Municipal Finance:
    municipal_governance_merged.csv: Manual input data derived from Better Together 2017 data found at https://www.bettertogetherstl.com/wp-content/uploads/2015/12/General-Administration-Report-Study-3-Final.pdf
    muni_finances_merged.csv: Manual input data derived from Better Together 2017 data found at https://www.bettertogetherstl.com/wp-content/uploads/2015/12/Better-Together-General-Administration-Report-2-FINAL-.pdf