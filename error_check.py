import numpy as np
import pandas as pd

class Error_Check():

    def __init__(self, extrema_df, sigma = 4):
        self.sigma = sigma
        self.detect_error_waves(extrema_df)
        self.detect_4_by_std()
        
    def detect_error_waves(self, extrema_df):
        """Find values with status signal problem and is a peak or trough,
        then adds a 'signal_error' boolean column to the DataFrame
        """
        print "start detect_error_waves"
        error_wave_mask = extrema_df['sig_qual']>0
        extrema_df['signal_error'] = error_wave_mask
        extrems_plus_errors = extrema_df.sort()
        self.extrema_with_errors = extrems_plus_errors
    
    def detect_4_by_std(self):
        """This function groups the displacements in the DataFrame by filename
        getting the standard deviation for each displacement (heave,north,west) 
        The displacements are then compared against 4 times 
        their standard deviation and any records exceeding this comparison for 
        any displacement are give a True value for >4*std column, the standard
        deviations are also stored in the DataFrame so further comparison can
        be made
        """
        print "detect_4_by_std"
        four_times_std_heave_30_mins = []
        grouped_displacements = self.extrema_with_errors.groupby('file_name')
        self.raw_plus_std = self.extrema_with_errors.join(grouped_displacements['heave','north','west'].std(), 
                                                          on='file_name', rsuffix='_file_std')                                  
        heave_4_std = self.raw_plus_std.heave > ( self.raw_plus_std.heave_file_std * 4 )
        north_4_std = self.raw_plus_std.north > ( self.raw_plus_std.north_file_std * 4 )
        west_4_std = self.raw_plus_std.heave > ( self.raw_plus_std.west_file_std * 4 )
        disp_more_than_4_std = heave_4_std + north_4_std + west_4_std
        self.raw_plus_std['>4*std'] = disp_more_than_4_std
        self.raw_plus_std.save('raw_plus_std')
        print self.raw_plus_std
