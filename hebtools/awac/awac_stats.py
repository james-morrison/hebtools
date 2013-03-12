"""
Module for generating statistics dataframe for the pressure data from a 
Nortek AWAC wad file using the outputs of parse_wad.py 

@author: James Morrison
@license: MIT
"""

import os
import sys
import pandas as pd
import numpy as np
import time
from datetime import datetime
import logging
logging.basicConfig(stream=sys.stderr, level=logging.INFO)

time_based_stats = True
columns = ['start_times', 'end_times', 'h_max', 'h_1_3_mean', 'h_avg', 'h_std']

def timestamp_to_half_hour(timestamp, set_length_seconds):
    unix_timestamp = time.mktime(timestamp.timetuple())
    return round( unix_timestamp / set_length_seconds ) * set_length_seconds

def arrays_to_df_excel(stats_dict, awac_name, path):
    index_df = pd.DatetimeIndex(stats_dict['start_times'])
    stats_dfs = []
    for column in columns:
        stats_dfs.append(pd.DataFrame(stats_dict[column], 
                                     columns=[column]))
                                     
    set_df = pd.concat(stats_dfs, axis=1)
    set_df = set_df.set_index(columns[0])
    file_name = 'wave_h_' + str(stats_dict['set_size']) + '_set_' + awac_name
    set_df.save(file_name)
    set_df.to_excel(file_name + '.xlsx')


def get_stats_from_df(large_dataframe, series_name, half_hourly = True):
    """ Generates statistics ( defaulting to half hourly ) for awac wave 
    heights """
    large_dataframe = large_dataframe.sort()
    stats_dict = dict([(column,[]) for column in columns])

    if time_based_stats:                          
        timestamp = large_dataframe.ix[0].name
        last_timestamp = large_dataframe.ix[-1].name
        if half_hourly:
            time_set = 1800 
            first_halfhour = timestamp_to_half_hour(timestamp, time_set)
            last_halfhour = timestamp_to_half_hour(last_timestamp, time_set)
            index = np.arange(first_halfhour, last_halfhour + time_set, 
                              time_set)
            set_size = 'half_hour'
        else: 
            time_set = 3600
            index = np.arange(time.mktime(timestamp.timetuple()), 
                              time.mktime(last_timestamp.timetuple()), 
                              time_set)
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
            stats_dict[columns[0]].append(subset.index[0])
            stats_dict[columns[1]].append(subset.index[-1])
            stats_dict[columns[2]].append(subset.max()[0])
            stats_dict[columns[3]].append(subset[series_name].order()[-(len(subset)/3):].mean())
            stats_dict[columns[4]].append(subset.mean()[0])
            stats_dict[columns[5]].append(subset.std()[0])
    logging.info("finished stats")
    return stats_dict 

def process_wave_height(awac_path):
    awac_path = os.path.normpath(awac_path)
    path = os.path.sep.join(awac_path.split(os.path.sep)[:-1])
    os.chdir(path)
    awac_file_name = awac_path.split(os.path.sep)[-1:][0]
    wave_height_df = pd.load(awac_file_name)
    stats_dict = get_stats_from_df(wave_height_df, "wave_height_decibar")
    arrays_to_df_excel(stats_dict, 'test_awac', path)

if __name__ == "__main__":
    if len(sys.argv) == 1: 
        print "No path to wad file passed"     
    else:
       process_wave_height(sys.argv[1])