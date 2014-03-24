import pandas as pd
import logging
import sys
logging.basicConfig(stream=sys.stderr, level=logging.INFO)

def check(extrema_df, sigma = 4):
     
    directions = ['heave','north','west']
    std_factor = {}
    suf = '_file_std'
    
    def detect_error_waves(extrema_df):
        """Find values with status signal problem and is a peak or trough,
        then adds a 'signal_error' boolean column to the DataFrame
        """
        logging.info("start detect_error_waves")
        error_wave_mask = extrema_df['sig_qual']>0
        extrema_df['signal_error'] = error_wave_mask
        extrems_plus_errors = extrema_df.sort()
        return extrems_plus_errors
    
    def compare_std(raw_plus_std, direction):
        return raw_plus_std[direction].abs() > \
               (raw_plus_std[direction + suf] * sigma)
    
    def calculate_std(sigma, displacements):
        """This function groups the displacements in the DataFrame by filename
        getting the standard deviation for each displacement (heave,north,west) 
        , the standard deviations are also stored in the DataFrame so further 
        comparison can be made
        """
        logging.info("calculate_std")
        filtered_displacements = displacements[displacements['signal_error']==0]
        grouped_displacements = filtered_displacements.groupby('file_name')
        std_deviations = grouped_displacements['heave','north','west'].std()
        raw_plus_std = displacements.join(std_deviations, on='file_name', 
                                          rsuffix='_file_std')                                
        raw_plus_std.to_pickle('raw_plus_std')
        return raw_plus_std
        
    def compare_factors(main_factor, second_factor, third_factor):
        """ return mask of one displacement where its displacements are the 
        largest """
        return main_factor[(main_factor > second_factor) & \
                           (main_factor > third_factor)]
    
    def calc_std_factor(raw_plus_std):
        for direction in directions:
            std_factor[direction] = (raw_plus_std[direction] /
                                     raw_plus_std[direction + suf]).abs()
        factors = []
        dirs = directions[:]
        for direction in directions:
            factors.append(compare_factors(std_factor[dirs[0]], 
                                           std_factor[dirs[1]],
                                           std_factor[dirs[2]]))
            dirs.append(dirs.pop(0))
        combined_factors = pd.concat(factors)
        combined_factors.name = 'max_std_factor'
        raw_plus_std = raw_plus_std.join(combined_factors)
        raw_plus_std.to_pickle('raw_plus_std')
        return raw_plus_std
        
    displacements = detect_error_waves(extrema_df)
    raw_plus_std = calculate_std(sigma, displacements)
    return calc_std_factor(raw_plus_std)