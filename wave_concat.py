"""
Module for concatenating wave_height_dataframes produced by raw_combined.py
Given a buoy root directory and buoy name the code will iterate over a list of 
buoys producing statistics for the concatenated wave_height_dataframes 
including h_max, h_1_3_mean and the time period these statistics cover. The 
statistics are then saved as a Pandas DataFrame and exported to Excel xlsx 
format. This process can also be carried out for the pressure data from a 
Nortek AWAC in process_awac_wave_height given a wad file from 
wad_to_dataframe.py 

@author: James Morrison
@license: MIT
"""

import os
import pandas as pd
import numpy as np
import time
from datetime import datetime

#buoys = ['Roag_Wavegen','Bragar_HebMarine2','Siadar_HebMarine1']
buoys = ['buoy_data']
buoys_root_path = ''
awac_root_path = 'D:\\awac_time_series\\'
time_based_stats = True

def timestamp_to_nearest_half_hour(timestamp, set_length_seconds):
    unix_timestamp = time.mktime(timestamp.timetuple())
    return round(unix_timestamp/set_length_seconds)*set_length_seconds

def arrays_to_df_excel(stats_dict, buoy_name, path):
    index_df = pd.DatetimeIndex(stats_dict['start_times'])
    end_df = pd.DataFrame(stats_dict['end_times'], index=index_df, columns=['end_times'])
    h_1_3_mean_df = pd.DataFrame(stats_dict['h_1_3_mean'], index=index_df, 
                                 columns=['h_1_3_mean'])
    h_max_df = pd.DataFrame(stats_dict['h_max'], index=index_df, columns=['h_max'])
    h_avg_df = pd.DataFrame(stats_dict['h_avg'], index=index_df, columns=['h_avg'])
    h_std_df = pd.DataFrame(stats_dict['h_std'], index=index_df, columns=['h_std'])
    set_df = h_max_df.join([h_1_3_mean_df, h_avg_df, h_std_df, end_df])
    set_df.save(path + 'wave_h_' + str(stats_dict['set_size']) + 
                'set_' + buoy_name)
    set_df.to_excel(path + 'wave_h_' + str(stats_dict['set_size']) + 'set_' + 
                    buoy_name + '.xlsx')


def get_stats_from_df(large_dataframe, series_name):
    date_time_col = 'date_time_index'
    large_dataframe = large_dataframe.sort()
    reset_index_df = large_dataframe.reset_index()
    cols = reset_index_df.columns.values
    cols[0] = date_time_col
    reset_index_df.columns = cols
    grouped_df = reset_index_df.groupby('file_name')
    file_name_std_df = grouped_df[series_name].std()
    file_name_std_df.name = 'h_std'
    file_name_max_series = grouped_df[series_name].max()
    file_name_max_series.name = 'h_max'
    file_name_avg_series = grouped_df[series_name].mean()
    file_name_avg_series.name = 'h_avg'
    file_name_end_series = grouped_df[date_time_col].last()
    file_name_df_time_indexed = pd.DataFrame(file_name_end_series.index.values, columns = ['end_times'],
                                             index=grouped_df[date_time_col].first().values)
    print "file_name_df_time_indexed", file_name_df_time_indexed.ix[0]
    file_name_max_series = pd.DataFrame(file_name_max_series).join(pd.DataFrame(file_name_avg_series))
    file_name_max_series = file_name_max_series.join(pd.DataFrame(file_name_std_df))
    file_name_max_series.index = grouped_df[date_time_col].first().values
    file_names_df = pd.DataFrame(grouped_df.file_name.values.values, columns = ['file_names'],
                                 index=grouped_df[date_time_col].first().values)
    file_name_max_series = file_name_max_series.join(file_names_df)
    print file_name_max_series
    print file_name_df_time_indexed
    file_name_df_max = file_name_df_time_indexed.join(file_name_max_series)
    print file_name_df_max.ix[0]

def iterate_over_buoys(buoys):
    for buoy_name in buoys:
        buoy_path = buoys_root_path + buoy_name
        years = os.listdir(buoy_path)
        large_dataframe = pd.DataFrame()
        for year in years:
            year_path = os.path.join(buoy_path, year)
            if os.path.isdir(year_path):
                    months = os.listdir(year_path)
                    for month in months:
                        month_path = os.path.join(year_path,month)
                        if os.path.isdir(month_path):
                            print month_path
                            os.chdir(month_path)
                            wave_height_df = pd.load('wave_height_dataframe')
                            large_dataframe = pd.concat([large_dataframe, 
                                                         wave_height_df])
        large_dataframe.save('large_wave_height_df')
        stats_dict = get_stats_from_df(large_dataframe, "wave_height_cm")
        arrays_to_df_excel(stats_dict, buoy_name, buoys_root_path)
        
def process_awac_wave_height():
    #concat all three datasets from the hebmarine awac together
    os.chdir(awac_root_path)
    wave_height_df = pd.load('hebmarine_awac_full_wave_height_dataframe')
    stats_dict = get_stats_from_df(wave_height_df, "wave_height_decibar")
    arrays_to_df_excel(stats_dict, 'hebmarine_awac', awac_root_path)
        
iterate_over_buoys(buoys)    
#process_awac_wave_height()
    