# -*- coding: utf-8 -*-
"""This modules takes a folder_path to a buoy month directory, iterates over the 
files, creates a pandas DataFrame for each month and saves it in the month 
folder. The pandas DataFrame is time indexed to nearest tenth of a second 
second, with columns for signal_quality, heave, north, west. 

A numpy file 'prob_files.npy' is saved containing a simple 1d array, listing 
files which have structure errors, so their data is unable to be included in the 
DataFrame. The heave timeseries of the DataFrame is then checked to find peaks
and troughs, those identified are then added as a column 'extrema' to the 
orginal data and saved again. 

Data which has a non zero status signal and values which deviate more than four
times from the standard deviation are then masked from calculations. The masked
data containing extrema is then used to calculate, wave heights and zero 
crossing periods along with their approximate timestamps.

@author: James Morrison
@license: MIT
"""

import numpy as np
import calendar
from datetime import datetime
import os
import glob
import pandas as pd
folder_path = 'D:\New_Datawell\Roag_Wavegen'
import wave_stats
import error_check
import extrema
        
class Load_Raw_Files:
    
    def __init__(self, folder_path):    
        self.iterate_over_months(folder_path)
  
    def get_rounded_timestamps(self, file_name, raw_array_length):
        """ Takes the length of the raw file and based on the file name gives the
        start timestamp and the raw records are assumed to be sent every 0.78125 
        seconds or 1.28Hz, returns a list of UTC datetimes """
        date_time = datetime.strptime(file_name.split('}')[1][:-5], "%Y-%m-%dT%Hh%M")
        if raw_array_length < 2300:
            time_interval = 0.78125
        else:
            time_interval = 1800/float(raw_array_length)
        unix_timestamp = calendar.timegm(date_time.timetuple())
        time_index = np.linspace(unix_timestamp, 
                                 unix_timestamp + raw_array_length*time_interval - time_interval, 
                                 raw_array_length)
        time_index = [round(x*10.0)/10.0 for x in time_index]    
        utc_timestamps = [datetime.utcfromtimestamp(x) for x in time_index]
        return utc_timestamps

    def iterate_over_file_names(self, path):
        raw_cols = ['sig_qual','heave','north','west']
        os.chdir(path)
        problem_files = []
        file_names = glob.glob('*.raw')
        file_names.sort()
        big_raw_array = pd.DataFrame(columns = raw_cols)
        small_raw_array = pd.DataFrame(columns = raw_cols)
        for index, filepath in enumerate(file_names):
            try:
                raw_file = open(filepath)
                raw_records = raw_file.readlines()
                if len(raw_records) == 0:
                    continue
                records = []
                for record in raw_records:
                    record_list = record.split(',')
                    # Checking that record is valid format
                    if len(record_list) == 4:
                        new_array = []
                        bad_record = False
                        for value in record_list:
                            value = value.strip()
                            if value == '' or 'E' in value:
                                bad_record = True
                            else:
                                new_array.append(long(value.strip('\n')))
                        if not bad_record:
                            records.append(new_array)
                raw_array = pd.DataFrame(records,columns=raw_cols,dtype=np.int)
            except StopIteration:
                print(filepath, "StopIteration")
                problem_files.append(filepath)
                continue
            raw_file_length = len(raw_array)
            if raw_file_length > 2500 or raw_file_length == 0:
                print("Possibly serious errors in transmission")
                problem_files.append(filepath)
                continue
            raw_array.index = self.get_rounded_timestamps(filepath, len(raw_array))
            big_raw_array = big_raw_array.append( raw_array )
        big_raw_array.save('raw_buoy_displacement_pandas')  
        np.save("prob_files",np.array(problem_files))
        print("finish iterate_over_files")
        return big_raw_array

 
        
    def iterate_over_months(self, folder_path):
        dirs = os.listdir(folder_path)    
        for x in dirs:
            month_dirs = os.listdir(os.path.join(folder_path,x))
            for month_dir in month_dirs:
                path = os.path.join(folder_path,x,month_dir)
                print(path)
                month_raw_displacements = self.iterate_over_file_names(path)
                extrema_df = extrema.Get_Extrema(month_raw_displacements)
                error_df = error_check.Error_Check(extrema_df.raw_disp_with_extrema)
                wave_stats.Wave_Stats(error_df.raw_plus_std)
        
Load_Raw_Files(folder_path)