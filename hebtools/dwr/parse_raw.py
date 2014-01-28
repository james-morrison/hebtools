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
import sys
import glob
import pandas as pd
from . import error_check
from . import problem_files
from hebtools.common.wave_stats import WaveStats
from hebtools.common.extrema import GetExtrema
import logging
logging.basicConfig(stream=sys.stderr, level=logging.INFO)

def iter_loadtxt(filename, skiprows=0, dtype=np.int):
    """ This function is adapted from Joe Kington's example on Stack Overflow
    http://stackoverflow.com/q/8956832/ """
    def iter_func():
        with open(filename, 'r') as infile:
            for _ in range(skiprows):
                next(infile)
            for line in infile:
                line = line.rstrip().split(',') 
                if len(line)==4:                
                    for item in line:
                        try:                        
                            yield dtype(item)
                        except ValueError:
                            logging.info("Bad Record")
                            yield dtype(0)

    data = np.fromiter(iter_func(), dtype=dtype)
    data = data.reshape((-1, 4))
    return data
        
def load(folder_path, year = None, month = None):
    
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
        DataFrame after each successful return from iterate_over_file """
        raw_cols = ['sig_qual','heave','north','west']
        os.chdir(path)
        file_names = glob.glob('*.raw')
        file_names.sort()
        files = []
        problem_files_arr = []
        for index, filepath in enumerate(file_names):
            raw_array, prob_file = iterate_over_file(filepath, raw_cols)
            if prob_file:
                problem_files_arr.append(filepath)
            else:
                files.append( raw_array )
        displacements_df = pd.concat(files)
        displacements_df.to_hdf('buoy_data.h5','displacements', format='t',
                                append=False, complib='blosc', complevel=9)
        pd.DataFrame(problem_files_arr).to_hdf('buoy_data.h5', 'problem_files')
        logging.info("finish iterate_over_files")
        return displacements_df
        
    def iterate_over_file(filepath, raw_cols):
        try:
            raw_array = pd.DataFrame(iter_loadtxt(filepath) ,columns=raw_cols)
            file_name_df = pd.DataFrame([filepath]*len(raw_array),columns=['file_name'])
            raw_array = raw_array.join(file_name_df)
        except StopIteration:
            logging.info(filepath, "StopIteration")
            return None, True
        raw_file_length = len(raw_array)
        if raw_file_length > 2500 or raw_file_length == 0:
            logging.info("Possibly serious errors in transmission")
            return None, True
        raw_array.index = get_rounded_timestamps(filepath, len(raw_array))
        
        return raw_array, False        
    
    def iterate_over_years(year, folder_path):
        if month != None and year != None:
            process_month(os.path.join(folder_path,str(year),str(month)))
        elif year != None:
            iterate_over_months(os.path.join(folder_path,str(year)))
        else:
            year_dirs = os.listdir(folder_path)
            for year_dir in year_dirs:
                year_path = os.path.join(folder_path,year_dir)
                if os.path.isdir(year_path):
                    iterate_over_months(year_path)
            problem_files.concat('.')
        
    def iterate_over_months(year_folder_path):
        logging.info(year_folder_path)
        month_dirs = os.listdir(year_folder_path)
        for month_dir in month_dirs:
            path = os.path.join(year_folder_path,month_dir)
            if os.path.isdir(path):
                process_month(path)
                
    def process_month(month_path):
        month_raw_displacements = iterate_over_file_names(month_path)
        extrema_df = GetExtrema(month_raw_displacements)
        raw_plus_std = error_check.check(extrema_df.raw_disp_with_extrema)
        WaveStats(raw_plus_std)

    starting_path = os.path.abspath('.') 
    iterate_over_years(year, folder_path)
    os.chdir(starting_path)
