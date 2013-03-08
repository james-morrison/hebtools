# -*- coding: utf-8 -*-
"""
author: James Morrison
"""
import unittest
import os
import numpy as np
import pandas as pd
from hebtools.dwr import parse_raw
from hebtools.dwr import problem_file_concat
from hebtools.dwr import wave_concat
print os.getcwd()

number_of_waves = 313053
test_folder_path = '../../buoy_data'
    
# class TestParseRaw(unittest.TestCase):

   # def setUp(self):
       # try:        
           # folder_path = '../../buoy_data'
           # parse_raw.load(folder_path)
       # except WindowsError:
           # print "Load Raw Files failed"

   # def test_wave_height_dataframe(self):
       # wave_height_dataframe = pd.load('wave_height_dataframe')
       # self.assertEqual(len(wave_height_dataframe),number_of_waves)

# class TestWaveStats(unittest.TestCase):

    # def setUp(self):
        # #Test

    # def test_wave_height_dataframe(self):
        # os.chdir(os.path.join('buoy_data','2005','july'))
        # raw_plus_std = pd.load('raw_plus_std')
        # wave_stats.Wave_Stats(raw_plus_std)
        # wave_height_dataframe = pd.load('wave_height_dataframe')
        # self.assertEqual(len(wave_height_dataframe),number_of_waves)
        
# class TestProblemFileConcat(unittest.TestCase):

   # def setUp(self):
       # try:        
           # problem_file_concat.iterate_over_buoy(test_folder_path)
       # except WindowsError:
           # print "ProblemFileConcat failed"

   # def test_problem_file_concat(self):
       # os.chdir(test_folder_path)
       # prob_files = np.load('prob_files.npy')
       # self.assertEqual(len(prob_files),0)  

class TestWaveConcat(unittest.TestCase):

    def setUp(self):
        wave_concat.iterate_over_buoy_years('../../buoy_data')

    def test_wave_concat(self):
        wave_height_stats_df = pd.load('large_wave_height_df')
        self.assertEqual(len(wave_height_stats_df),number_of_waves)       
        

if __name__=='__main__':
    unittest.main()    
        