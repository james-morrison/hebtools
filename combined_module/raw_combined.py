# -*- coding: utf-8 -*-
"""
Created on Fri Jul 27 15:52:46 2012

This modules takes a folder_path to a buoy month directory, iterates over the 
files, creates a pandas DataFrame for each month and saves it in the month 
folder. The pandas DataFrame is time indexed to nearest tenth of a second 
second, with columns for signal_quality, heave, north, west. A numpy file is 
saved contains a simple 1d array listing files which have structure errors and 
therefore their data is unable to be included in the DataFrame. The heave 
timeseries of the DataFrame is then checked to find peaks and troughs, those 
identified are then added as a column 'extrema' to the orginal DataFrame and 
saved again. The DataFrame containing extrema is then used to calculate, wave 
heights with timestamps. The zero crossing periods, including their timestamps 
are also calculated.

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
folder_path = 'D:\New_Datawell\Roag_Wavegen' 
dirs = os.listdir(folder_path)    
template = "%Y-%m-%dT%Hh%M"

def _datacheck_peakdetect(x_axis, y_axis):
    if x_axis is None:
        x_axis = list(range(len(y_axis)))
    
    if len(y_axis) != len(x_axis):
        raise ValueError
    
    #needs to be a numpy array
    y_axis = np.array(y_axis)
    x_axis = np.array(x_axis)
    return x_axis, y_axis
    
def peakdetect(y_axis, x_axis = None, lookahead = 4, delta=0):
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
    x_axis, y_axis = _datacheck_peakdetect(x_axis, y_axis)
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
    
def str_to_datetime(date_str):
    if '.' in date_str:
        return datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S.%f")
    else:
        return datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")

def datetime_to_float(date_time):
    return float('%s.%s' %(calendar.timegm(date_time.utctimetuple()), date_time.microsecond))

def str_to_float(date_str):
    date_time = str_to_datetime(date_str)
    return datetime_to_float(date_time)    

def get_zero_upcross_periods(raw_disp):
    print("start get_zero_upcross_periods")
    """ Based on code from https://gist.github.com/255291"""
    #timestamps = [str_to_float(x) for x in raw_disp.index]
    timestamps = [calendar.timegm(x.utctimetuple()) for x in raw_disp.index]
    heave = raw_disp['heave']
    indices = find((heave[1:]>=0)&(heave[:-1]<0))
    np.save('zero_cross_indices',indices)
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
    print("end get_zero_upcross_periods")

def get_rounded_timestamps(file_name, raw_array_length):
    """ Takes the length of the raw file and based on the file name gives the
    start timestamp and the raw records are assumed to be sent every 0.78125 
    seconds or 1.28Hz, returns a list of UTC datetimes """
    date_time = datetime.strptime(file_name.split('}')[1][:-5], template)
    if raw_array_length < 2300:
        time_interval = 0.78125
    else:
        time_interval = 1800/float(raw_array_length)
    unix_timestamp = calendar.timegm(date_time.timetuple())
    time_index = np.linspace(unix_timestamp, 
                             unix_timestamp + raw_array_length*time_interval - time_interval, 
                             raw_array_length)
    time_index = [round(x*10.0)/10.0 for x in time_index]    
    utc_timestamps_old = [str(datetime.utcfromtimestamp(x)) for x in time_index]
    np.save('utc_timestamps_old',utc_timestamps_old)
    utc_timestamps = [datetime.utcfromtimestamp(x) for x in time_index]
    np.save('utc_timestamps',utc_timestamps)
    return utc_timestamps

def iterate_over_file_names(path):
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
                if len(record_list) == 4:
                    records.append(record_list)
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
        raw_array.index = get_rounded_timestamps(filepath, len(raw_array))
        big_raw_array = big_raw_array.append( raw_array )
    big_raw_array.save('raw_buoy_displacement_pandas')  
    np.save("prob_files",np.array(problem_files))
    print("finish iterate_over_files")
    return big_raw_array

def calc_stats(raw_disp):
    print("start calc_stats")
    # There is an issue with the line below if you have signal_error true but
    # the following trough has a signal_error false would you get mismatched
    # peak and troughs in your DataFrame and therefore incorrect wave heights
    # to address this you need to search for signal_error True or >4*std True
    # and if extrema is not NaN find out if it is a peak ( then remove 
    # following trough and if it is a trough remove preceding peak
    masked_raw_disp = raw_disp.ix[raw_disp['signal_error']==False]
    extrema = masked_raw_disp.ix[np.invert(np.isnan(masked_raw_disp['extrema']))]
    differences = np.ediff1d(np.array(extrema['heave']))
    wave_height_timestamps = extrema.index[differences>0]
    wave_heights = differences[differences>0]
    wave_height_dataframe = pd.DataFrame(wave_heights, columns=['wave_height_cm'], index = wave_height_timestamps)    
    wave_heights, wave_height_timestamps, differences, extrema, masked_raw_disp = None, None, None, None, None
    wave_height_dataframe.save('wave_height_dataframe')
    wave_height_dataframe = None
    get_zero_upcross_periods(raw_disp)
    print("end calc_stats")

def get_extrema_timestamps(extrema, index):
    indexes = [x[0] for x in extrema]
    timestamps = [index[z] for z in indexes]
    return timestamps

def get_peaks(big_raw_array):
    print("start get_peaks")
    y = big_raw_array['heave']
    index = big_raw_array.index
    _max, _min = peakdetect(y)
    maxima_timestamps = get_extrema_timestamps(_max, index)
    minima_timestamps = get_extrema_timestamps(_min, index)
    maxima_df = pd.DataFrame(np.ones(len(_max), dtype=np.int64), columns = ['extrema'], index = maxima_timestamps)
    minima_df = pd.DataFrame(np.ones(len(_min), dtype=np.int64), columns = ['extrema'], index = minima_timestamps)*-1
    extrema_df = maxima_df.reset_index().merge(minima_df.reset_index(), how='outer').set_index('index')
    maxima_df, minima_df, maxima_timestamps, minima_timestamps = None, None, None, None
    extrema_df = extrema_df.sort()
    raw_disp_with_extrema = big_raw_array.join(extrema_df)
    extrema_df, big_raw_array = None, None
    raw_disp_with_extrema = raw_disp_with_extrema.sort()
    raw_disp_with_extrema.save('raw_disp_with_extrema')
    print("end get_peaks")
    return raw_disp_with_extrema

def detect_error_waves(extrems_df):
    print "start detect_error_waves"
    error_wave_mask = extrems_df['sig_qual']>0
    bad_extrem_indexes = np.where(error_wave_mask==True)
    bad_waves = []
    for index in bad_extrem_indexes[0]:
        extrema_type = extrems_df['extrema'].ix[index]
        bad_waves.append(index)
        if extrema_type == -1:
            bad_waves.append(index+1)
        else:
            bad_waves.append(index-1)
		
    boolean_error_waves = []
    for element in range(len(extrems_df)):
        boolean_error_waves.append(False)
    boolean_error_waves_array = np.array(boolean_error_waves)
    for element in bad_waves:
        boolean_error_waves_array[element] = True
    error_waves_df = pd.DataFrame(boolean_error_waves_array ,columns=['signal_error'], index = extrems_df.index )
    extrems_plus_errors = extrems_df.join(error_waves_df)
    extrems_plus_errors = extrems_plus_errors.sort()
    extrems_plus_errors.save('raw_disp_with_extrema_and_errors')
    print "end detect_error_waves"	
    return extrems_plus_errors

def detect_4_by_std(raw_disp):
    print "start detect_4_by_std"
    raw_set_length = 2304
    four_times_std_heave_30_mins = []
    for x in range(0, len(raw_disp), raw_set_length):
        end_index = x+raw_set_length
        if end_index > len(raw_disp):
            disp_set = raw_disp.ix[x:]
        else:
            disp_set = raw_disp.ix[x:end_index]
        set_description = disp_set.describe()
        four_times_heave_std = set_description['heave'][2] * 4
        four_times_std_heave_30_mins.append(disp_set['heave'].abs()>four_times_heave_std)
    
    flat_four_times_std = pd.concat(four_times_std_heave_30_mins)
    flat_four_times_std.name=['>4*std']
    flat_four_times_std = pd.DataFrame(flat_four_times_std)
    raw_plus_std = raw_disp.join(flat_four_times_std)
    raw_plus_std.save('raw_plus_std')
    print "end detect_4_by_std"
    return raw_plus_std
    
def iterate_over_months(dirs, folder_path):
    for x in dirs:
        month_dirs = os.listdir(os.path.join(folder_path,x))
        for month_dir in month_dirs:
            path = os.path.join(folder_path,x,month_dir)
            #path = os.path.join(folder_path,x)
            print(path)
            big_raw_array = iterate_over_file_names(path)
            raw_disp_with_extrema = get_peaks(big_raw_array)
            big_raw_array = None
            raw_disp_with_extrema_errors = detect_error_waves(raw_disp_with_extrema)
            raw_plus_std = detect_4_by_std(raw_disp_with_extrema_errors)
            raw_disp_with_extrema = None
            calc_stats(raw_plus_std)
            raw_disp_with_extrema_errors = None
        
iterate_over_months(dirs, folder_path)