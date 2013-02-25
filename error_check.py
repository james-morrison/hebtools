import numpy as np
import pandas as pd

class Error_Check():

    def __init__(self, extrema_df, sigma = 4 ):
        self.sigma = sigma
        self.detect_error_waves(extrema_df)
        self.detect_4_by_std()
        self.calc_std_factor()
        
    def detect_error_waves(self, extrema_df):
        """Find values with status signal problem and is a peak or trough,
        then adds a 'signal_error' boolean column to the DataFrame
        """
        print "start detect_error_waves"
        error_wave_mask = extrema_df['sig_qual']>0
        extrema_df['signal_error'] = error_wave_mask
        extrems_plus_errors = extrema_df.sort()
        self.displacements = extrems_plus_errors
    
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
        filtered_displacements = self.displacements[self.displacements['signal_error']==0]
        grouped_displacements = filtered_displacements.groupby('file_name')
        standard_deviations = grouped_displacements['heave','north','west'].std()
        self.raw_plus_std = self.displacements.join(standard_deviations, 
                                                          on='file_name', 
                                                          rsuffix='_file_std')                                  
        heave_4_std = self.raw_plus_std.heave.abs() > ( self.raw_plus_std.heave_file_std * self.sigma )
        north_4_std = self.raw_plus_std.north.abs() > ( self.raw_plus_std.north_file_std * self.sigma )
        west_4_std = self.raw_plus_std.west.abs() > ( self.raw_plus_std.west_file_std * self.sigma )
        disp_more_than_4_std = heave_4_std + north_4_std + west_4_std
        self.raw_plus_std['>4*std'] = disp_more_than_4_std
        self.raw_plus_std.save('raw_plus_std')
        print self.raw_plus_std
        
    def calc_std_factor(self):
        heave_std_factor = (self.raw_plus_std.heave / self.raw_plus_std.heave_file_std).abs()
        north_std_factor = (self.raw_plus_std.north / self.raw_plus_std.north_file_std).abs()
        west_std_factor = (self.raw_plus_std.west / self.raw_plus_std.west_file_std).abs()
        west_more_than_mask = (west_std_factor > heave_std_factor) & \
                              (west_std_factor > north_std_factor)
        north_more_than_mask = (north_std_factor > heave_std_factor) & \
                               (north_std_factor > west_std_factor)
        heave_more_than_mask = (heave_std_factor > west_std_factor) & \
                               (heave_std_factor > north_std_factor)
        heave_factors = heave_std_factor[heave_more_than_mask]
        north_factors = north_std_factor[north_more_than_mask]
        west_factors = west_std_factor[west_more_than_mask]
        combined_factors = pd.concat([heave_factors,north_factors,west_factors])
        combined_factors.name = 'max_std_factor'
        self.raw_plus_std = self.raw_plus_std.join(combined_factors)
        self.raw_plus_std.save('raw_plus_std')