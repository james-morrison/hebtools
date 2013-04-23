"""
Module for concatenating wave_height_dataframes produced by parse_raw module.
Passed a buoy directory the module will iterate over the years and months of 
data producing statistics from the concatenated wave_height_dataframes 
including h_max, h_1_3_mean, h_rms and the time period these statistics cover.
The statistics are then saved as a Pandas DataFrame and exported to Excel xlsx 
format. 

@author:James Morrison
@license: MIT
"""

import os
import sys
import pandas as pd
import numpy as np
from collections import OrderedDict

def filter_maximums(heave_std_series, max_series, multiple, grouped_df):
    max_series[max_series>(heave_std_series*multiple)]
    #max_series
                        

def std_factor(series_dict, columns):
    numerator = ( np.sqrt( 8 - 2 * np.pi ) * series_dict[columns['file_std']])
    return  numerator / series_dict[columns['std']]

def avg_factor(series_dict, columns):
    numerator = ( 2.5 *  series_dict[columns['file_std']])
    return numerator / series_dict[columns['avg']]
    
def rms_factor(series_dict, columns):
    numerator = ( np.sqrt(8) *  series_dict[columns['file_std']])
    return  numerator / series_dict[columns['rms']]
    
def h_1_3(subset):
    return subset.order()[-(len(subset)/3):].mean()

def rms(subset):
    return np.sqrt((subset**2).sum()/len(subset))
                        
def get_stats_from_df_groupby(large_dataframe, series_name, path, sigma = 3.5):
    '''Groups DataFrame by file_name, which should be approximately half hours
    Standard deviation, Maximum and Mean are extracted as series and joined 
    into DataFrame along with end_timestamps and start_timestamps and 
    file_names. DataFrame is then saved and exported as Excel workbook.
    '''
    new_cols = ['date_time_index']
    large_dataframe = large_dataframe.sort()
    large_dataframe = large_dataframe[large_dataframe.max_std_factor < sigma]
    heave_std_multiple = np.sqrt(8*np.log10(len(large_dataframe)))
    reset_index_df = large_dataframe.reset_index()
    cols = reset_index_df.columns.values
    [new_cols.append(x) for x in cols[1:]]
    reset_index_df.columns = new_cols
    grouped_df = reset_index_df.groupby('file_name')
    series_dict = OrderedDict()
    columns = {'std':'h_std', 'file_std':'heave_file_std', 'max':'h_max', 
               'avg':'h_avg', '1_3':'h_1_3_mean', 'rms':'h_rms', 
               'm_std_fac':'max_std_factor', 
               'std_fac':'heave_file_std_over_h_std',
               'avg_fac':'heave_file_std_over_h_avg', 
               'rms_fac':'heave_file_std_over_h_rms',
               'end':'end_times'}
    series_dict[columns['std']] = grouped_df[series_name].std()
    series_dict[columns['file_std']] = grouped_df[columns['file_std']].first()
    series_dict[columns['max']] = grouped_df[series_name].max()    
    #filter_maximums(heave_file_std_series, max_series, heave_std_multiple, 
    #                grouped_df)
    series_dict[columns['avg']] = grouped_df[series_name].mean()
    series_dict[columns['1_3']] = grouped_df.wave_height_cm.apply(h_1_3)
    series_dict[columns['rms']] = grouped_df.wave_height_cm.apply(rms)
    series_dict[columns['m_std_fac']] = grouped_df['max_std_factor'].max()
    series_dict[columns['std_fac']] = std_factor(series_dict, columns)
    series_dict[columns['avg_fac']] = avg_factor(series_dict, columns)
    series_dict[columns['rms_fac']] = rms_factor(series_dict, columns)
    series_dict[columns['end']] = grouped_df[new_cols[0]].last() 
    start_timestamps = grouped_df[new_cols[0]].first().values
    avg_max_std_end_df = pd.concat(series_dict.values(), axis=1)
    avg_max_std_end_df.columns = series_dict.keys()                                   
    avg_max_std_end_df.index = start_timestamps
    file_names_df = pd.DataFrame(grouped_df.file_name.size().index, 
                                 columns = ['file_names'], 
                                 index=start_timestamps)
    all_stats_df = avg_max_std_end_df.join(file_names_df)
    file_name = path + 'stats_groupby_' + str(sigma)
    all_stats_df.to_excel(file_name + '.xlsx')
    all_stats_df.save(file_name)
    
def iterate_over_buoy_years(buoy_path):
    os.chdir(buoy_path)
    years = os.listdir('.')
    large_dataframe = pd.DataFrame()
    for year in years:
        if os.path.isdir(year):
            os.chdir(year)
            months = os.listdir('.')
            for month in months:
                if os.path.isdir(month):
                    os.chdir(month)
                    wave_height_df = pd.load('wave_height_dataframe')
                    large_dataframe = pd.concat([large_dataframe, 
                                                 wave_height_df])
                    os.chdir('..') 
            os.chdir('..') 
    print os.getcwd()    
    large_dataframe.save('large_wave_height_df')
    get_stats_from_df_groupby(large_dataframe, "wave_height_cm", buoy_path)
            
if __name__ == "__main__":
    if len(sys.argv) == 1:
        print "wave_concat module requires path to buoy directory" 
    else:
        iterate_over_buoy_years(sys.argv[1])
    