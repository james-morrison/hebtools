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
from datetime import datetime
import calendar
import os
import glob
import pandas as pd
from matplotlib.mlab import find
folder_path = 'D:\Datawell\Roag_Wavegen' 

class Wave_Stats:
    
    def __init__(self, raw_disp):    
        self.raw_disp = raw_disp
        self.calc_stats()
        self.get_zero_upcross_periods()
    
    def get_zero_upcross_periods(self):
        print("start get_zero_upcross_periods")
        """ Based on code from https://gist.github.com/255291"""
        timestamps = [calendar.timegm(x.utctimetuple()) for x in self.raw_disp.index]
        heave = self.raw_disp['heave']
        indices = find((heave[1:]>=0)&(heave[:-1]<0))
        crossings = [i - heave[i] / (heave[i+1] - heave[i]) for i in indices]
        np.save('crossings',crossings)
        zero_crossing_timestamps = []
        for crossing in crossings:
            #Check if zero cross occurs at the end of the time-series
            if crossing+1 == len(timestamps):
                zero_crossing_timestamps.append(timestamps[int(crossing)])
            else:
                difference = timestamps[int(crossing)]-timestamps[int(crossing+1)]
                fraction = crossing-int(crossing)
                zero_crossing_timestamps.append(timestamps[int(crossing)] + difference * fraction)
        zero_crossing_timestamps_np = np.array(zero_crossing_timestamps)
        zero_upcross_periods = np.ediff1d(zero_crossing_timestamps_np)
        zero_crossing_timestamps = [datetime.utcfromtimestamp(x) for x in zero_crossing_timestamps]
        df = pd.DataFrame(zero_upcross_periods, index = zero_crossing_timestamps[:-1])
        df.save('zero_crossing_dataframe')    
        
    def calc_stats(self):
        print("start calc_stats")
        # wave heights are calculated from peak to trough
        accompanying_extrema = self.find_accompanying_false_extrema()
        extrema = self.raw_disp.join(accompanying_extrema)
        extrema.save('pre_extrema')
        extrema = extrema.ix[np.invert(np.isnan(extrema['extrema']))]
        extrema = extrema.ix[extrema['signal_error']==False]
        extrema = extrema.ix[extrema['>4*std']==False]
        extrema = extrema.ix[extrema['accompanying_false_extrema']==False]
        extrema.save('extrema')
        differences = np.ediff1d(np.array(extrema['heave']))
        wave_height_timestamps = extrema.index[differences<0]
        wave_heights = np.absolute(differences[differences<0])
        wave_height_dataframe = pd.DataFrame(wave_heights, columns=['wave_height_cm'], index = wave_height_timestamps)    
        wave_height_dataframe.save('wave_height_dataframe')
    
    def find_accompanying_false_extrema(self):
        # This function selects peaks, and for those with signal_error True or 
        # >4*std True masks the following trough and then for all troughs with
        # signal_error True or >4*std True mask the preceding peak
        peaks = self.raw_disp[self.raw_disp['extrema']==1]
        false_peaks = peaks[peaks['signal_error']==True]
        false_peaks_std = peaks[peaks['>4*std']==True]
        false_peaks = false_peaks.combine_first(false_peaks_std)
        false_peak_index = false_peaks.index
        troughs = self.raw_disp[self.raw_disp['extrema']==-1]
        indexes = []
        for index_of_false_peak in false_peak_index:
            if len(troughs.ix[index_of_false_peak:])!=0:
                indexes.append(troughs.ix[index_of_false_peak:].ix[0].name)
        false_troughs = troughs[troughs['signal_error']==True]
        false_troughs_std = troughs[troughs['>4*std']==True]
        false_troughs.combine_first(false_troughs_std)
        false_trough_index = false_troughs.index
        for index_of_false_trough in false_trough_index:
            if len(peaks.ix[:index_of_false_trough])!=0:
                indexes.append(peaks.ix[:index_of_false_trough].ix[-1].name)
        boolean_array = self.raw_disp.index == indexes[0]
        for x in indexes[1:]:
            boolean_array += self.raw_disp.index == x
        return pd.DataFrame(boolean_array, index = self.raw_disp.index, 
                            columns = ['accompanying_false_extrema'])


class Get_Extrema():

    def __init__(self, raw_displacements):    
        self.raw_displacements = raw_displacements
        self.get_peaks()
    
    def _datacheck_peakdetect(self, x_axis, y_axis):
        if x_axis is None:
            x_axis = list(range(len(y_axis)))
        
        if len(y_axis) != len(x_axis):
            raise ValueError
        
        #needs to be a numpy array
        y_axis = np.array(y_axis)
        x_axis = np.array(x_axis)
        return x_axis, y_axis
        
    def peakdetect(self, y_axis, x_axis = None, lookahead = 4, delta=0):
        """
        Converted from/based on a MATLAB script at: 
        http://billauer.co.il/peakdet.html
        
        function for detecting local maximas and minmias in a signal.
        Discovers peaks by searching for values which are surrounded by lower
        or larger values for maximas and minimas respectively
        
        keyword arguments:
        y_axis -- A list containg the signal over which to find peaks
        x_axis -- (optional) A x-axis whose values correspond to the y_axis list
            and is used in the return to specify the postion of the peaks. If
            omitted an index of the y_axis is used. (default: None)
        lookahead -- (optional) distance to look ahead from a peak candidate to
            determine if it is the actual peak (default: 200) 
            '(sample / period) / f' where '4 >= f >= 1.25' might be a good value
        delta -- (optional) this specifies a minimum difference between a peak and
            the following points, before a peak may be considered a peak. Useful
            to hinder the function from picking up false peaks towards to end of
            the signal. To work well delta should be set to delta >= RMSnoise * 5.
            (default: 0)
                delta function causes a 20% decrease in speed, when omitted
                Correctly used it can double the speed of the function
        
        return -- two lists [max_peaks, min_peaks] containing the positive and
            negative peaks respectively. Each cell of the lists contains a tupple
            of: (position, peak_value) 
            to get the average peak value do: np.mean(max_peaks, 0)[1] on the
            results to unpack one of the lists into x, y coordinates do: 
            x, y = zip(*tab)
        """
        max_peaks = []
        min_peaks = []
        dump = []   #Used to pop the first hit which almost always is false
           
        # check input data
        x_axis, y_axis = self._datacheck_peakdetect(x_axis, y_axis)
        # store data length for later use
        length = len(y_axis)
        
        
        #perform some checks
        if lookahead < 1:
            raise ValueError("Lookahead must be '1' or above in value")
        if not (np.isscalar(delta) and delta >= 0):
            raise ValueError("delta must be a positive number")
        
        #maxima and minima candidates are temporarily stored in
        #mx and mn respectively
        mn, mx = np.Inf, -np.Inf
        
        #Only detect peak if there is 'lookahead' amount of points after it
        for index, (x, y) in enumerate(list(zip(x_axis[:-lookahead], 
                                            y_axis[:-lookahead]))):
            if y > mx:
                mx = y
                mxpos = x
            if y < mn:
                mn = y
                mnpos = x
            
            ####look for max####
            try:
                if y < mx-delta and mx != np.Inf:
                    #Maxima peak candidate found
                    #look ahead in signal to ensure that this is a peak and not jitter
                    if y_axis[index:index+lookahead].max() < mx:
                        max_peaks.append([mxpos, mx])
                        dump.append(True)
                        #set algorithm to only find minima now
                        mx = np.Inf
                        mn = np.Inf
                        if index+lookahead >= length:
                            #end is within lookahead no more peaks can be found
                            break
                        continue
                    #else:  #slows shit down this does
                    #    mx = ahead
                    #    mxpos = x_axis[np.where(y_axis[index:index+lookahead]==mx)]
                
                ####look for min####
                if y > mn+delta and mn != -np.Inf:
                    #Minima peak candidate found 
                    #look ahead in signal to ensure that this is a peak and not jitter
                    if y_axis[index:index+lookahead].min() > mn:
                        min_peaks.append([mnpos, mn])
                        dump.append(False)
                        #set algorithm to only find maxima now
                        mn = -np.Inf
                        mx = -np.Inf
                        if index+lookahead >= length:
                            #end is within lookahead no more peaks can be found
                            break
                    #else:  #slows shit down this does
                    #    mn = ahead
                    #    mnpos = x_axis[np.where(y_axis[index:index+lookahead]==mn)]
        
            except TypeError:
                print(type(y), y)
                print(type(delta), delta)
                print(type(mx), mx)
                print(type(np.Inf), np.Inf)            
        #Remove the false hit on the first value of the y_axis
        try:
            if dump[0]:
                max_peaks.pop(0)
            else:
                min_peaks.pop(0)
            del dump
        except IndexError:
            #no peaks were found, should the function return empty lists?
            pass
            
        return [max_peaks, min_peaks]
    
    def get_extrema_timestamps(self, extrema, index):
        indexes = [x[0] for x in extrema]
        timestamps = [index[z] for z in indexes]
        return timestamps
    
    def get_extrema_df(self, extrema_index, index, extrema_type):
        extrema_timestamps = self.get_extrema_timestamps(extrema_index, index)
        return pd.DataFrame(np.ones(len(extrema_index), dtype=np.int64), 
                            columns = ['extrema'], 
                            index = extrema_timestamps)*extrema_type
    
    def get_peaks(self):
        print("start get_peaks")
        y = self.raw_displacements['heave']
        index = self.raw_displacements.index
        _max, _min = self.peakdetect(y)
        maxima_df = self.get_extrema_df(_max, index, 1 )
        minima_df = self.get_extrema_df(_min, index, -1 )
        extrema_df = pd.concat([maxima_df, minima_df])
        raw_disp_with_extrema = self.raw_displacements.join(extrema_df)
        raw_disp_with_extrema = raw_disp_with_extrema.sort()
        self.raw_disp_with_extrema = raw_disp_with_extrema

class Error_Check():

    def __init__(self, extrema_df):    
        self.detect_error_waves(extrema_df)
        self.detect_4_by_std()
        
    def detect_error_waves(self, extrema_df):
        """Find values with status signal problem and is a peak or trough,
        then adds a 'signal_error' boolean column to the DataFrame
        """
        print "start detect_error_waves"
        error_wave_mask = extrema_df['sig_qual']>0
        error_waves_df = pd.DataFrame(error_wave_mask ,columns=['signal_error'], index = extrema_df.index )
        # bad_extrem_indexes = np.where(error_wave_mask==True)
        # bad_waves = []
        # for index in bad_extrem_indexes[0]:
            # extrema_type = extrema_df['extrema'].ix[index]
            # bad_waves.append(index)
            # if extrema_type == -1:
                # bad_waves.append(index+1)
            # else:
                # bad_waves.append(index-1)	
        # boolean_error_waves = []
        # for element in range(len(extrema_df)):
            # boolean_error_waves.append(False)
        # boolean_error_waves_array = np.array(boolean_error_waves)
        # for element in bad_waves:
            # boolean_error_waves_array[element] = True
        # error_waves_df = pd.DataFrame(boolean_error_waves_array ,columns=['signal_error'], index = extrema_df.index )
        extrems_plus_errors = extrema_df.join(error_waves_df)
        extrems_plus_errors = extrems_plus_errors.sort()
        extrems_plus_errors.save('self.extrems_plus_errors_with_extrema_and_errors')	
        self.extrema_with_errors = extrems_plus_errors

    def compare_std(self, disp_set):
        """Compare values with the calculated four times standard deviation, 
        returning a boolean array, if any values exceeds the comparison, 
        that value for that record is stored as True, with the implication
        that the record should be masked
        """
        mask = np.array([])
        columns = ['heave', 'north', 'west']
        for column in columns:
            four_times_heave_std = disp_set[column].std() * 4
            if not np.isnan(four_times_heave_std):
                if len(mask)==0:
                    mask = disp_set[column].abs() > four_times_heave_std
                else:
                    new_mask = disp_set[column].abs() > four_times_heave_std
                    mask += new_mask
        return mask

    
    def detect_4_by_std(self):
        """This function iterates through the displacements DataFrame in 2304 
        long sets, generating statistics for each set including standard 
        deviation the heave displacements are then compared against 4 times 
        their standard deviation 
        """
        print "detect_4_by_std"
        raw_set_length = 2304
        four_times_std_heave_30_mins = []
        for x in range(0, len(self.extrema_with_errors), raw_set_length):
            end_index = x+raw_set_length
            if end_index > len(self.extrema_with_errors):
                disp_set = self.extrema_with_errors.ix[x:]
            else:
                disp_set = self.extrema_with_errors.ix[x:end_index]
            mask = self.compare_std(disp_set)
            if len(mask) != 0:
                four_times_std_heave_30_mins.append(mask)    
        flat_four_times_std = pd.concat(four_times_std_heave_30_mins)
        flat_four_times_std.name=['>4*std']
        flat_four_times_std = pd.DataFrame(flat_four_times_std)
        raw_plus_std = self.extrema_with_errors.join(flat_four_times_std)
        raw_plus_std.save('raw_plus_std')
        self.raw_plus_std = raw_plus_std

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
                extrema = Get_Extrema(month_raw_displacements)
                error_check = Error_Check(extrema.raw_disp_with_extrema)
                wave_stats = Wave_Stats(error_check.raw_plus_std)
        
Load_Raw_Files(folder_path)