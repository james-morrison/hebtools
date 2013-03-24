# -*- coding: utf-8 -*-
"""
author: James Morrison
"""
import unittest
import os
import numpy as np
import pandas as pd
from hebtools.dwr import parse_raw
from hebtools.dwr import problem_files
from hebtools.dwr import wave_concat
from hebtools.common import wave_stats
print os.getcwd()

number_of_waves = 10599
test_folder_path = os.path.abspath('data/waverider/') + os.path.sep
year = '2005'
month = 'July'
    
class TestParseRaw(unittest.TestCase):

   def setUp(self):
       try:        
           parse_raw.load(test_folder_path, year)
       except WindowsError:
           print "Load Raw Files failed"

   def test_wave_height_dataframe(self):
       print os.getcwd()
       wave_height_dataframe = pd.load('wave_height_dataframe')
       self.assertEqual(len(wave_height_dataframe),number_of_waves)

class TestWaveStats(unittest.TestCase):

    def setUp(self):
        print "Test"

    def test_wave_height_dataframe(self):
        os.chdir(os.path.join(test_folder_path, year, month))
        raw_plus_std = pd.load('raw_plus_std')
        wave_stats.WaveStats(raw_plus_std)
        wave_height_dataframe = pd.load('wave_height_dataframe')
        self.assertEqual(len(wave_height_dataframe),number_of_waves)
        
class TestProblemFiles(unittest.TestCase):

   def setUp(self):
       try:        
           problem_files.concat(test_folder_path)
       except WindowsError:
           print "ProblemFileConcat failed"

   def test_problem_file_concat(self):
       os.chdir(test_folder_path)
       prob_files = np.load('prob_files.npy')
       self.assertEqual(len(prob_files),0)  

class TestWaveConcat(unittest.TestCase):

    def setUp(self):
        wave_concat.iterate_over_buoy_years(test_folder_path)

    def test_wave_concat(self):
        wave_height_stats_df = pd.load('large_wave_height_df')
        self.assertEqual(len(wave_height_stats_df),number_of_waves)       
        

if __name__=='__main__':
    unittest.main()    
        