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
        
    def bad_subset(self, subset):
        if np.sum(subset['signal_error']==True) > 0:
            return True
        elif np.sum(subset['>4*std']==True) > 0:
            return True
        else:
            return False
            
    def calc_stats(self, column_name, error_check, series_name, df_file_name):
        logging.info("start calc_stats")
        # wave heights are calculated from peak to trough
        extrema = self.raw_disp
        print extrema
        extrema = extrema.ix[np.invert(np.isnan(extrema['extrema']))]
        differences = np.ediff1d(np.array(extrema[column_name]))
        wave_height_timestamps = extrema.index[differences<0]
        wave_heights = np.absolute(differences[differences<0])
        print wave_heights
        wave_height_dataframe = pd.DataFrame(wave_heights, columns=[series_name], index = wave_height_timestamps)    
        if error_check:
            """Filter wave heights on the basis of any true values occuring for 
            signal_error or >4*std, grab the time index of a wave height
            and the timestamp of the next wave height and check the interval
            between them for >4*std or signal_error true and if so remove the
            wave height"""
            bad_wave_index = []
            for index, wave_height in enumerate(wave_height_dataframe.iterrows()):
                if index+1 < len(wave_height_dataframe):
                    subset = self.raw_disp.ix[wave_height[0]:wave_height_dataframe.ix[index+1].name]
                    result = self.bad_subset(subset)
                    if result:
                        bad_wave_index.append(wave_height[0])
        wave_height_dataframe.save(df_file_name)
        filterd_wave_height_df = wave_height_dataframe.drop(bad_wave_index)
        filterd_wave_height_df.save(df_file_name)