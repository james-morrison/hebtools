import pandas as pd
from datetime import datetime 
import extrema
import wave_stats

#Read Nortek wad file with varying white space gaps ( fixed length record )
wad_file_path = 'D:\\wad_file.wad'
wad_df = pd.read_csv(wad_file_path, delimiter = r'\s*')
columns = ['month', 'day', 'year', 'hour', 'minute', 'seconds', 'pressure',
           'ast_distance1_beam4', 'ast_distance2_beam4', 'ast_quality_beam4',
           'analog_input', 'velocity_beam1_x_east_m_s', 
           'velocity_beam2_y_north_m_s', 'velocity_beam3_x_up_m_s', 
           'amplitude_beam1', 'amplitude_beam2', 'amplitude_beam3']
wad_df.columns = columns
date_times = wad_df.apply(lambda x: datetime.strptime(str(int(x['year'])) + ' '
                          + str(int(x['month'])) + ' ' + str(int(x['day'])) + 
                          ' ' + str(int(x['hour'])) + ' ' + 
                          str(int(x['minute'])) + ' ' + str(int(x['seconds'])),
                          "%Y %m %d %H %M %S"),axis=1)
wad_df.index = pd.DatetimeIndex( date_times.values )
wad_df = wad_df.drop(['minute', 'hour', 'seconds', 'year', 'month', 'day'], axis=1)
wad_df.save(wad_file_path.replace('.','_') + '_df')
extrema_df = extrema.Get_Extrema(wad_df, 'pressure')
print extrema_df
wave_stats.Wave_Stats(extrema_df.raw_disp_with_extrema, 'pressure', error_check=False)

