# -*- coding: utf-8 -*-
"""The class Load_Raw_Files takes a buoy directory path as a parameter and the
optional parameter of a year, the class will then iterate over the specified 
years or months and load the raw files for each month into a time indexed 
pandas DataFrame saved in that specific month folder. The DataFrame contains
columns for signal status, heave, north, west. 

A numpy file 'prob_files.npy' is saved containing a simple 1d array, listing 
files which have structure errors, meaning their data is unable to be 
included in the DataFrame. 

The module extrema is then called checked to find local peaks and troughs, 
those identified are then added as a column 'extrema' to the orginal DataFrame. 

Local extrema which have a non zero status signal and values which deviate more
than four times from the standard deviation and their corresponding local 
extrema can then be masked from calculations. The module wave_stats uses the 
masked displacement data which is then used to calculate a time series of wave 
heights and zero crossing periods.

@author: James Morrison
@license: MIT
"""

import numpy as np
import calendar
from datetime import datetime
import os
import glob
import sys
import pandas as pd
import error_check
from hebtools.common.wave_stats import WaveStats
from hebtools.common.extrema import GetExtrema
        
def load(folder_path, year = None):
    
    def get_rounded_timestamps(file_name, raw_array_length):
        """ Takes the length of the raw file and based on the file name gives 
        the start timestamp and the raw records are assumed to be sent every 
        0.78125 seconds or 1.28Hz, returns a list of UTC datetimes """
        date_time = datetime.strptime(file_name.split('}')[1][:-5], 
                                      "%Y-%m-%dT%Hh%M")
        if raw_array_length < 2300:
            time_interval = 0.78125
        else:
            time_interval = 1800/float(raw_array_length)
        unix_timestamp = calendar.timegm(date_time.timetuple())
        time_index = np.linspace(unix_timestamp, 
                                 unix_timestamp + raw_array_length * 
                                 time_interval - time_interval, 
                                 raw_array_length)
        time_index = [round(x*10.0)/10.0 for x in time_index]    
        utc_timestamps = [datetime.utcfromtimestamp(x) for x in time_index]
        return utc_timestamps

    def iterate_over_file_names(path):
        """ Iterates over one months worth of raw files, appending to a pandas
        DataFrame after each successfull return from iterate_over_file """
        raw_cols = ['sig_qual','heave','north','west']
        os.chdir(path)
        problem_files = []
        file_names = glob.glob('*.raw')
        file_names.sort()
        big_raw_array = pd.DataFrame(columns = raw_cols)
        files = []
        for index, filepath in enumerate(file_names):
            raw_array, prob_file = iterate_over_file(filepath, raw_cols)
            if prob_file:
                problem_files.append(filepath)
            else:
                files.append( raw_array )
        big_raw_array = pd.concat(files)
        big_raw_array.save('raw_buoy_displacement_pandas')  
        np.save("prob_files",np.array(problem_files))
        print("finish iterate_over_files")
        return big_raw_array
        
    def iterate_over_file(filepath, raw_cols):
        try:
            raw_file = open(filepath)
            raw_records = raw_file.readlines()
            if len(raw_records) == 0:
                return None, True
            records = []
            for record in raw_records:
                returned_record = parse_record(record)
                if returned_record:
                    records.append(returned_record)
            raw_array = pd.DataFrame(records,columns=raw_cols,dtype=np.int)
            file_name_df = pd.DataFrame([filepath]*len(records),columns=['file_name'])
            raw_array = raw_array.join(file_name_df)
        except StopIteration:
            print(filepath, "StopIteration")
            return None, True
        raw_file_length = len(raw_array)
        if raw_file_length > 2500 or raw_file_length == 0:
            print("Possibly serious errors in transmission")
            return None, True
        raw_array.index = get_rounded_timestamps(filepath, len(raw_array))
        
        return raw_array, False
        
    def parse_record(record):
        record_list = record.split(',')
        # Checking that record is valid format
        if len(record_list) == 4:
            new_array = []
            for value in record_list:
                value = value.strip()
                if value == '' or 'E' in value:
                    return None
                else:
                    new_array.append(long(value.strip('\n')))
            return new_array
        return None
    
    def iterate_over_years(year, folder_path):
        if year != None:
            iterate_over_months(os.path.join(folder_path,str(year)))
        else:
            year_dirs = os.listdir(folder_path)
            for year_dir in year_dirs:
                iterate_over_months(os.path.join(folder_path,year_dir))
        
    def iterate_over_months(year_folder_path):
        print year_folder_path
        month_dirs = os.listdir(year_folder_path)
        for month_dir in month_dirs:
            path = os.path.join(year_folder_path,month_dir)
            if os.path.isdir(path):
                month_raw_displacements = iterate_over_file_names(path)
                extrema_df = GetExtrema(month_raw_displacements)
                raw_plus_std = error_check.check(extrema_df.raw_disp_with_extrema)
                WaveStats(raw_plus_std)
               
    iterate_over_years(year, folder_path)
