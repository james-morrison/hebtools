import os
import sys
import numpy as np

def concat(buoy_path):
    os.chdir(buoy_path)
    years = os.listdir('.')
    years = [dir for dir in years if os.path.isdir(dir)]
    large_np_array = np.array([])
    for year in years:
        os.chdir(year)
        months = os.listdir('.')
        for month in months:
            os.chdir(month)
            prob_files_np = np.load('prob_files.npy')
            large_np_array = np.concatenate([large_np_array, prob_files_np])
            os.chdir('..')
        os.chdir('..')
    np.save('prob_files', large_np_array)
    np.savetxt('problem_files.csv', large_np_array, fmt='%s')

if __name__ == "__main__":
    if len(sys.argv) != 1:
        concat(sys.argv[1])
    else:
        print "No buoy directory supplied"
