import numpy as np
import os

def iterate_over_buoys(buoys):
    for buoy_name in buoys:
        buoy_path = buoys_root_path + buoy_name
        years = os.listdir(buoy_path)
        large_np_array = np.array([])
        for year in years:
            year_path = os.path.join(buoy_path, year)
            months = os.listdir(year_path)
            for month in months:
                month_path = os.path.join(year_path,month)
                print month_path
                os.chdir(month_path)
                prob_files_np = np.load('prob_files.npy')
                large_np_array = np.concatenate([large_np_array, prob_files_np])
        np.save(buoys_root_path + '\\' + buoy_name + '_prob_files', large_np_array)
        np.savetxt(buoys_root_path + '\\' + buoy_name + "_problem_files.csv", large_np_array, fmt='%s')

if __name__ == "__main__":
    buoys = ['Roag_Wavegen','Bragar_HebMarine2','Siadar_HebMarine1']
    buoys_root_path = 'D:\\Datawell\\'     
    iterate_over_buoys(buoys)    
