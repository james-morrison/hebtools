import numpy as np
from datetime import datetime
from matplotlib.mlab import find
import pandas as pd
import calendar
import logging
import sys
logging.basicConfig(stream=sys.stderr, level=logging.INFO)

class Wave_Stats:
    
    def __init__(self, raw_disp, column_name = 'heave', error_check = True, series_name = 'wave_height_cm', df_file_name = 'wave_height_dataframe'):    
        self.raw_disp = raw_disp
        self.calc_stats(column_name, error_check, series_name, df_file_name)
        if error_check:
            self.get_zero_upcross_periods(column_name)
    
    def get_zero_upcross_periods(self, column_name):
        logging.info('start get_zero_upcross_periods')
        """ Based on code from https://gist.github.com/255291"""
        timestamps = [calendar.timegm(x.utctimetuple()) for x in self.raw_disp.index]
        heave = self.raw_disp[column_name]
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
        
    def mask_df(self, df, columns, comparison_val = False):
        for col in columns:
            df = df[df[col]==comparison_val]
        return df
        
    def calc_stats(self, column_name, error_check, series_name, df_file_name):
        logging.info("start calc_stats")
        # wave heights are calculated from peak to trough
        if error_check:
            accompanying_extrema = self.find_accompanying_false_extrema()
            self.raw_disp['accompanying_false_extrema'] = accompanying_extrema
            extrema = self.raw_disp.ix[~np.isnan(self.raw_disp['extrema'])]
            extrema = self.mask_df(extrema, ['signal_error', '>4*std',
                                             'accompanying_false_extrema'])
        else:
            extrema = self.raw_disp
            extrema = extrema.ix[np.invert(np.isnan(extrema['extrema']))]

        differences = np.ediff1d(np.array(extrema[column_name]))
        wave_height_timestamps = extrema.index[differences<0]
        wave_heights = np.absolute(differences[differences<0])
        wave_height_dataframe = pd.DataFrame(wave_heights, columns=[series_name], index = wave_height_timestamps)    
        wave_height_dataframe.save(df_file_name)
    
    def get_false_extrema_index(self, extrema_type):
        extrema = self.raw_disp[self.raw_disp['extrema']==extrema_type]
        false_extrema = extrema[extrema['signal_error']==True]
        false_extrema_std = extrema[extrema['>4*std']==True]
        false_extrema = false_extrema.combine_first(false_extrema_std)
        return extrema, false_extrema.index
    
#    def find_accompanying_false_extrema(self):
#        # This function selects peaks, and for those with signal_error True or 
#        # >4*std True masks the following trough and then for all troughs with
#        # signal_error True or >4*std True mask the preceding peak
#        peaks, false_peak_index = self.get_false_extrema_index(1)
#        troughs, false_trough_index = self.get_false_extrema_index(-1)
#        indexes = []
#        for index_of_false_peak in false_peak_index:
#            if len(troughs.ix[index_of_false_peak:])!=0:
#                indexes.append(troughs.ix[index_of_false_peak:].ix[0].name)
#        
#        for index_of_false_trough in false_trough_index:
#            if len(peaks.ix[:index_of_false_trough])!=0:
#                indexes.append(peaks.ix[:index_of_false_trough].ix[-1].name)
#        boolean_array = self.raw_disp.index == indexes[0]
#        for x in indexes[1:]:
#            boolean_array += self.raw_disp.index == x
#        return boolean_array

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
        return boolean_array