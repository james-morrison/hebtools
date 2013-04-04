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
from hebtools.dwr import parse_historical
from hebtools.common import wave_stats

number_of_waves = 10599
test_data = os.path.abspath(os.path.join('data','waverider')) + os.path.sep
year = '2005'
month = 'July'
historical_records = 48
    
class TestParseRaw(unittest.TestCase):

   def setUp(self):
       try:        
           parse_raw.load(test_data, year)
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
        os.chdir(os.path.join(test_data, year, month))
        raw_plus_std = pd.load('raw_plus_std')
        wave_stats.WaveStats(raw_plus_std)
        wave_height_dataframe = pd.load('wave_height_dataframe')
        self.assertEqual(len(wave_height_dataframe),number_of_waves)
        
class TestProblemFiles(unittest.TestCase):

   def setUp(self):
       try:        
           problem_files.concat(test_data)
       except WindowsError:
           print "ProblemFileConcat failed"

   def test_problem_file_concat(self):
       os.chdir(test_data)
       prob_files = np.load('prob_files.npy')
       self.assertEqual(len(prob_files),0)  

class TestWaveConcat(unittest.TestCase):

    def setUp(self):
        wave_concat.iterate_over_buoy_years(test_data)

    def test_wave_concat(self):
        wave_height_stats_df = pd.load('large_wave_height_df')
        self.assertEqual(len(wave_height_stats_df),number_of_waves)       
        
class TestParseHistorical(unittest.TestCase):

    def setUp(self):
        print test_data
        parse_historical.load(test_data)

    def test_parse_historical(self):
        his_df = pd.load(os.path.join(test_data, '_his_dataframe'))
        self.assertEqual(len(his_df),historical_records)       
 
        hiw_df = pd.load(os.path.join(test_data, '_hiw_dataframe'))
        self.assertEqual(len(hiw_df),historical_records)       

if __name__=='__main__':
    unittest.main()    
        
