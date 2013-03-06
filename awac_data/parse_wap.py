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

wap_file_path = 'D:\\your_path_here.wap'

output_wap_filename = 'ouput_filename'
 
wap_file = pd.io.parsers.read_csv(wap_file_path, delimiter=r'\s*', names=wap_columns )

timestamps = wap_file.Day.map(str) + ',' + wap_file.Month.map(str) + ','\
            + wap_file.Year.map(str) + 'T' + wap_file.Hour.map(str) + ':'\ 
                        + wap_file.Minute.map(str) + ':' + wap_file.Second.map(str)
                        
date_times = []

for x in timestamps:
    date_times.append(datetime.strptime(x,'%d,%m,%YT%H:%M:%S'))
        
date_times_index = pd.DatetimeIndex(date_times)

wap_file.index = date_times_index

wap_file.save(output_wap_filename)

wap_file.to_excel(output_wap_filename + '.xlsx')