import os
import glob
import numpy as np
import pandas as pd
from datetime import datetime

his_columns = ['date_time', 'Tp', 'dirp', 'sprp', 'Tz', 'Hm0', 'TI', 'T1', 'Tc', 
           'Tdw2', 'Tdw1', 'Tpc', 'nu','eps','QP','Ss','TRef','TSea','Bat']
           
hiw_columns = ['date_time','% no reception errors','Hmax','Tmax','H(1/10)',
               'T(1/10)','H1/3','T1/3','Hav','Tav','Eps','#Waves']

matching_string_buoy_his = '*$*.his'
matching_string_computed_his = '*[!$]}*.his'
matching_string_hiw = '*.hiw'
file_types = [matching_string_computed_his, matching_string_hiw]

def get_buoy_dataframe(buoy_path, matching_string):
    print "buoy_path", buoy_path
    years = os.listdir(buoy_path)
    df_list = []
    years = [x for x in years if os.path.isdir(os.path.join(buoy_path,x))]
    print "years", years
    for year in years:
        year_path = os.path.join(buoy_path, year)
        months = os.listdir(year_path)
        for month in months:
            month_path = os.path.join(year_path,month)
            print month_path
            os.chdir(month_path)
            try:
                file_name = glob.glob(matching_string)[0]
                print file_name
                if matching_string[-1] == 'w':
                    columns = hiw_columns
                else:
                    columns = his_columns
                df = pd.io.parsers.read_csv(file_name, names = columns)
                date_time_array = []
                for date_time_string in df['date_time'].values:
                    if date_time_string == 'nan':
                        date_time_array.append(datetime.strptime(date_time_string[:-5],
                                                                 "%Y-%m-%dT%H:%M:%S"))
                    else:
                        date_time_array.append(datetime(1970,1,1))
                df.index = pd.DatetimeIndex(date_time_array)
                df_list.append(df)
            except IndexError:
                print "No file found matching", matching_string
    if len(df_list) != 0:
        large_df = pd.concat(df_list)
        large_df = large_df.sort_index()       
        large_df.save(buoy_path + '_' + matching_string[-3:] + '_dataframe')
        thirty_min_resample = large_df.resample('30Min')
        thirty_min_resample.to_excel(buoy_path + '_30_minute_' + \
                                     matching_string[-3:] + '.xlsx' )


def load(buoy_path):
    for file_type in file_types:
        get_buoy_dataframe(buoy_path, file_type)
        

