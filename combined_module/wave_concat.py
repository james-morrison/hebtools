import os
import pandas as pd
import numpy as np
import time
from datetime import datetime

buoys = ['Roag_Wavegen','Bragar_HebMarine2','Siadar_HebMarine1']
buoys_root_path = 'D:\\Datawell\\'
set_size = 'half_hour'
for buoy_name in buoys:
    buoy_path = buoys_root_path + buoy_name
    years = os.listdir(buoy_path)
    large_dataframe = pd.DataFrame()
    for year in years:
        year_path = os.path.join(buoy_path, year)
        months = os.listdir(year_path)
        for month in months:
            month_path = os.path.join(year_path,month)
            print month_path
            os.chdir(month_path)
            wave_height_df = pd.load('wave_height_dataframe')
            large_dataframe = pd.concat([large_dataframe, wave_height_df])
    large_dataframe.save('large_wave_height_df')
    large_dataframe = large_dataframe.sort()
    #index = np.arange(set_size,len(large_dataframe),set_size)
    start_times = []
    end_times = []
    h_max = []
    h_1_3_mean = []
    time_set = 1800
    timestamp = large_dataframe.ix[0].name
    last_timestamp = large_dataframe.ix[-1].name
    first_unix_timestamp = time.mktime(timestamp.timetuple())
    first_nearest_halfhour = round(first_unix_timestamp/time_set)*1800
    last_unix_timestamp = time.mktime(last_timestamp.timetuple())
    last_nearest_halfhour = round(last_unix_timestamp/time_set)*1800
    index = np.arange(first_nearest_halfhour,last_nearest_halfhour,time_set)
    print index
    for x in index:
        #subset = large_dataframe.ix[x-set_size:x]
        subset = large_dataframe.ix[datetime.utcfromtimestamp(x-time_set):datetime.utcfromtimestamp(x)]
        if len(subset) != 0:
            start_times.append(subset.index[0])
            end_times.append(subset.index[-1])
            h_1_3_mean.append(subset.wave_height_cm.order()[-(len(subset)/3):].mean())
            h_max.append(subset.max()[0])
    index_df = pd.DatetimeIndex(start_times)
    print index_df
    end_df = pd.DataFrame(end_times, index=index_df, columns=['end_times'])
    h_1_3_mean_df = pd.DataFrame(h_1_3_mean, index=index_df, 
                                 columns=['h_1_3_mean'])
    h_max_df = pd.DataFrame(h_max, index=index_df, columns=['h_max'])
    set_df = h_max_df.join([h_1_3_mean_df,end_df])
    set_df.save(buoys_root_path + 'wave_h_' + str(set_size) + 
                'set_' + buoy_name)
    set_df.to_excel(buoys_root_path + 'wave_h_' + str(set_size) + 'set_' + 
                    buoy_name + '.xlsx')
    