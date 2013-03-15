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

def get_func_list():
    def first(x): return x.index[0]
    def last(x): return x.index[-1]
    def max(x): return x.max()
    def h_1_3(x): return x.order()[-(len(x)/3):].mean()
    def mean(x): return x.mean()
    def std(x): return x.std()    
    return [first, last, h_1_3, max, mean, std]

def time_stats(large_dataframe, half_hourly, series_name):    
    if half_hourly:
        interval = "30min"
    else:       
        interval = "1H"
    grouped_df_time = large_dataframe.groupby(pd.TimeGrouper(interval))
    series_list = []
    func_list = get_func_list()
    for func in func_list:
        series_list.append(grouped_df_time[series_name].apply(func))
    stats_df = pd.concat(series_list, axis=1)
    stats_df.columns = columns
    file_name = 'awac_stats_' + interval
    stats_df.save(file_name)
    stats_df.save(file_name + '.xlsx')

def get_stats_from_df(large_dataframe, series_name, path, half_hourly = True):
    """ Generates statistics ( defaulting to half hourly ) for awac wave 
    heights """
    large_dataframe = large_dataframe.sort()
    stats_dict = dict([(column,[]) for column in columns])
    if time_based_stats:                          
        time_stats(large_dataframe, half_hourly, series_name)
    else:
        set_size = 100
        stats_dict['set_size'] = set_size
        #index = np.arange(set_size,len(large_dataframe),set_size)
        df_list = np.array_split(large_dataframe,np.arange(0,len(large_dataframe),
                       set_size))[1:]
        for subset in df_list:
            if len(subset) != 0:
                for index, func in enumerate(get_func_list()):       
                    stats_dict[columns[index]].append(func(subset))
        arrays_to_df_excel(stats_dict, 'awac', path)
    logging.info("finished stats")

def process_wave_height(awac_path):
    awac_path = os.path.normpath(awac_path)
    path = os.path.sep.join(awac_path.split(os.path.sep)[:-1])
    os.chdir(path)
    awac_file_name = awac_path.split(os.path.sep)[-1:][0]
    wave_height_df = pd.load(awac_file_name)
    get_stats_from_df(wave_height_df, "wave_height_decibar", path)
    

if __name__ == "__main__":
    if len(sys.argv) == 1: 
        print "No path to wad file passed"     
    else:
       process_wave_height(sys.argv[1])