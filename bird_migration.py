# -*- coding: utf-8 -*-
"""
Created on Thu Sep 26 15:55:38 2019

@author: benjamin.a.cooper
"""

import pandas as pd
import matplotlib.pyplot as plt
import shapefile as shp
import numpy as np
import seaborn as sns
import geopandas as gpd
import json

sns.set(style='whitegrid', palette='pastel', color_codes=True)
sns.mpl.rc('figure', figsize=(10,6))

with open('/Users/bencooper/Desktop/migratio/Council Districts Fill.geojson') as f:
    dists = json.loads(f.read())

dict_df = pd.DataFrame(dists['features'])['geometry']
df = gpd.GeoDataFrame.from_records(dict_df)

def read_shapefile(sf):
    fields = [x[0] for x in sf.fields][1:]
    records = sf.records()
    shps = [s.points for s in sf.shapes()]
    
    df = pd.DataFrame(columns = fields, data =records)
    df.assign(coords=shps)
    return df


#path = r'C:\Users\benjamin.a.cooper\WPy64-3740\DataSets\shared_mobility.csv'
path = r'/Users/bencooper/Desktop/migratio/shared_mobility.csv'

data = pd.read_csv(path, nrows=20)
scooter_df = data[data['Vehicle Type']=='scooter']


ct_start = scooter_df['Census Tract Start'].astype(str).str.slice(7,11)
ct_end = scooter_df['Census Tract End'].astype(str).str.slice(7,11)


time_start = pd.to_datetime(scooter_df['Start Time'])
time_end = pd.to_datetime(scooter_df['End Time'])

df = pd.concat([ct_start, ct_end, time_start, time_end], axis=1)

print(aus.records()[1])
shape_df = read_shapefile(aus)
print(shape_df.head())
#def create_dot(time_i, loc_i):
#    #make dot @ start time and location
#
#def move_dot(time_i, time_f, loc_i, loc_f):
#    #create vector from initial to final location