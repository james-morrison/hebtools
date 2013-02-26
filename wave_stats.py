import numpy as np
from datetime import datetime
from matplotlib.mlab import find
import pandas as pd
import calendar
import logging
import sys
logging.basicConfig(stream=sys.stderr, level=logging.INFO)

class Wave_Stats:
    
    def __init__(self, raw_disp, column_name = 'heave', error_check = True, 
                 series_name = 'wave_height_cm', 
                 df_file_name = 'wave_height_dataframe'):    
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
        zero_cross_t_stamps = []
        for crossing in crossings:
            #Check if zero cross occurs at the end of the time-series
            if crossing+1 == len(timestamps):
                zero_cross_t_stamps.append(timestamps[int(crossing)])
            else:
                difference = timestamps[int(crossing)]-timestamps[int(crossing+1)]
                fraction = crossing-int(crossing)
                zero_cross_t_stamps.append(timestamps[int(crossing)] + difference * fraction)
        zero_crossing_timestamps_np = np.array(zero_cross_t_stamps)
        zero_upcross_periods = np.ediff1d(zero_crossing_timestamps_np)
        def get_datetime(x):
            return datetime.utcfromtimestamp(x)
        zero_cross_t_stamps = [get_datetime(x) for x in zero_cross_t_stamps]
        df = pd.DataFrame(zero_upcross_periods, 
                          index = zero_cross_t_stamps[:-1])
        df.save('zero_crossing_dataframe')    
        
    def mask_df(self, df, columns, comparison_val = False):
        for col in columns:
            df = df[df[col]==comparison_val]
        return df
        
    def bad_subset(self, subset):
        #if np.sum(subset['signal_error']==True) > 0:
        #    return True
        #elif np.sum(subset['>4*std']==True) > 0:
        #    return True
        #else:
            return False
        
    def check_wave_height_dataframe(self, wave_height_df):
        """Filter wave heights on the basis of any true values occuring for 
        signal_error or >4*std, grab the time index of a wave height
        and the timestamp of the next wave height and check the interval
        between them for >4*std or signal_error true and if so remove the
        wave height"""
        bad_wave_booleans = []
        max_std_factor = []
        heave_file_std = []
        for index, wave_height in enumerate(wave_height_df.iterrows()):
            if index+1 < len(wave_height_df):
                subset = self.raw_disp.ix[wave_height[0]:wave_height_df.ix[index+1].name]
                bad_wave_booleans.append(self.bad_subset(subset))
                max_std_factor.append(subset.max_std_factor.max())
                heave_file_std.append(subset.heave_file_std.max())
        print len(bad_wave_booleans), wave_height_df
        bool_df = pd.DataFrame(bad_wave_booleans, columns=['bad_wave'],
                               index=wave_height_df.index[:-1])
        std_df = pd.DataFrame(max_std_factor, columns=['max_std_factor'],
                              index=wave_height_df.index[:-1])
        heave_df = pd.DataFrame(heave_file_std, columns=['heave_file_std'],
                              index=wave_height_df.index[:-1])                                   
        bool_std_heave_df = pd.concat([bool_df, std_df, heave_df],
                                axis=1)
        return wave_height_df.join(bool_std_heave_df)
    
    def calc_stats(self, column_name, error_check, series_name, df_file_name):
        logging.info("start calc_stats")
        # wave heights are calculated from peak to trough
        extrema = self.raw_disp
        extrema = extrema.ix[np.invert(np.isnan(extrema['extrema']))]
        extrema.save('check_extrema')
        differences = np.ediff1d(np.array(extrema[column_name]))
        np.save('differences',differences)
        wave_height_timestamps = extrema.index[differences<0]
        file_names = extrema.file_name[differences<0]
        wave_heights = np.absolute(differences[differences<0])
        np.save('wave_heights',wave_heights)
        wave_height_df = pd.DataFrame(wave_heights, columns=[series_name],
                                      index = wave_height_timestamps)
        print wave_height_df
        file_name_df = pd.DataFrame(file_names, columns=['file_name'], 
                                    index = wave_height_timestamps)
        wave_height_df = wave_height_df.join(file_name_df)
        if error_check:        
            wave_height_df = self.check_wave_height_dataframe(wave_height_df)
        wave_height_df.save(df_file_name)
        print wave_height_df.describe()
        
        