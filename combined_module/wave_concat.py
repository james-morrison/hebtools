import os
import pandas as pd
import numpy as np

buoy_name = 'Roag_Wavegen'
buoys_root_path = 'D:\\Datawell\\'
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
index = np.arange(50,len(large_dataframe),50)
start_times = []
end_times = []
h_max = []
h_1_3_mean = []
for x in index:
    subset = large_dataframe.ix[x-50:x]
    start_times.append(subset.index[0])
    end_times.append(subset.index[-1])
    h_1_3_mean.append(subset.wave_height_cm.order()[-17:].mean())
    h_max.append(subset.max()[0])
index_df = pd.DatetimeIndex(start_times)
end_df = pd.DataFrame(end_times, index=index_df, columns=['end_times'])
h_1_3_mean_df = pd.DataFrame(h_1_3_mean, index=index_df, columns=['h_1_3_mean'])
h_max_df = pd.DataFrame(h_max, index=index_df, columns=['h_max'])
fifty_set_df = h_max_df.join([h_1_3_mean_df,end_df])
fifty_set_df.save('wave_h_50set_roag')
fifty_set_df.to_excel('wave_h_50set_roag.xlsx')