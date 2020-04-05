# -*- coding: utf-8 -*-
"""
Created on Thu Sep 26 15:55:38 2019

@author: benjamin.a.cooper
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
#import seaborn as sns
import geopandas as gpd 
from PIL import Image, ImageDraw
import datetime as dt


#sns.set(style='whitegrid', palette='pastel', color_codes=True)
#sns.mpl.rc('figure', figsize=(10,6))

geojson_path =('/Users/bencooper/Desktop/Personal_Projects/migratio/Council Districts Fill.geojson')
shp_path = r'/Users/bencooper/Desktop/Personal_Projects/migratio/census_tracts_2010_msa/census_tracts_2010_msa.shp'
path = r'/Users/bencooper/Desktop/Personal_Projects/migratio/shared_mobility.csv'
png_path = r'/Users/bencooper/Desktop/Personal_Projects/migratio/img2.png'
downtown_tracts_path = r'/Users/bencooper/Desktop/Personal_Projects/migratio/downtown_tracts.csv'

plot_locations = gpd.read_file(shp_path) #       generate GeoDataFrame
plot_locations = plot_locations[['TRACTCE10','geometry']]

#Prod
scooter_df = pd.read_csv(path, usecols=['Vehicle Type','Census Tract Start','Census Tract End','End Time','Start Time', 'Day of Week'], dtype={'Vehicle Type':str,'Census Tract Start':str,'Census Tract End':str,'End Time':str, 'Start Time':str})#       build main data frame holding times and locations

#Test
#scooter_df = pd.read_csv(path,nrows=2000, usecols=['Vehicle Type','Census Tract Start','Census Tract End','End Time','Start Time', 'Day of Week'], dtype={'Vehicle Type':str,'Census Tract Start':str,'Census Tract End':str,'End Time':str, 'Start Time':str})#       build main data frame holding times and locations


downtown_census_tracts_df = pd.read_csv(downtown_tracts_path)




def fig2data ( fig ):
    """
    @brief Convert a Matplotlib figure to a 4D numpy array with RGBA channels and return it
    @param fig a matplotlib figure
    @return a numpy 3D array of RGBA values
    """
    # draw the renderer
    fig.canvas.draw ( )
 
    # Get the RGBA buffer from the figure
    w,h = fig.canvas.get_width_height()
    buf = np.frombuffer ( fig.canvas.tostring_argb(), dtype=np.uint8 )
    buf.shape = ( w, h,4 )
 
    # canvas.tostring_argb give pixmap in ARGB mode. Roll the ALPHA channel to have it in RGBA mode
    buf = np.roll ( buf, 3, axis = 2 )
    return buf

def fig2img ( fig ):
    """
    @brief Convert a Matplotlib figure to a PIL Image in RGBA format and return it
    @param fig a matplotlib figure
    @return a Python Imaging Library ( PIL ) image
    """
    # put the figure pixmap into a numpy array
    buf = fig2data ( fig )
    w, h, d = buf.shape
    return Image.frombytes( "RGBA", ( w ,h ), buf.tostring( ) )
    
    

def create_gif(time_rng,plot_locations):
    count = 0
    global scooter_df
    count_df = build_count_df()
    count_max = count_df['count'].idxmax()
    print(count_max)
    
    for day in range(7):
        for time in time_rng:
            cond1 = count_df['time'] == time
            cond2 = count_df['DoW'] == day
            temp_count_df = count_df[(cond1 & cond2)]
            missing_tracts = plot_locations[plot_locations['TRACTCE10'].isin(temp_count_df['TRACTCE10']) == False]
            present_geometry_dict = plot_locations[plot_locations['TRACTCE10'].isin(temp_count_df['TRACTCE10'])]
            present_geometry_dict = present_geometry_dict.set_index('TRACTCE10')
            present_geometry_dict = present_geometry_dict['geometry'].to_dict()
            
            temp_count_df['geometry'] = temp_count_df['TRACTCE10'].map(present_geometry_dict)
            temp_count_df = temp_count_df[['TRACTCE10','geometry','count']]
            temp_count_df = temp_count_df.append(missing_tracts)
        
            temp_plot_df = gpd.GeoDataFrame(temp_count_df)    
            variable = 'count'
            vmin, vmax = 0, int(count_max)
            fig, ax = plt.subplots(1, figsize = (10,10))
            temp_plot_df.plot(column=variable, cmap='Reds', linewidth=0.8, ax=ax, edgecolor='0.8')
            ax.axis('off')
            
            
            ax.annotate('Time:{}\nDay of Week:{}'.format(time, day),xy=(0.1, .08),  xycoords='figure fraction', horizontalalignment='left', verticalalignment='top', fontsize=12, color='#555555')
            
                        
            sm = plt.cm.ScalarMappable(cmap='Oranges', norm=plt.Normalize(vmin=vmin, vmax=vmax))
            # empty array for the data range
            sm._A = []
            # add the colorbar to the figure
            cbar = fig.colorbar(sm)
            
            
            frame = fig2img(fig)
    #        frame.save('out/{0:03d}.png'.format(count), optimize=False)
            frame.save('out2/{0:05d}.png'.format(count), optimize=False)
            count +=1
            
            print('finished {}/{}'.format(count,len(time_rng)*7))
            if sum(temp_count_df['count']) == 0:
                print('WARNING: BLANK MAP')
            fig.clear()
            plt.close(fig)
#    im_list[0].save('out.gif', save_all=True, optimize=False, append_images=im_list[1:], duration=100, loop=0)
    
        




def manipulation_scooter_df():
    global scooter_df
    print('\n\nstarting scooter_df manipulations...\n')
    
    scooter_df = scooter_df[scooter_df['Vehicle Type']=='scooter']#       selects only scooter rides
        
    print('\n\nconverting scooter_df times to datetime...')
    scooter_df['Start Time'] = pd.to_datetime(scooter_df['Start Time'],format= '%m/%d/%Y %I:%M:%S %p' ).dt.time
    scooter_df['End Time'] = pd.to_datetime(scooter_df['End Time'],format= '%m/%d/%Y %I:%M:%S %p' ).dt.time
    
    
    
    print('\n\nstripping extra 0\'s from "Census Tract x" columns...\n\n')
    scooter_df['Census Tract Start'] = scooter_df['Census Tract Start'].astype(str).str.slice(7,11)
    scooter_df['Census Tract End'] = scooter_df['Census Tract End'].astype(str).str.slice(7,11)
    scooter_df['Census Tract Start'] = scooter_df['Census Tract Start'].str.lstrip('0')
    scooter_df['Census Tract End'] = scooter_df['Census Tract End'].str.lstrip('0')
    

plot_locations['TRACTCE10'] = plot_locations['TRACTCE10'].str.lstrip('0')#       Standardize the format of Cencus Tract IDs
downtown_census_tracts_df['TRACTCE10'] = pd.Series(downtown_census_tracts_df['TRACTCE10'].values.astype(str))
plot_locations = plot_locations[plot_locations['TRACTCE10'].isin(downtown_census_tracts_df['TRACTCE10'])]


def build_count_df():
    global scooter_df
    
    cond1 = scooter_df['Start Time'] == scooter_df['End Time']
    cond2 = scooter_df['Census Tract Start'] == scooter_df['Census Tract End']
    
    scooter_df.loc[(cond1 & cond2), 'End Time'] = np.NaN
    
    
    df1 = pd.DataFrame()
    df2 = pd.DataFrame()
    df1['time'] = scooter_df['Start Time']
    df1['TRACTCE10'] = scooter_df['Census Tract Start']
    df1['DoW'] = scooter_df['Day of Week']
    
    df2['time'] = scooter_df['End Time']
    df2['TRACTCE10'] = scooter_df['Census Tract End']
    df2['DoW'] = scooter_df['Day of Week']
#    scooter_df = scooter_df.rename(columns={'End Time':'time','Census Tract End':'TRACTCE10'})

    df = pd.concat([df1,df2], join='inner')
    df = df.dropna()
    count_df = df.groupby(['time','TRACTCE10','DoW']).size().reset_index().rename(columns={0:'count'})
    return count_df


time_rng = pd.Series([val.time() for val in pd.to_datetime(pd.date_range('00:00','23:45', freq='15min'))])
plot_locations['count'] = 0

manipulation_scooter_df()
create_gif(time_rng, plot_locations)
