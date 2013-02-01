import pandas as pd
from datetime import datetime 
import extrema
import wave_stats
import os

#Read Nortek wad file with varying white space gaps ( fixed length record )

def wad_to_dataframe(wad_file_path):
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

def pressure_to_wave_height(wad_df):
    extrema_df = extrema.Get_Extrema(wad_df, 'pressure')
    os.chdir('D:\\awac_time_series\\')
    wave_stats.Wave_Stats(extrema_df.raw_disp_with_extrema, 'pressure', error_check=False, series_name = 'wave_height_decibar', df_file_name = 'aquamarine_awac_wave_height')

def join_df(wave_stat_df_1, name_1, wave_stat_df_2, name_2):
    wave_stat_df_1 = rename_and_resample(wave_stat_df_1)
    wave_stat_df_2 = rename_and_resample(wave_stat_df_1)
    combined_wave_stat = wave_stat_df_1.join(wave_stat_df_2)
    combined_wave_stat.save('combined_awacs_resampled_hour')

def rename_and_resample(wave_stat_df, name):
    wave_stat_df = wave_stat_df.resample('1H')
    for x in wave_stat_df_1.columns:
        new_cols.append('name_1' + '_' + x)
    wave_stat_df.columns = new_cols
    return wave_stat_df    
    
#wad_df = pd.load('D:\\AquaMarine_AWAC_Recovery_1\\aquamarine_awac_recovery_1\\shortened_wad_df')
wad_file_path = 'D:\\AWAC_time_series\\MERGE - 601sec.wad'
wad_to_dataframe(wad_file_path)
pressure_to_wave_height(wad_df)
