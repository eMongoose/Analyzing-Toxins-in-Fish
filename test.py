import pandas as pd
from src.paths import *


df = pd.read_csv(RAW_PATH / 'OCs_1977-1987.csv')

print(df['Parameter_Group'].value_counts())