import os
import sys
import numpy as np

def iterate_over_buoy(buoy_path):
    print "iterate_over_buoy"
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
    np.save(buoy_path + os.path.sep + 'prob_files', large_np_array)
    np.savetxt(buoy_path + os.path.sep + 'problem_files.csv', large_np_array, fmt='%s')

if __name__ == "__main__":
    if len(sys.argv) != 1:
        iterate_over_buoy(sys.argv[1])
    else:
        print "No buoy directory supplied"
