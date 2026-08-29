import pandas as pd
import numpy as np
from src.paths import *

# Define a dictionary
# fire me for these naming conventions
datasets = {
    'oc1' : 'OCS_1.csv',
    'oc2' : 'OCS_2.csv',
    'oc3' : 'OCS_3.csv',
    'oc4' : 'OCS_4.csv',
    'oc3_25' : 'OCS_3-25.csv',
    'oc3_5' : 'OCS_3-5.csv'
}

# Read source files
ds_df = {}

for key, filename in datasets.items():
    temp = pd.read_csv(OUTPUT_PATH / filename, index_col=0)
    temp['source_dataset'] = key
    ds_df[key] = temp
    
    
# Drop the fork length
ds_df['oc3_25'] = ds_df['oc3_25'].drop(columns='Fork length (cm)')  

# Combine datasets
df = pd.concat([ds_df['oc1'], ds_df['oc2'], ds_df['oc3'], ds_df['oc3_25'], ds_df['oc3_5'], ds_df['oc4']], ignore_index=True)

# Delete unnecessary columns
df = df.drop(columns=[
    'Genus',  # Too Broad- can be used for different analyses
    'Species', # Too specific
    'Station_Name', # Need not know where it was tested
    'Basin/Site', # Redundant with the waterbody parameter
    'Measurement_Date', # Need not know when the fish length was measured
    'Province/State', # Redundant with the waterbody parameter
    'Latitude', # Location not required. We already have bodies of water.
    'Longitude'
])

# Rename columns
df = df.rename(columns={
    'CSP_No' : 'fish_id',
    'Common_Name' : 'name', 
    'Total Length (cm)' : 'length', 
    'Total Weight (g)': 'weight',
    'Tissue_Code' : 'tissue',
    'Composite_Count' : 'count',
    'Collection_Date' : 'date',
    'Collection_Year' : 'year',
    'Value' : 'concentration',
    'Value_Flag' : 'p_flag',
    'Master_Parameter_Name' : 'mp_name',
    'Parameter_name' : 'p_name',
    'Parameter_Group' : 'toxin_family',
    'Parameter_Code' : 'p_code',
    'Rep' : 'rep_no',
    'Unit_Code' : 'unit',
    'LOD' : 'detect_limit',
    'Waterbody' : 'waterbody',
    'MDL - typical' : 'mdl', # method detection limit
    
    'Sex_Code' : 'gender',
    'Maturity_Code' : 'maturity',
    
    'Laboratory': 'laboratory',
    'Method_Code': 'method_code'
})

# Convert date to datetime
df['date'] = pd.to_datetime(df['date'], errors='coerce')
df['year'] = df['date'].dt.year

# Determine surrogacy
df['is_surrogate'] = (
    df['mp_name'].str.contains('surrogate', case=False, na=False) |
    df['p_name'].str.contains('surrogate', case=False, na=False)
)

# Standardize units
df['unit_clean'] = df['unit'].str.strip().str.upper() # Strip capitalization, and convert to all caps

# Convert comparable units (1 ug/g -> 1000 ng/g, 1 pg/g -> 0.001 ng/g)
df['conc_ng_g'] = np.nan

# Explicit wet-weight measurements
df.loc[df['unit_clean'] == 'NG/G WET', 'conc_ng_g'] = df['concentration'] # Default measurement
df.loc[df['unit_clean'] == 'UG/G WET', 'conc_ng_g'] = df['concentration'] * 1000 # For rows in unit_clean == UG/G WET, measure concentration * 1000 into conc_ng_g

# Units where wet/dry basis is unspecified
df.loc[df['unit_clean'] == 'NG/G', 'conc_ng_g'] = df['concentration'] # Default measurement
df.loc[df['unit_clean'] == 'UG/G', 'conc_ng_g'] = df['concentration'] * 1000 # For rows in unit_clean == UG/G, put the concentration * 1000 into conc_ng_g
df.loc[df['unit_clean'] == 'PG/G', 'conc_ng_g'] = df['concentration'] * 0.001 # For rows in unit_clean == PG/G, put the concentration / 1000 into conc_ng_g

# Create a basis
df['basis'] = 'unspecified'

df.loc[df['unit_clean'].isin(['NG/G WET', 'UG/G WET']), 'basis'] = 'wet' # 
df.loc[df['unit_clean'] == 'PG/G-TEQ', 'basis'] = 'TEQ'
df.loc[df['unit_clean'].isin(['PCT', 'GRAMS']), 'basis'] = 'not_concentration'


# Standardize p_name
df['toxin_clean'] = df['p_name'].replace({
    'ppDDE': "p-p'-DDE",
    'ppDDT': "p-p'-DDT"
})

# Standardize p_flag
df["p_flag"] = df["p_flag"].astype("string").str.strip().str.upper()

################### OUTPUT SECTION ###################
final_cols = [
    # date
    'date',
    'year',
    
    # location
    'waterbody',
    
    # fish identification
    'fish_id',
    'name',
    'length',
    'weight',
    'gender',
    'maturity', # IMM - immature, JUV - Juvenile, ADS - Adult
    'tissue', # WHA - whole, 
    
    # testing
    'count', # number of fish
    'mp_name', # master parameter (toxin) name 
    'p_name',
    'toxin_clean',
    'p_code',
    'toxin_family',
    'concentration', # how much was found
    'conc_ng_g',

    'p_flag', # result
    'unit', 
    'unit_clean',
    'basis',

    'rep_no',
    'detect_limit',
    'mdl',

    # 'housekeeping'
    'is_surrogate',
    'source_dataset',
    'laboratory',
    'method_code',

]

df = df[final_cols]

# Sort by date and fish ID
df = df.sort_values(by=['date', 'fish_id', 'p_code', 'rep_no'])

# Save cleaned dataframe to CSV
# cleaned = {
#     'master_dataset.csv' : df,
# }

# for filename, dataframe in cleaned.items():
#     dataframe.to_csv(CLEANED_PATH / filename, index=False) 

df.to_csv(CLEANED_PATH / 'master_data.csv', index=False)