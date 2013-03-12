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


def get_stats_from_df(large_dataframe, series_name, path, half_hourly = True):
    """ Generates statistics ( defaulting to half hourly ) for awac wave 
    heights """
    large_dataframe = large_dataframe.sort()
    stats_dict = dict([(column,[]) for column in columns])
    print "large_df", os.getcwd()
    large_dataframe.save('large_dataframe')
    if time_based_stats:                          
        timestamp = large_dataframe.ix[0].name
        last_timestamp = large_dataframe.ix[-1].name
        if half_hourly:
            set_size = 'half_hour'
            grouper = pd.TimeGrouper("30min")
        else:
            set_size = 'half_hour'        
            grouper = pd.TimeGrouper("1H")
        stats_dict['set_size'] = set_size
    else:
        set_size = 100
        stats_dict['set_size'] = set_size
        index = np.arange(set_size,len(large_dataframe),set_size)
    if time_based_stats:
        print large_dataframe
        grouped_df_time = large_dataframe.groupby(grouper)
        series_list = []
        series_list.append(grouped_df_time[series_name].apply(lambda x : x.index[0]))
        series_list.append(grouped_df_time[series_name].apply(lambda x : x.index[-1]))
        series_list.append(grouped_df_time[series_name].apply(lambda x : x.order()[-(len(x)/3):].mean()))
        series_list.append(grouped_df_time.max())
        series_list.append(grouped_df_time.mean())
        series_list.append(grouped_df_time.std())
        stats_df = pd.concat(series_list, axis=1)
        stats_df.columns = columns
        stats_df.save('test')
        stats_df.save('test.xlsx')
    else:
        for x in index:
            subset = large_dataframe.ix[x-set_size:x]
            if len(subset) != 0:
                stats_dict[columns[0]].append(subset.index[0])
                stats_dict[columns[1]].append(subset.index[-1])
                stats_dict[columns[2]].append(subset.max()[0])
                stats_dict[columns[3]].append(subset[series_name].order()[-(len(subset)/3):].mean())
                stats_dict[columns[4]].append(subset.mean()[0])
                stats_dict[columns[5]].append(subset.std()[0])
        arrays_to_df_excel(stats_dict, 'test_awac', path)
    logging.info("finished stats")
    return stats_dict 

def process_wave_height(awac_path):
    awac_path = os.path.normpath(awac_path)
    path = os.path.sep.join(awac_path.split(os.path.sep)[:-1])
    os.chdir(path)
    awac_file_name = awac_path.split(os.path.sep)[-1:][0]
    wave_height_df = pd.load(awac_file_name)
    stats_dict = get_stats_from_df(wave_height_df, "wave_height_decibar", path)
    

if __name__ == "__main__":
    if len(sys.argv) == 1: 
        print "No path to wad file passed"     
    else:
       process_wave_height(sys.argv[1])