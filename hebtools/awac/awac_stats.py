"""
Module for generating statistics dataframe for the pressure data from a 
Nortek AWAC wad file using the outputs of parse_wad.py 

@author: James Morrison
@license: MIT
"""

import os
import pandas as pd
import numpy as np
import time
from datetime import datetime

time_based_stats = True

def timestamp_to_nearest_half_hour(timestamp, set_length_seconds):
    unix_timestamp = time.mktime(timestamp.timetuple())
    return round( unix_timestamp / set_length_seconds ) * set_length_seconds

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


def get_stats_from_df(large_dataframe, series_name, half_hourly = True):
    ''' AWAC process should be updated to use groupby as in 
        wave_concat.get_stats_from_df_groupby described in Issue #18
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

def process_awac_wave_height(awac_root_path):
    #concat all three datasets from the hebmarine awac together
    os.chdir(awac_root_path)
    wave_height_df = pd.load('hebmarine_awac_full_wave_height_dataframe')
    stats_dict = get_stats_from_df(wave_height_df, "wave_height_decibar")
    arrays_to_df_excel(stats_dict, 'hebmarine_awac', awac_root_path)

if __name__ == "__main__":
    if len(sys.argv) == 1: 
        awac_root_path = 'D:\\awac_time_series\\'     
    else:
       awac_root_path = sys.argv[1] 
    process_awac_wave_height(awac_root_path)    