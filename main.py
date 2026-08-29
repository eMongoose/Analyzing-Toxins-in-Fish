import pandas as pd
import numpy as np
from src.paths import *


df = pd.read_csv(CLEANED_PATH / 'master_data.csv', parse_dates=['date'])

df = df[~df['is_surrogate']].copy() # make a copy without the surrogate ones

df = df[df['rep_no'] == 1].copy() # Use primary replicate only for the main analysis

df['result_status'] = 'detected' # fill rows with 'detected'

df.loc[df['p_flag'].isin(['ND', 'BDL']), 'result_status'] = 'nondetect'
df.loc[df['p_flag'] == 'BQL', 'result_status'] = 'below_quantification'


# ND = no detection
# BDL = below the detection limit
# BQL = detection too low to reliably quantify


# Create a boolean for whether the result is censored
df['is_censored'] = (df['p_flag'].isin(['ND', 'BDL', 'BQL']))

# Create a column that keeps concentrations only for quantified measurements 
df['detected_conc'] = df['conc_ng_g']
df.loc[df['is_censored'], 'detected_conc'] = np.nan


selected_toxins = [ 
    "p-p'-DDE",
    'Dieldrin',
    'Mirex',
    'Total PCBs (as Arochlor 1254)'
]

df = df[df['toxin_clean'].isin(selected_toxins)].copy()

# Test to see how much data tremains
# print(
#     df.groupby('toxin_clean').agg(
#         observations=('fish_id', 'size'),
#         fish=('fish_id', 'nunique'),
#         first_year=('year', 'min'),
#         last_year=('year', 'max')
#     )
# )

# Build a yearly summary table for Power BI

# Median quantified concentration
yearly_conc = df.groupby(['year', 'toxin_clean']).agg(
    median_conc=('detected_conc', 'median'),
    mean_conc=('detected_conc', 'mean'),
    n_quantified=('detected_conc', 'count')
).reset_index()

# Detection/Censoring rate
yearly_detection = df.groupby(['year', 'toxin_clean']).agg(
    total=('is_censored', 'size'),
    censored=('is_censored', 'sum')
).reset_index()

# Calculate the percentage that is ND/BDL/BQL
yearly_detection['pct_censored'] = yearly_detection['censored'] / yearly_detection['total'] * 100

# Calculate the percent that is NOT censored
yearly_detection['pct_quantified'] = 100 - yearly_detection['pct_censored']


# Save the files
df.to_csv(CLEANED_PATH / 'analysis_data.csv', index=False)
yearly_conc.to_csv(CLEANED_PATH / 'yearly_concentration.csv', index=False)
yearly_detection.to_csv(CLEANED_PATH / 'yearly_detection.csv', index=False)