import numpy as np
import pandas as pd

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
        extrema_df['signal_error'] = error_wave_mask
        extrems_plus_errors = extrema_df.sort()
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
        self.extrema_with_errors['>4*std'] = flat_four_times_std
        self.extrema_with_errors.save('raw_plus_std')
        self.raw_plus_std = self.extrema_with_errors
        print self.raw_plus_std
