from datetime import datetime
from hebtools.common import wave_power
import glob
import numpy as np
import os
import pandas as pd

his_columns = ['date_time', 'tp', 'dirp', 'sprp', 'tz', 'hm0', 'ti', 't1', 'tc',
           'tdw2', 'tdw1', 'tpc', 'nu','eps','qp','ss','tref','tsea','bat']
           
hiw_columns = ['date_time','% no reception errors','hmax','tmax','h(1/10)',
               't(1/10)','h1/3','t1/3','Hav','Tav','Eps','#Waves']

matching_string_buoy_his = '*$*.his'
matching_string_computed_his = '*[!$]}*.his'
matching_string_hiw = '*.hiw'
file_types = [matching_string_computed_his, matching_string_hiw]

def get_historical_dataframe(buoy_path, matching_string):
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
                date_times = []
                for date_time_string in df['date_time'].values:
                    if date_time_string != 'nan':
                        date_time = datetime.strptime(date_time_string[:-5],
                                                      "%Y-%m-%dT%H:%M:%S")
                        date_times.append(date_time)
                    else:
                        date_times.append(datetime(1970,1,1))
                df.index = pd.DatetimeIndex(date_times)
                if matching_string[-1] == 's':
                    wavelen = lambda x: wave_power.get_wavelength(x['tp'])
                    wav_pow = lambda x: wave_power.calculate(x['hm0']/100,
                                                             x['tp'])
                    df['wavelength'] = df.apply(wavelen, axis=1) 
                    df['wave_power'] = df.apply(wav_pow, axis=1)
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
        return thirty_min_resample


def load(buoy_path):
    historical_dfs = []
    for file_type in file_types:
        historical_dfs.append(get_historical_dataframe(buoy_path, file_type))
    his_hiw_df = pd.concat(historical_dfs)
    his_hiw_df.save(os.path.join(buoy_path,'his_hiw_df'))

