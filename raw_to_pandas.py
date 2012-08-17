# -*- coding: utf-8 -*-
"""
Created on Fri Jul 27 15:52:46 2012

Modules takes path to a buoy year directory, iterates over months and creates
a pandas and numpy array file for each month and save it in the month folder. 
The pandas file contains a DataFrame time indexed to nearest half second, with 
columns for signal_quality, heave, north, west. The numpy file contains a
simple 1d array listing files which have structure errors and their data is 
unable to be included in the pandas file.

@author: James Morrison

"""
import numpy as np
from datetime import datetime
import calendar
import os
import glob
import pandas as pd
folder_path = 'D:\\path\\to\\buoy_year_folder\\'
dirs = os.listdir(folder_path)
    
template = "%Y-%m-%dT%Hh%M"

def get_rounded_timestamps(file_name, raw_array_length):
    """ Takes the length of the raw file and based on the file name gives the
    start timestamp and the raw records are assumed to be sent every 0.78125 
    seconds or 1.28Hz, returns a list of UTC datetimes """
    date_time = datetime.strptime(file_name.split('}')[1][:-5], template)
    time_interval = 0.78125
    if raw_array_length == 2305:
        """ Due to signals being sent more frequently than every second some 
        half hour files contain one more record and a slightly shorter interval
        (1800/2305) takes account of this """
        time_interval = 0.7809110629
    unix_timestamp = calendar.timegm(date_time.timetuple())
    time_index = np.linspace(unix_timestamp, 
                             unix_timestamp + raw_array_length*time_interval - time_interval, 
                             raw_array_length)
    time_index = [round(x*2.0)/2.0 for x in time_index]    
    utc_timestamps = [str(datetime.utcfromtimestamp(x)) for x in time_index]
    return utc_timestamps

def iterate_over_file_names(path):
    raw_cols = ['sig_qual','heave','north','west']
    os.chdir(path)
    problem_files = []
    file_names = glob.glob('*.raw')
    big_raw_array = pd.DataFrame(columns = raw_cols)
    for index, filepath in enumerate(file_names):
        print filepath
        try:
            raw_array = pd.io.parsers.read_csv(filepath,names=raw_cols)
        except StopIteration:
            print filepath, "StopIteration"
            problem_files.append(filepath)
            continue
        raw_file_length = len(raw_array)
        print raw_file_length
        if raw_file_length > 2500 or raw_file_length == 0:
            print "Possibly serious errors in transmission"
            problem_files.append(filepath)
            continue
        raw_array.index = get_rounded_timestamps(filepath, len(raw_array))
        big_raw_array = pd.concat([big_raw_array, raw_array])
    big_raw_array.save('raw_buoy_displacement_pandas')  
    np.save("prob_files",np.array(problem_files))
    
for x in dirs:
    path = os.path.join(folder_path, x)
    iterate_over_file_names(path)