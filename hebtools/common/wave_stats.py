""" Module for calculating wave heights and zero crossing period from 
DataFrames where the extrema positions have been calculated
@author: James Morrison
@license: MIT
"""
import numpy as np
from datetime import datetime
from matplotlib.mlab import find
import pandas as pd
import calendar
import logging
import sys
logging.basicConfig(stream=sys.stderr, level=logging.INFO)

class WaveStats:
    
    def __init__(self, raw_disp, column_name = 'heave', error_check = True, 
                 series_name = 'wave_height_cm', 
                 df_file_name = 'wave_height_dataframe'):    
        self.raw_disp = raw_disp
        self.calc_stats(column_name, error_check, series_name, df_file_name)
        if error_check:
            self.get_zero_upcross_periods(column_name)
    
    def get_zero_upcross_periods(self, column_name):
        """ Based on code from https://gist.github.com/255291"""
        logging.info('start get_zero_upcross_periods')
        timestamps = [calendar.timegm(x.utctimetuple()) for x in self.raw_disp.index]
        heave = self.raw_disp[column_name]
        indices = find((heave[1:]>=0)&(heave[:-1]<0))
        crossings = [i - heave[i] / (heave[i+1] - heave[i]) for i in indices]
        zero_cross_t_stamps = []
        for crossing in crossings:
            #Check if zero cross occurs at the end of the time-series
            if crossing+1 == len(timestamps):
                zero_cross_t_stamps.append(timestamps[int(crossing)])
            else:
                difference = timestamps[int(crossing)]-timestamps[int(crossing+1)]
                fraction = crossing-int(crossing)
                timestamp = timestamps[int(crossing)] + difference * fraction
                zero_cross_t_stamps.append(timestamp)
        zero_crossing_timestamps_np = np.array(zero_cross_t_stamps)
        zero_upcross_periods = np.ediff1d(zero_crossing_timestamps_np)
        def get_datetime(x):
            return datetime.utcfromtimestamp(x)
        zero_cross_t_stamps = [get_datetime(x) for x in zero_cross_t_stamps]
        df = pd.DataFrame(zero_upcross_periods, 
                          index = zero_cross_t_stamps[:-1])
        df.to_pickle('zero_crossing_dataframe')    
        
    def mask_df(self, df, columns, comparison_val = False):
        for col in columns:
            df = df[df[col]==comparison_val]
        return df
        
    def check_wave_height_dataframe(self, wave_height_df):
        """Filter wave heights on the basis of any true values occuring for 
        signal_error or >4*std, grab the time index of a wave height
        and the timestamp of the next wave height and check the interval
        between them for >4*std or signal_error true and if so remove the
        wave height"""
        columns = ['max_std_factor', 'heave_file_std']
        stats_dict = dict([(column,[]) for column in columns])
        indexes = np.where(np.in1d(self.raw_disp.index, wave_height_df.index))
        df_list = np.split(self.raw_disp, indexes[0])[1:]
        for subset in df_list:
                stats_dict[columns[0]].append(subset.max_std_factor.max())
                stats_dict[columns[1]].append(subset.heave_file_std.max())
        logging.info((len(stats_dict[columns[1]]), len(wave_height_df.index)))
        stats_df = pd.DataFrame(stats_dict, index=wave_height_df.index)
        return wave_height_df.join(stats_df)
    
    def calc_stats(self, column_name, error_check, series_name, df_file_name):
        """ wave heights are calculated from peak to trough """        
        logging.info("start calc_stats")        
        extrema = self.raw_disp
        #From the extrema column of the dataframe, extract all non null values
        extrema = extrema.ix[np.invert(np.isnan(extrema['extrema']))]
        peak_to_peak_period = np.diff(extrema[extrema['extrema']==1].index.values)
        p_to_p_period_df = pd.DataFrame(dict(period=peak_to_peak_period), 
                                        dtype='float')
        
        # Calculate the difference between adjacent extrema
        differences = np.ediff1d(np.array(extrema[column_name]))
        # Pick the negative difference, the downward slope of the wave
        sub_zero_diff = differences<0
        # Get the timestamps of the difference ( the peak )
        wave_height_timestamps = extrema.index[sub_zero_diff]
        # Remove the negative sign giving a positive wave height 
        wave_heights = np.absolute(differences[sub_zero_diff])
        # Bring timestamps and wave heights together into one dataframe
        wave_height_df = pd.DataFrame(wave_heights, columns=[series_name],
                                      index = wave_height_timestamps)                                      
        p_to_p_period_df.index = wave_height_timestamps[:-1]
        p_to_p_period_df = p_to_p_period_df/1000000000
        # Exclude periods greater than 30 seconds as that is in excess of
        # maximum size the moored wave buoys can record
        p_to_p_period_df[p_to_p_period_df>30]=np.nan
        wave_height_df = wave_height_df.join(p_to_p_period_df)
        # If the data is from a Datawell buoy add the original raw filename
        if error_check:
            file_names = extrema.file_name[sub_zero_diff]
            file_name_df = pd.DataFrame(file_names, columns=['file_name'], 
                                    index = wave_height_timestamps)
            wave_height_df = wave_height_df.join(file_name_df)    
            wave_height_df = self.check_wave_height_dataframe(wave_height_df)
        wave_height_df.to_hdf('buoy_data.h5', 'wave_height', format='t',
                              append=False, complib='blosc', complevel=9)