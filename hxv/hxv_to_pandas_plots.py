# -*- coding: utf-8 -*-
"""
Created on Mon Aug 27 17:00:28 2012

@author: le12jm
"""

import os
import glob
import numpy as np
from datetime import datetime
import calendar
import pandas as pd
from matplotlib.mlab import find
import matplotlib.pyplot as plt
import time
path = 'D:\\downloads\\weird_waves2\\'
os.chdir(path)
file_names = glob.glob('*.hxv')
template = "%Y-%m-%dT%Hh%M"

def _datacheck_peakdetect(x_axis, y_axis):
    if x_axis is None:
        x_axis = range(len(y_axis))
    
    if len(y_axis) != len(x_axis):
        raise (ValueError, 
                'Input vectors y_axis and x_axis must have same length')
    
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
        raise ValueError, "Lookahead must be '1' or above in value"
    if not (np.isscalar(delta) and delta >= 0):
        raise ValueError, "delta must be a positive number"
    
    #maxima and minima candidates are temporarily stored in
    #mx and mn respectively
    mn, mx = np.Inf, -np.Inf
    
    #Only detect peak if there is 'lookahead' amount of points after it
    for index, (x, y) in enumerate(zip(x_axis[:-lookahead], 
                                        y_axis[:-lookahead])):
        if y > mx:
            mx = y
            mxpos = x
        if y < mn:
            mn = y
            mnpos = x
        
        ####look for max####
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

def get_zero_upcross_periods(raw_disp, errors, hxv_file_name):
    """ Based on code from https://gist.github.com/255291"""
    timestamps = [time.mktime(x.timetuple()) for x in raw_disp.index]
    heave = raw_disp
    #print heave
    indices = find((heave[1:]>=0)&(heave[:-1]<0))
    crossings = [i - heave[i] / (heave[i+1] - heave[i]) for i in indices]
    zero_crossing_timestamps = []
    for crossing in crossings:
        difference = timestamps[int(crossing-1)]-timestamps[int(crossing)]
        fraction = crossing-int(crossing)
        zero_crossing_timestamps.append(timestamps[int(crossing)] + difference * fraction)
    zero_crossing_timestamps_np = np.array(zero_crossing_timestamps)
    zero_upcross_periods = np.ediff1d(zero_crossing_timestamps_np)
    zero_crossing_timestamps = [datetime.fromtimestamp(x) for x in zero_crossing_timestamps]
    df = pd.DataFrame(zero_upcross_periods, columns = ['Heave'], index = zero_crossing_timestamps[:-1])
    df.save('zero_crossing_dataframe')
    return df

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
    elif raw_array_length == 2303:
        time_interval = 0.78158923143
    unix_timestamp = calendar.timegm(date_time.timetuple())
    time_index = np.linspace(unix_timestamp, 
                             unix_timestamp + raw_array_length*time_interval - time_interval, 
                             raw_array_length)
    time_index = [round(x*10.0)/10.0 for x in time_index]    
    utc_timestamps = [datetime.utcfromtimestamp(x) for x in time_index]
    return utc_timestamps

for hxv_file_name in file_names:
    print hxv_file_name
    array = np.genfromtxt(hxv_file_name, delimiter = ',', dtype='|S4')
    utc_timestamps = get_rounded_timestamps(hxv_file_name, len(array))
    heave_section = array[:,2]
    sig_qual_section = array[:,0]
    sig_qual = [int(x[0:2]) for x in sig_qual_section]
    sig_qual = np.array(sig_qual)
    heave = [x[0:-1] for x in heave_section]
    sign = [int(x[0],16)for x in heave]
    signs = []
    large_value = []
    for x in sign:
        if x < 8:
            signs.append(1)
        else:
            signs.append(-1)
        large_value.append(x%8)
    
    hex_value = [int(x[1:],16) for x in heave]
    final_hex_value = []
    for index, x in enumerate(hex_value):
        final_hex_value.append(signs[index] * (large_value[index]*256 + x))
    file_dataframe = pd.DataFrame(final_hex_value, columns = ['Heave'], index = utc_timestamps)
    sig_qual_df = pd.DataFrame(sig_qual, columns = ['Signal_Quality'], index = utc_timestamps)
    file_dataframe = file_dataframe.join(sig_qual_df)
    fig, ax = plt.subplots(2, sharex=True)
    ax2 = ax[0].twinx()
    file_dataframe['Heave'].plot(ax=ax[0], style='b-')
    file_dataframe['Signal_Quality'].plot(ax=ax2, style='r-')
    ax[1].set_xlabel('Time ( Hours:Minutes:Seconds )')
    ax[0].set_ylabel('Displacement ( Centimetres )')
    ax[1].set_ylabel('Period ( Seconds )')
    ax2.set_ylabel('Signal Quality (0 is best)')
    
    counter = 0
    for x in sig_qual:
        if x != 0:
            counter +=1
    df = get_zero_upcross_periods(file_dataframe['Heave'], counter, hxv_file_name)
    df.plot(ax=ax[1],style='g-')
    plt.title(hxv_file_name)
    plt.savefig(hxv_file_name[:-5] + '_heave.png')

