import os
import sys
import numpy as np
import logging
logging.basicConfig(stream=sys.stderr, level=logging.INFO)

def concat(buoy_path):
    logging.info("concat")
    os.chdir(buoy_path)
    years = os.listdir('.')
    years = [dir for dir in years if os.path.isdir(dir)]
    large_np_array = np.array([])
    logging.info("start loop")
    #pdb.set_trace()    
    for year in years:
        logging.info(year)
        os.chdir(year)
        months = os.listdir('.')
        for month in months:
            logging.info(month)
            os.chdir(month)
            prob_files_np = np.load('prob_files.npy')
            logging.info("prob_files_np_loaded")
            large_np_array = np.concatenate([large_np_array, prob_files_np])
            os.chdir('..')
        os.chdir('..')
    logging.info("finish loop")
    np.save('prob_files', large_np_array)
    np.savetxt('problem_files.csv', large_np_array, fmt='%s')
    logging.info("finish concat")

if __name__ == "__main__":
    if len(sys.argv) != 1:
        concat(sys.argv[1])
    else:
        print("No buoy directory supplied")
