"""
Module for concatenating wave_height_dataframes produced by raw_combined.py
Given a buoy root directory and buoy name the code will iterate over a list of 
buoys producing statistics for the concatenated wave_height_dataframes 
including h_max, h_1_3_mean and the time period these statistics cover. The 
statistics are then saved as a Pandas DataFrame and exported to Excel xlsx 
format. 
"""


import os
import pandas as pd
import numpy as np

buoys = ['buoy_data']
buoys_root_path = ''

def filter_maximums(heave_std_series, max_series, multiple, grouped_df):
    max_series[max_series>(heave_std_series*multiple)]
    #max_series
                        
                    
def get_stats_from_df_groupby(large_dataframe, series_name, path):
    '''Groups DataFrame by file_name, which should be approximately half hours
    Standard deviation, Maximum and Mean are extracted as series and joined 
    into DataFrame along with end_timestamps and start_timestamps and 
    file_names. DataFrame is then saved and exported as Excel workbook.
    '''
    new_cols = ['date_time_index']
    large_dataframe = large_dataframe.sort()
    sigma = 3.5
    large_dataframe = large_dataframe[large_dataframe.max_std_factor < sigma]
    heave_std_multiple = np.sqrt(8*np.log10(len(large_dataframe)))
    reset_index_df = large_dataframe.reset_index()
    cols = reset_index_df.columns.values
    [new_cols.append(x) for x in cols[1:]]
    reset_index_df.columns = new_cols
    grouped_df = reset_index_df.groupby('file_name')
    std_series = grouped_df[series_name].std()
    std_series.name = 'h_std'
    heave_file_std_series = grouped_df['heave_file_std'].first()
    heave_file_std_series.name = 'heave_file_std'
    max_series = grouped_df[series_name].max()    
    max_series.name = 'h_max'
    #filter_maximums(heave_file_std_series, max_series, heave_std_multiple, 
    #                grouped_df)
    avg_series = grouped_df[series_name].mean()
    avg_series.name = 'h_avg'
    h_1_3_mean_series = grouped_df.wave_height_cm.apply(lambda x : x.order()[-(len(x)/3):].mean())    
    h_1_3_mean_series.name = 'h_1_3_mean'
    h_rms_series = grouped_df.wave_height_cm.apply(lambda x: np.sqrt((x**2).sum()/len(x)))
    h_rms_series.name = 'h_rms'
    max_std_factor_series = grouped_df['max_std_factor'].max()
    max_std_factor_series.name = 'max_std_factor'
    h_std_file_std = ( np.sqrt( 8- 2 * np.pi ) *  \
                       heave_file_std_series) / std_series
    h_std_file_std.name = 'heave_file_std_over_h_std'
    h_avg_file_std = ( 2.5 *  heave_file_std_series) / avg_series
    h_avg_file_std.name = 'heave_file_std_over_h_avg'
    h_rms_file_std = ( np.sqrt(8) *  heave_file_std_series) / h_rms_series
    h_rms_file_std.name = 'heave_file_std_over_h_rms'
    end_timestamps_series = grouped_df[new_cols[0]].last()
    end_timestamps_series.name = 'end_times'
    start_timestamps = grouped_df[new_cols[0]].first().values
    avg_max_std_end_df = pd.concat([std_series, max_series, avg_series, 
                                    end_timestamps_series, h_1_3_mean_series, 
                                    h_rms_series, heave_file_std_series, 
                                    h_std_file_std, h_avg_file_std, 
                                    h_rms_file_std, max_std_factor_series], 
                                   axis=1)
    avg_max_std_end_df.index = start_timestamps
    file_names_df = pd.DataFrame(grouped_df.file_name.size().index, 
                                 columns = ['file_names'], 
                                 index=start_timestamps)
    all_stats_df = avg_max_std_end_df.join(file_names_df)
    all_stats_df.to_excel(path + 'wave_h_groupby_' + str(sigma) + '.xlsx')
    all_stats_df.save(path + 'stats_groupby_df_' + str(sigma))
    print "sigma ", str(sigma)
    print all_stats_df.describe()
    print np.mean([all_stats_df.heave_file_std_over_h_avg.mean(),
                   all_stats_df.heave_file_std_over_h_std.mean(),
                   all_stats_df.heave_file_std_over_h_rms.mean()])
    
def iterate_over_buoys(buoys):
    for buoy_name in buoys:
        buoy_path = buoys_root_path + buoy_name
        years = os.listdir(buoy_path)
        large_dataframe = pd.DataFrame()
        for year in years:
            year_path = os.path.join(buoy_path, year)
            if os.path.isdir(year_path):
                    months = os.listdir(year_path)
                    for month in months:
                        month_path = os.path.join(year_path,month)
                        if os.path.isdir(month_path):
                            print month_path
                            os.chdir(month_path)
                            wave_height_df = pd.load('wave_height_dataframe')
                            large_dataframe = pd.concat([large_dataframe, 
                                                         wave_height_df])
        large_dataframe.save('large_wave_height_df')
        stats_dict = get_stats_from_df_groupby(large_dataframe, "wave_height_cm", buoys_root_path)
            
iterate_over_buoys(buoys)
    