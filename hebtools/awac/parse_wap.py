# -*- coding: utf-8 -*-
"""
Given a Nortek wave parameters or wap file ( Columns can vary depending on 
version see the accompanying wave header or whr file for columns headings )
data is imported into a Pandas DataFrame and timestamp information is extracted
and applied as an index then DataFrame is save and an Excel xlsx version 
( openpyxl module required for Excel export ) 

@author: James Morrison
@license: MIT
"""
import os 
import pandas as pd
from datetime import datetime

wap_columns = ['Month', 'Day', 'Year', 'Hour', 'Minute', 'Second', 'Spectrum type', 
 'Significant height (Hm0)', 'Mean 1/3 height (H3)', 'Mean 1/10 height (H10)',
 'Maximum height (Hmax)', 'Mean Height (Hmean)', 'Mean  period (Tm02)', 
 'Peak period (Tp)', 'Mean zerocrossing period (Tz)', 'Mean 1/3 Period (T3)',
 'Mean 1/10 Period (T10)', 'Maximum Period (Tmax)', 'Peak direction (DirTp)',
 'Directional spread (SprTp)', 'Mean direction (Mdir)', 'Unidirectivity index',
 'Mean Pressure (dbar)', 'Mean AST distance (m)', 'Mean AST distance (Ice)(m)',
 'No Detects', 'Bad Detects', 'Number of Zero-Crossings', 
 'Current speed (wave cell)(m/s)','Current direction (wave cell)', 'Error Code']
 
df_columns = ['month', 'day', 'year', 'hour', 'minute', 'second', 
              'spectrum_type', 'significant_height_Hm0',
              'mean_1_3_height_H3', 'mean_1_10_height_H10', 
              'Maximum height_Hmax', 'mean_height_Hmean', 'mean_period_Tm02', 
              'peak_period_Tp', 'mean_zerocrossing_period_Tz', 
              'mean_1_3_period_T3', 'mean_1_10_period_T10', 
              'maximum_period_Tmax', 'peak_direction_DirTp', 
              'directional_spread_SprTp', 'mean_direction_mdir', 
              'unidirectivity index', 'mean_pressure_dbar', 
              'mean_ast_distance_m', 'mean_ast_distance_ice_m', 'no_detects', 
              'bad_detects', 'num_zero_cross', 'current_speed_wave_cell',
              'current_direction_wave_cell', 'error_code']
              
def load(path, name=""):
    """ path to wap file as parameter, wap data is loaded into pandas DataFrame,
    time and date columns processed into DatetimeIndex, resulting DataFrame
    Excel exported version is saved to disk in directory of wap file.
    """
    path = os.path.normpath(path)
    if os.path.sep in path:
        os.chdir(os.path.sep.join(path.split(os.path.sep)[:-1]))
        file_name = path.split(os.path.sep)[-1]
    else:
        file_name = path
    
    wap_file = pd.io.parsers.read_csv(file_name, 
                                      delimiter=r'\s*', names=df_columns)    
    timestamps = wap_file.day.map(str) + ',' + wap_file.month.map(str) + ','\
                 + wap_file.year.map(str) + 'T' + wap_file.hour.map(str) + ':'\
                 + wap_file.minute.map(str) + ':' + wap_file.second.map(str)
    date_times = []

    for x in timestamps:
        date_times.append(datetime.strptime(x,'%d,%m,%YT%H:%M:%S'))
        
    date_times_index = pd.DatetimeIndex(date_times)
    wap_file.index = date_times_index
    wap_file = wap_file[wap_file.error_code==0]
    if name != '':
        wap_file.columns = [name + '_' + x for x in wap_file.columns]
    file_name = file_name[:-4]
    wap_file.save(file_name + '_wap_df')
    wap_file.to_excel(file_name + '_wap' + '.xlsx')
    
