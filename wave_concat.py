"""
Module for concatenating wave_height_dataframes produced by raw_combined.py
Given a buoy root directory and buoy name the code will iterate over a list of 
buoys producing statistics for the concatenated wave_height_dataframes 
including h_max, h_1_3_mean and the time period these statistics cover. The 
statistics are then saved as a Pandas DataFrame and exported to Excel xlsx 
format. 

This process can also be carried out for the pressure data from a 
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


def get_stats_from_df_groupby(large_dataframe, series_name, path):
    '''Groups DataFrame by file_name, which should be approximately half hours
    Standard deviation, Maximum and Mean are extracted as series and joined 
    into DataFrame along with end_timestamps and start_timestamps and 
    file_names. DataFrame is then saved and exported as Excel workbook.
    '''
    new_cols = ['date_time_index']
    large_dataframe = large_dataframe.sort()
    large_dataframe = large_dataframe[large_dataframe.bad_wave==False]
    reset_index_df = large_dataframe.reset_index()
    cols = reset_index_df.columns.values
    [new_cols.append(x) for x in cols[1:]]
    reset_index_df.columns = new_cols
    grouped_df = reset_index_df.groupby('file_name')
    std_series = grouped_df[series_name].std()
    std_series.name = 'h_std'
    max_series = grouped_df[series_name].max()
    max_series.name = 'h_max'
    avg_series = grouped_df[series_name].mean()
    avg_series.name = 'h_avg'
    h_1_3_mean_series = grouped_df.wave_height_cm.apply(lambda x : x.order()[-(len(x)/3):].mean())    
    h_1_3_mean_series.name = 'h_1_3_mean'
    h_rms_series = grouped_df.wave_height_cm.apply(lambda x: np.sqrt((x**2).sum()/len(x)))
    h_rms_series.name = 'h_rms'
    end_timestamps_series = grouped_df[new_cols[0]].last()
    end_timestamps_series.name = 'end_times'
    start_timestamps = grouped_df[new_cols[0]].first().values
    avg_max_std_end_df = pd.concat([std_series, max_series, avg_series, 
                                    end_timestamps_series, h_1_3_mean_series, 
                                    h_rms_series], axis=1)
    avg_max_std_end_df.index = start_timestamps
    file_names_df = pd.DataFrame(grouped_df.file_name.size().index, 
                                 columns = ['file_names'], 
                                 index=start_timestamps)
    all_stats_df = avg_max_std_end_df.join(file_names_df)
    all_stats_df.to_excel(path + 'wave_h_groupby.xlsx')
    all_stats_df.save(path + 'stats_groupby_df')

def get_stats_from_df(large_dataframe, series_name, half_hourly = True):
    '''Old implementation still used with AWAC wad dataframe, AWAC process 
    needs updating to take advantage of groupby as in get_stats_from_df_groupby
    '''
    large_dataframe = large_dataframe.sort()
    
    stats_dict = {'start_times':[], 'end_times':[], 'h_max':[], 
                  'h_1_3_mean':[], 'h_avg':[], 'h_std':[]}
    if time_based_stats:                        
        
        timestamp = large_dataframe.ix[0].name
        last_timestamp = large_dataframe.ix[-1].name
        if half_hourly:
            time_set = 1800 
            first_nearest_halfhour = timestamp_to_nearest_half_hour(timestamp, time_set)
            last_nearest_halfhour = timestamp_to_nearest_half_hour(last_timestamp, time_set)
            index = np.arange(first_nearest_halfhour, last_nearest_halfhour, time_set)
            set_size = 'half_hour'
        else: 
            time_set = 3600
            index = np.arange(time.mktime(timestamp.timetuple()), time.mktime(last_timestamp.timetuple()), time_set)
            set_size = 'hour'
        stats_dict['set_size'] = set_size
    else:
        set_size = 100
        stats_dict['set_size'] = set_size
        index = np.arange(set_size,len(large_dataframe),set_size)
    for x in index:
        if time_based_stats:                   
            subset = large_dataframe.ix[datetime.utcfromtimestamp(x-time_set):datetime.utcfromtimestamp(x)]
        else:
            subset = large_dataframe.ix[x-set_size:x]
        if len(subset) != 0:
            stats_dict['start_times'].append(subset.index[0])
            stats_dict['end_times'].append(subset.index[-1])
            stats_dict['h_1_3_mean'].append(subset[series_name].order()[-(len(subset)/3):].mean())
            stats_dict['h_avg'].append(subset.mean()[0])
            stats_dict['h_std'].append(subset.std()[0])
            stats_dict['h_max'].append(subset.max()[0])
    "finished stats"
    return stats_dict 
    
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
        stats_dict = get_stats_from_df_groupby(large_dataframe, "wave_height_cm", buoys_root_path)
        
def process_awac_wave_height():
    #concat all three datasets from the hebmarine awac together
    os.chdir(awac_root_path)
    wave_height_df = pd.load('hebmarine_awac_full_wave_height_dataframe')
    stats_dict = get_stats_from_df(wave_height_df, "wave_height_decibar")
    arrays_to_df_excel(stats_dict, 'hebmarine_awac', awac_root_path)
        
iterate_over_buoys(buoys)    
#process_awac_wave_height()
    