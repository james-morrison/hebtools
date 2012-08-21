# -*- coding: utf-8 -*-
"""
Created on Mon Aug 20 16:03:46 2012

Loadas a Pandas DataFrame produced by detect_peaks.py, selects all the heave 
values at the local extrema calculates the difference between the extrema.
Where the differences are negative ( falling from peak ) get the timestamps of 
those peaks as well as the fall in height.


@author: James Morrison
@license: MIT
"""

import pandas as pd
from datetime import datetime
import calendar
import numpy as np
from matplotlib.mlab import find

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

def get_periods(raw_disp):
    local_maxima = raw_disp.ix[raw_disp['extrema']==1]
    local_maxima_index = local_maxima.index
    timestamps = [str_to_float(x) for x in local_maxima_index]
    print len(timestamps)
    np.save('timestamps',timestamps)
    timestamps_periods = np.array([timestamps[0:-1]]).transpose()
    print timestamps_periods.shape
    periods = np.ediff1d(np.array(timestamps))
    periods_vert = np.array([periods]).transpose()
    print periods_vert.shape
    periods_with_timestamps = np.concatenate((periods_vert,timestamps_periods), axis=1)
    print periods_with_timestamps
    return periods_with_timestamps

def get_zero_upcross_periods(raw_disp):
    """ Based on code from https://gist.github.com/255291 """
    timestamps = [str_to_float(x) for x in raw_disp.index]
    heave = raw_disp['heave']
    indices = find((heave[1:]>=0)&(heave[:-1]<0))
    crossings = [i - heave[i] / (heave[i+1] - heave[i]) for i in indices]
    zero_crossing_timestamps = []
    for crossing in crossings:
        difference = timestamps[int(crossing)]-timestamps[int(crossing+1)]
        fraction = crossing-int(crossing)
        zero_crossing_timestamps.append(timestamps[int(crossing)] + difference * fraction)
    zero_crossing_timestamps_np = np.array(zero_crossing_timestamps)
    np.save('zero_crossing_timestamps',zero_crossing_timestamps_np)
    zero_upcross_periods = np.ediff1d(zero_crossing_timestamps_np)
    np.save('zero_upcross_periods',zero_upcross_periods)    

raw_disp = pd.load('raw_disp_with_extrema')
#periods = get_periods(raw_disp)
extrema = raw_disp.ix[np.invert(np.isnan(raw_disp['extrema']))]
differences = np.ediff1d(np.array(extrema['heave']))
wave_height_timestamps = extrema.index[differences<0]
wave_heights = differences[differences<0]
wave_height_time_vert = np.array([wave_height_timestamps]).transpose()
wave_height_vert = np.array([wave_heights]).transpose()
wave_heights_with_timestamps = np.concatenate((wave_height_vert, wave_height_time_vert), axis=1)
np.save('wave_heights',wave_heights_with_timestamps)
get_zero_upcross_periods(raw_disp)

    




