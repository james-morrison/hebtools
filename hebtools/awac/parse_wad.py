""" Module for reading Nortek wad file with varying white space gaps ( fixed 
length record ) converts the wad data into pandas DataFrame and creates wave 
heights DataFrame using hebtools.common classes  

@author: James Morrison
@license: MIT
"""

import os
import sys
import numpy as np
import pandas as pd
from datetime import datetime 
from hebtools.common import extrema
from hebtools.common import wave_stats

def iter_loadtxt(filename, delimiter='', skiprows=0, dtype=float):
    """ This function is adapted from Joe Kington's example on Stack Overflow
    http://stackoverflow.com/q/8956832/ """
    def iter_func():
        with open(filename, 'r') as infile:
            for _ in range(skiprows):
                next(infile)
            for line in infile:
                line = line.rstrip().split()
                for item in line:
                    yield dtype(item)
        iter_loadtxt.rowlength = len(line)

    data = np.fromiter(iter_func(), dtype=dtype)
    data = data.reshape((-1, iter_loadtxt.rowlength))
    return data


class ParseWad:
    
    def __init__(self, wad_file_path):
        print os.getcwd()
        wad_file_path = os.path.normpath(wad_file_path)
        if os.path.sep in wad_file_path:
            path = os.path.sep.join(wad_file_path.split(os.path.sep)[:-1])
            wad_file_path = wad_file_path.split(os.path.sep)[-1:][0]
        else:
            path = '.'    
        os.chdir(path)
        self.parse_wad(wad_file_path)
        

        
    def parse_wad(self, wad_file_path):
        wad_df = pd.DataFrame(iter_loadtxt(wad_file_path))
        columns = ['month', 'day', 'year', 'hour', 'minute', 'seconds', 
                   'pressure', 'ast_distance1_beam4', 'ast_distance2_beam4', 
                   'ast_quality_beam4', 'analog_input', 
                   'velocity_beam1_x_east_m_s', 'velocity_beam2_y_north_m_s', 
                   'velocity_beam3_x_up_m_s', 'amplitude_beam1', 
                   'amplitude_beam2', 'amplitude_beam3']
        wad_df.columns = columns
        def fmt(x): 
            return str(int(x))
        def join_date_time(x):
            return ' '.join([fmt(x['year']), fmt(x['month']), fmt(x['day']),
                   fmt(x['hour']), fmt(x['minute']), fmt(x['seconds'])])
        date_times = wad_df.apply(lambda x: datetime.strptime(join_date_time(x)
                                  , "%Y %m %d %H %M %S"),axis=1)
        wad_df.index = pd.DatetimeIndex( date_times.values )
        wad_df = wad_df.drop(['minute', 'hour', 'seconds', 'year', 'month', 
                              'day'], axis=1)
        wad_df.save(wad_file_path.replace('.','_') + '_df')
        self.pressure_to_wave_height(wad_df)
    
    def pressure_to_wave_height(self, wad_df):
        extrema_df = extrema.GetExtrema(wad_df, 'pressure')
        wave_stats.WaveStats(extrema_df.raw_disp_with_extrema, 'pressure', 
                             error_check=False, 
                             series_name = 'wave_height_decibar', 
                             df_file_name = 'awac_wave_height_df')
    
def join_wad(wad_dict):            

    def join_df(wad_dict):
        wad_list = []
        for wad_name, wad_df in wad_dict.iteritems():
            wad_list.append(rename_and_resample(wad_df, wad_name))
        combined_wave_stat = wad_list[0].join(wad_list[1:])
        combined_wave_stat.save('combined_awacs_resampled_hour')   
        
    def rename_and_resample(wave_stat_df, name):
        wave_stat_df = wave_stat_df.resample('1H')
        wave_stat_df.columns = [name + '_' + x for x in wave_stat_df.columns]
        return wave_stat_df    
    
    join_df(wad_dict)

if __name__ == "__main__":
    if len(sys.argv) == 1:        
        print "No path to wad file supplied"
    else:
        ParseWad(sys.argv[1])

